from datetime import datetime, timedelta
import os
import logging

from airflow import DAG
from airflow.operators.python import PythonOperator

from sqlalchemy import create_engine, text
import pandas as pd

# ══════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════
MALI_DB_URL = os.environ.get("MALI_DB_URL", "")

logger = logging.getLogger(__name__)

default_args = {
    "owner"           : "olivier_ouedraogo",
    "depends_on_past" : False,
    "email_on_failure": False,
    "email_on_retry"  : False,
    "retries"         : 2,
    "retry_delay"     : timedelta(minutes=5),
}

# ══════════════════════════════════════
# FONCTIONS UTILITAIRES
# ══════════════════════════════════════
def get_engine():
    return create_engine(MALI_DB_URL)

def log_result(table, nb_rows):
    logger.info(f"✅ {table} rechargée — {nb_rows} lignes")

# ══════════════════════════════════════
# TASK 1 — TEST CONNEXION
# ══════════════════════════════════════
def test_connexion():
    logger.info("🔌 Test de connexion PostgreSQL Mali Élevage...")
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(text(
            "SELECT COUNT(*) FROM public.commandes"
        ))
        nb = result.fetchone()[0]
    logger.info(f"✅ Connexion OK — {nb} commandes dans la base")
    return nb

# ══════════════════════════════════════
# TASK 2 — ETL DIMENSIONS
# ══════════════════════════════════════
def etl_dimensions():
    logger.info("📐 Rechargement des dimensions...")
    engine = get_engine()

    sql_temps = """
    INSERT INTO analytique.dim_temps (
        date_id, jour, semaine, mois, mois_nom,
        trimestre, annee, annee_semaine, est_weekend
    )
    SELECT DISTINCT
        DATE(c.date_commande),
        EXTRACT(DOW FROM c.date_commande)::INT,
        EXTRACT(WEEK FROM c.date_commande)::INT,
        EXTRACT(MONTH FROM c.date_commande)::INT,
        TO_CHAR(c.date_commande, 'Month'),
        EXTRACT(QUARTER FROM c.date_commande)::INT,
        EXTRACT(YEAR FROM c.date_commande)::INT,
        EXTRACT(YEAR FROM c.date_commande)::INT * 100
            + EXTRACT(WEEK FROM c.date_commande)::INT,
        CASE WHEN EXTRACT(DOW FROM c.date_commande) IN (0,6)
             THEN TRUE ELSE FALSE END
    FROM public.commandes c
    WHERE c.date_commande IS NOT NULL
    ON CONFLICT (date_id) DO NOTHING;
    """

    sql_client = """
    INSERT INTO analytique.dim_client (
        client_id, nom, telephone, adresse, ferme_id
    )
    SELECT
        id,
        nom,
        telephone,
        COALESCE(adresse, ''),
        tenant_id
    FROM public.clients
    WHERE tenant_id = 1
    ON CONFLICT (client_id) DO UPDATE SET
        nom       = EXCLUDED.nom,
        telephone = EXCLUDED.telephone,
        adresse   = EXCLUDED.adresse;
    """

    with engine.begin() as conn:
        conn.execute(text(sql_temps))
        conn.execute(text(sql_client))

    logger.info("✅ Dimensions rechargées avec succès")

# ══════════════════════════════════════
# TASK 3 — ETL FAIT PRODUCTION
# ══════════════════════════════════════
def etl_fait_production():
    logger.info("🥚 Rechargement fait_production...")
    engine = get_engine()

    sql = """
    INSERT INTO analytique.fait_production (
        cycle_id, numero_fichier, date_incubation,
        oeufs_incubes, oeufs_eclos, poussins_commercialisables,
        taux_eclosion, taux_fertilite, taux_perte,
        duree_cycle_jours, cout_total_oeufs,
        machine_id, machine_nom, ferme_id, date_id
    )
    SELECT
        ic.id,
        ic.numero_fichier,
        DATE(ic.date_incubation),
        ic.oeufs_incubes,
        COALESCE(ir.oeufs_eclos, 0),
        GREATEST(
            COALESCE(ir.oeufs_eclos, 0)
            - COALESCE(ir.deces, 0)
            - COALESCE(ir.handicapes, 0),
        0),
        COALESCE(ir.taux_eclosion, ROUND(
            (COALESCE(ir.oeufs_eclos,0)::float
            / NULLIF(ic.oeufs_incubes,0) * 100)::numeric, 2)),
        ROUND(
            ((ic.oeufs_incubes - COALESCE(ir.oeufs_clairs,0))::float
            / NULLIF(ic.oeufs_incubes,0) * 100)::numeric, 2),
        ROUND(
            ((COALESCE(ir.deces,0) + COALESCE(ir.handicapes,0))::float
            / NULLIF(COALESCE(ir.oeufs_eclos,1),0) * 100)::numeric, 2),
        COALESCE(
            (DATE(ic.date_sortie) - DATE(ic.date_incubation)), 21),
        (ic.nombre_cartons * ic.prix_carton),
        ic.machine_id,
        mi.nom,
        ic.tenant_id,
        DATE(ic.date_incubation)
    FROM public.incubation_cycles ic
    LEFT JOIN public.incubation_results ir ON ir.cycle_id = ic.id
    LEFT JOIN public.machines_incubation mi ON mi.id = ic.machine_id
    WHERE ic.tenant_id = 1
    AND ic.numero_fichier != 'CYCLE-CREDIT'
    AND ic.oeufs_incubes > 0
    ON CONFLICT (cycle_id) DO UPDATE SET
        oeufs_eclos                = EXCLUDED.oeufs_eclos,
        poussins_commercialisables = EXCLUDED.poussins_commercialisables,
        taux_eclosion              = EXCLUDED.taux_eclosion,
        taux_perte                 = EXCLUDED.taux_perte;
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    nb = pd.read_sql(
        text("SELECT COUNT(*) as nb FROM analytique.fait_production"),
        engine
    )["nb"][0]
    log_result("fait_production", nb)

# ══════════════════════════════════════
# TASK 4 — ETL FAIT VENTES — CORRIGÉ
# Ajout Achat d'Oeufs normalisé en Oeufs
# Suppression filtre NOT ILIKE achat oeuf
# ══════════════════════════════════════
def etl_fait_ventes():
    logger.info("🛒 Rechargement fait_ventes...")
    engine = get_engine()

    sql = """
    INSERT INTO analytique.fait_ventes (
        commande_id, date_id, client_id, ferme_id,
        produit_normalise, quantite, prix_unitaire,
        montant, montant_paye, reste_a_payer,
        moyen_paiement, est_credit, cycle_id
    )
    SELECT
        c.id,
        DATE(c.date_commande),
        c.client_id,
        c.tenant_id,
        CASE
            WHEN c.produit ILIKE '%poussin%'      THEN 'Poussins'
            WHEN c.produit ILIKE '%poulet%'        THEN 'Poulet de chair'
            WHEN c.produit ILIKE '%oeuf%turquie%' THEN 'Oeufs Turquie'
            WHEN c.produit ILIKE '%achat%oeuf%'   THEN 'Oeufs'
            WHEN c.produit ILIKE '%oeuf%'          THEN 'Oeufs'
            ELSE c.produit
        END,
        c.quantite,
        ROUND((c.montant / NULLIF(c.quantite,0))::numeric, 2),
        c.montant,
        COALESCE(c.montant_total_paye, 0),
        COALESCE(c.montant - c.montant_total_paye, 0),
        COALESCE(c.moyen_paiement, 'Espèces'),
        CASE WHEN COALESCE(c.montant_total_paye,0) < c.montant
             THEN TRUE ELSE FALSE END,
        c.incubation_cycle_id
    FROM public.commandes c
    WHERE c.tenant_id = 1
    AND c.type_commande = 'Vente'
    AND c.statut_validation != 'Supprimé'
    ON CONFLICT (commande_id) DO UPDATE SET
        montant_paye     = EXCLUDED.montant_paye,
        reste_a_payer    = EXCLUDED.reste_a_payer,
        produit_normalise = EXCLUDED.produit_normalise;
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    nb = pd.read_sql(
        text("SELECT COUNT(*) as nb FROM analytique.fait_ventes"),
        engine
    )["nb"][0]
    log_result("fait_ventes", nb)

# ══════════════════════════════════════
# TASK 5 — ETL FAIT FINANCE
# Ajout synchronisation suppressions OLTP
# ══════════════════════════════════════
def etl_fait_finance():
    logger.info("💰 Rechargement fait_finance...")
    engine = get_engine()

    sql_insert = """
    INSERT INTO analytique.fait_finance (
        finance_id, date_id, ferme_id,
        type_transaction, categorie_normalisee,
        montant, description, user_name, source,
        statut_validation,
        date_transaction, supprime_oltp
    )
    SELECT
        f.id,
        DATE(f.date_transaction),
        f.tenant_id,
        f.type_transaction,
        CASE
            WHEN f.categorie ILIKE '%electricit%' THEN 'Électricité'
            WHEN f.categorie ILIKE '%transport%'   THEN 'Transport'
            WHEN f.categorie ILIKE '%aliment%'     THEN 'Alimentation élevage'
            WHEN f.categorie ILIKE '%salaire%'     THEN 'Salaire'
            WHEN f.categorie ILIKE '%achat%oeuf%'  THEN 'Achat œufs'
            WHEN f.categorie ILIKE '%douane%'      THEN 'Douane'
            WHEN f.categorie ILIKE '%medicament%'  THEN 'Médicaments'
            WHEN f.categorie ILIKE '%agio%'        THEN 'Agio'
            ELSE COALESCE(f.categorie, 'Autre')
        END,
        f.montant,
        f.description,
        f.user_name,
        'Manuel',
        f.statut_validation,
        DATE(f.date_transaction),
        FALSE
    FROM public.finance f
    WHERE f.tenant_id = 1
    ON CONFLICT (finance_id) DO UPDATE SET
        montant              = EXCLUDED.montant,
        categorie_normalisee = EXCLUDED.categorie_normalisee,
        statut_validation    = EXCLUDED.statut_validation,
        supprime_oltp        = FALSE;
    """

    # Synchronisation des suppressions : marque les transactions
    # présentes dans l'analytique mais absentes de l'OLTP
    sql_sync_suppressions = """
    UPDATE analytique.fait_finance af
    SET supprime_oltp = TRUE
    WHERE af.finance_id NOT IN (
        SELECT id FROM public.finance WHERE tenant_id = 1
    )
    AND af.supprime_oltp = FALSE;
    """

    with engine.begin() as conn:
        conn.execute(text(sql_insert))
        result = conn.execute(text(sql_sync_suppressions))
        nb_supprimees = result.rowcount

    if nb_supprimees > 0:
        logger.info(f"👻 {nb_supprimees} transaction(s) marquée(s) comme supprimée(s) de l'OLTP")

    nb = pd.read_sql(
        text("SELECT COUNT(*) as nb FROM analytique.fait_finance"),
        engine
    )["nb"][0]
    log_result("fait_finance", nb)

# ══════════════════════════════════════
# TASK 6 — ETL FAIT STOCK — BUG CORRIGÉ
# Suppression de la double exécution SQL
# ══════════════════════════════════════
def etl_fait_stock():
    logger.info("📦 Rechargement fait_stock...")
    engine = get_engine()

    sql = """
    INSERT INTO analytique.fait_stock (
        cycle_id, reference_eclosion,
        date_entree_stock, ferme_id,
        quantite_initiale, poussins_vendus,
        quantite_restante, taux_ecoulement, statut_stock
    )
    SELECT
        sp.cycle_id,
        ic.numero_fichier,
        DATE(sp.date_entree_stock),
        sp.tenant_id,
        sp.quantite_disponible,
        COALESCE(v.total_vendus, 0),
        sp.quantite_disponible - COALESCE(v.total_vendus, 0),
        ROUND(
            (COALESCE(v.total_vendus,0)::float
            / NULLIF(sp.quantite_disponible,0) * 100)::numeric, 2),
        CASE
            WHEN sp.quantite_disponible - COALESCE(v.total_vendus, 0) = 0
                THEN 'Terminé'
            ELSE 'Actif'
        END
    FROM public.stock_poussins sp
    LEFT JOIN public.incubation_cycles ic ON ic.id = sp.cycle_id
    LEFT JOIN (
        SELECT incubation_cycle_id,
               SUM(quantite) AS total_vendus
        FROM public.commandes
        WHERE statut_validation != 'Supprimé'
        AND type_commande = 'Vente'
        AND produit IN ('Poussins','Poussin d un jour')
        AND incubation_cycle_id IS NOT NULL
        GROUP BY incubation_cycle_id
    ) v ON v.incubation_cycle_id = sp.cycle_id
    WHERE sp.tenant_id = 1
    AND sp.quantite_disponible != 999999
    ON CONFLICT (cycle_id) DO UPDATE SET
        poussins_vendus   = EXCLUDED.poussins_vendus,
        quantite_restante = EXCLUDED.quantite_restante,
        taux_ecoulement   = EXCLUDED.taux_ecoulement,
        statut_stock      = EXCLUDED.statut_stock;
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    nb = pd.read_sql(
        text("SELECT COUNT(*) as nb FROM analytique.fait_stock"),
        engine
    )["nb"][0]
    log_result("fait_stock", nb)

# ══════════════════════════════════════
# TASK 7 — ETL FAIT ACTIVITE
# ══════════════════════════════════════
def etl_fait_activite():
    logger.info("🔍 Rechargement fait_activite...")
    engine = get_engine()

    sql = """
    INSERT INTO analytique.fait_activite (
        log_id, ferme_id, user_email, user_role,
        action, resource, resource_id,
        details, ip_address, timestamp_action
    )
    SELECT
        al.id,
        al.tenant_id,
        al.user_email,
        al.user_role,
        al.action,
        al.resource,
        al.resource_id,
        al.details,
        al.ip_address,
        al.timestamp
    FROM public.activity_logs al
    WHERE al.tenant_id = 1
    ON CONFLICT (log_id) DO NOTHING;
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    nb = pd.read_sql(
        text("SELECT COUNT(*) as nb FROM analytique.fait_activite"),
        engine
    )["nb"][0]
    log_result("fait_activite", nb)

# ══════════════════════════════════════
# TASK 8 — NOTIFICATION SUCCÈS
# ══════════════════════════════════════
def notification_succes(**context):
    engine = get_engine()

    stats = pd.read_sql(text("""
        SELECT
            (SELECT COUNT(*) FROM analytique.fait_ventes)     AS ventes,
            (SELECT COUNT(*) FROM analytique.fait_production) AS production,
            (SELECT COUNT(*) FROM analytique.fait_finance)    AS finance,
            (SELECT COUNT(*) FROM analytique.fait_stock)      AS stock,
            (SELECT COUNT(*) FROM analytique.fait_activite)   AS activite
    """), engine)

    run_date = context["ds"]
    logger.info("=" * 60)
    logger.info(f"✅ ETL MALI ÉLEVAGE — SUCCÈS — {run_date}")
    logger.info("=" * 60)
    logger.info(f"📊 fait_ventes     : {stats['ventes'][0]} lignes")
    logger.info(f"🥚 fait_production : {stats['production'][0]} lignes")
    logger.info(f"💰 fait_finance    : {stats['finance'][0]} lignes")
    logger.info(f"📦 fait_stock      : {stats['stock'][0]} lignes")
    logger.info(f"🔍 fait_activite   : {stats['activite'][0]} lignes")
    logger.info("=" * 60)

# ══════════════════════════════════════
# DÉFINITION DU DAG
# ══════════════════════════════════════
with DAG(
    dag_id="mali_elevage_etl",
    description="Pipeline ETL Mali Élevage — Rechargement schéma analytique",
    default_args=default_args,
    start_date=datetime(2026, 5, 29),
    schedule_interval="0 2 * * *",
    catchup=False,
    tags=["mali_elevage", "etl", "data_engineering"],
) as dag:

    t1 = PythonOperator(
        task_id="test_connexion",
        python_callable=test_connexion,
    )
    t2 = PythonOperator(
        task_id="etl_dimensions",
        python_callable=etl_dimensions,
    )
    t3 = PythonOperator(
        task_id="etl_fait_production",
        python_callable=etl_fait_production,
    )
    t4 = PythonOperator(
        task_id="etl_fait_ventes",
        python_callable=etl_fait_ventes,
    )
    t5 = PythonOperator(
        task_id="etl_fait_finance",
        python_callable=etl_fait_finance,
    )
    t6 = PythonOperator(
        task_id="etl_fait_stock",
        python_callable=etl_fait_stock,
    )
    t7 = PythonOperator(
        task_id="etl_fait_activite",
        python_callable=etl_fait_activite,
    )
    t8 = PythonOperator(
        task_id="notification_succes",
        python_callable=notification_succes,
        provide_context=True,
    )

    # ══ DÉPENDANCES ══
    t1 >> t2 >> [t3, t4, t5, t6, t7] >> t8