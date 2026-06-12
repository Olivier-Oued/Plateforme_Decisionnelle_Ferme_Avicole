# ══════════════════════════════════════
# TOUTES LES REQUÊTES SQL DU DASHBOARD
# ══════════════════════════════════════

# ── ACCUEIL ──────────────────────────
Q_KPI_GLOBAL = """
SELECT
    SUM(CASE WHEN type_transaction = 'Revenu'
             AND statut_validation = 'Validé'
        THEN montant ELSE 0 END)                AS total_revenus,
    SUM(CASE WHEN type_transaction = 'Dépense'
             AND statut_validation = 'Validé'
        THEN montant ELSE 0 END)                AS total_depenses,
    SUM(CASE WHEN type_transaction = 'Revenu'
             AND statut_validation = 'Validé'
        THEN montant
        WHEN type_transaction = 'Dépense'
             AND statut_validation = 'Validé'
        THEN -montant ELSE 0 END)               AS solde_operationnel,
    SUM(CASE WHEN type_transaction = 'Apport/Dette'
        THEN montant ELSE 0 END)                AS total_apport_dette
FROM analytique.fait_finance
WHERE supprime_oltp = FALSE;
"""

Q_KPI_VENTES = """
SELECT
    SUM(montant)                                AS ca_total,
    SUM(montant_paye)                           AS total_encaisse,
    SUM(reste_a_payer)                          AS total_creances,
    ROUND((SUM(montant_paye)
        / NULLIF(SUM(montant),0)*100)
        ::numeric, 2)                           AS taux_recouvrement,
    COUNT(*)                                    AS nb_commandes,
    COUNT(DISTINCT client_id)                   AS nb_clients
FROM analytique.fait_ventes;
"""

Q_KPI_PRODUCTION = """
SELECT
    COUNT(*)                                    AS total_cycles,
    ROUND(AVG(taux_eclosion)::numeric,2)        AS taux_eclosion_moyen,
    SUM(poussins_commercialisables)             AS total_poussins,
    ROUND(AVG(taux_perte)::numeric,2)           AS taux_perte_moyen
FROM analytique.fait_production;
"""

Q_KPI_STOCK = """
SELECT
    SUM(poussins_vendus)                        AS total_vendus,
    SUM(quantite_restante)                      AS total_restants,
    ROUND(AVG(taux_ecoulement)::numeric,2)      AS taux_ecoulement_moyen
FROM analytique.fait_stock;
"""

# ── VENTES ───────────────────────────
Q_CA_PAR_PRODUIT = """
SELECT
    produit_normalise,
    COUNT(*)                                    AS nb_commandes,
    SUM(montant)                                AS ca_total,
    ROUND((SUM(montant)/NULLIF(
        (SELECT SUM(montant) FROM analytique.fait_ventes),
        0)*100)::numeric,2)                     AS pct_ca
FROM analytique.fait_ventes
GROUP BY produit_normalise
ORDER BY ca_total DESC;
"""

Q_CA_PAR_MOIS = """
SELECT
    dt.annee, dt.mois, dt.mois_nom,
    SUM(fv.montant)                             AS ca_mensuel,
    SUM(fv.montant_paye)                        AS encaisse_mensuel,
    SUM(fv.reste_a_payer)                       AS creances_mensuel
FROM analytique.fait_ventes fv
JOIN analytique.dim_temps dt ON dt.date_id = fv.date_id
GROUP BY dt.annee, dt.mois, dt.mois_nom
ORDER BY dt.annee, dt.mois;
"""

Q_TOP_CLIENTS = """
SELECT
    dc.nom                                      AS client,
    COUNT(*)                                    AS nb_commandes,
    SUM(fv.montant)                             AS ca_total,
    SUM(fv.reste_a_payer)                       AS dette_actuelle,
    ROUND((SUM(fv.montant_paye)
        /NULLIF(SUM(fv.montant),0)*100)
        ::numeric,2)                            AS taux_recouvrement
FROM analytique.fait_ventes fv
JOIN analytique.dim_client dc ON dc.client_id = fv.client_id
GROUP BY dc.nom
ORDER BY ca_total DESC
LIMIT 10;
"""

Q_MOYEN_PAIEMENT = """
SELECT
    moyen_paiement,
    COUNT(*)                                    AS nb,
    SUM(montant)                                AS total
FROM analytique.fait_ventes
GROUP BY moyen_paiement
ORDER BY total DESC;
"""

Q_CLIENTS_DETTES = """
SELECT
    dc.nom                                      AS client,
    SUM(fv.reste_a_payer)                       AS dette,
    MAX(fv.date_commande)                       AS derniere_commande
FROM analytique.fait_ventes fv
JOIN analytique.dim_client dc ON dc.client_id = fv.client_id
WHERE fv.reste_a_payer > 0
GROUP BY dc.nom
ORDER BY dette DESC;
"""

# ── PRODUCTION ───────────────────────
Q_PRODUCTION_CYCLES = """
SELECT
    numero_fichier, date_incubation,
    oeufs_incubes, oeufs_eclos,
    poussins_commercialisables,
    taux_eclosion, taux_perte,
    duree_cycle_jours,
    COALESCE(machine_nom,'Non renseignée') AS machine
FROM analytique.fait_production
ORDER BY taux_eclosion DESC;
"""

Q_MACHINE_VS_SANS = """
SELECT
    CASE WHEN machine_id IS NOT NULL
        THEN 'Avec Machine 1'
        ELSE 'Sans machine' END              AS type_cycle,
    COUNT(*)                                AS nb_cycles,
    ROUND(AVG(taux_eclosion)::numeric,2)    AS taux_eclosion_moyen,
    ROUND(AVG(taux_perte)::numeric,2)       AS taux_perte_moyen,
    SUM(poussins_commercialisables)         AS total_poussins
FROM analytique.fait_production
GROUP BY CASE WHEN machine_id IS NOT NULL
    THEN 'Avec Machine 1' ELSE 'Sans machine' END
ORDER BY taux_eclosion_moyen DESC;
"""

Q_PRODUCTION_MENSUELLE = """
SELECT
    dt.annee, dt.mois, dt.mois_nom,
    COUNT(*)                                AS nb_cycles,
    SUM(fp.oeufs_incubes)                   AS oeufs_incubes,
    SUM(fp.poussins_commercialisables)      AS poussins_produits,
    ROUND(AVG(fp.taux_eclosion)::numeric,2) AS taux_eclosion_moyen
FROM analytique.fait_production fp
JOIN analytique.dim_temps dt ON dt.date_id = fp.date_id
GROUP BY dt.annee, dt.mois, dt.mois_nom
ORDER BY dt.annee, dt.mois;
"""

Q_COUT_PAR_POUSSIN = """
SELECT
    numero_fichier,
    cout_total_oeufs,
    poussins_commercialisables,
    ROUND((cout_total_oeufs
        /NULLIF(poussins_commercialisables,0))
        ::numeric,2)                        AS cout_par_poussin
FROM analytique.fait_production
WHERE cout_total_oeufs > 0
ORDER BY cout_par_poussin ASC;
"""

# ── FINANCE ──────────────────────────
Q_FINANCE_GLOBAL = """
SELECT
    -- Revenus validés uniquement (= App Opera)
    SUM(CASE WHEN type_transaction = 'Revenu'
             AND statut_validation = 'Validé'
        THEN montant ELSE 0 END)            AS total_revenus,

    -- Revenus par statut pour analyse
    SUM(CASE WHEN type_transaction = 'Revenu'
             AND statut_validation = 'En attente'
        THEN montant ELSE 0 END)            AS revenus_attente,
    SUM(CASE WHEN type_transaction = 'Revenu'
             AND statut_validation = 'Rejeté'
        THEN montant ELSE 0 END)            AS revenus_rejetes,

    -- Dépenses validées uniquement
    SUM(CASE WHEN type_transaction = 'Dépense'
             AND statut_validation = 'Validé'
        THEN montant ELSE 0 END)            AS total_depenses,

    -- Apport/Dette
    SUM(CASE WHEN type_transaction = 'Apport/Dette'
        THEN montant ELSE 0 END)            AS total_apport_dette,

    -- Solde réel = revenus validés - dépenses validées
    SUM(CASE WHEN type_transaction = 'Revenu'
                  AND statut_validation = 'Validé'
             THEN montant
             WHEN type_transaction = 'Dépense'
                  AND statut_validation = 'Validé'
             THEN -montant ELSE 0 END)      AS solde_operationnel
FROM analytique.fait_finance
WHERE supprime_oltp = FALSE;
"""

Q_DEPENSES_CATEGORIE = """
SELECT
    categorie_normalisee,
    COUNT(*)                                AS nb,
    SUM(montant)                            AS total,
    ROUND((SUM(montant)/NULLIF(
        (SELECT SUM(montant) FROM analytique.fait_finance
         WHERE type_transaction = 'Dépense'
         AND statut_validation = 'Validé'
         AND supprime_oltp = FALSE),0)*100)
        ::numeric,2)                        AS pct
FROM analytique.fait_finance
WHERE type_transaction = 'Dépense'
AND statut_validation = 'Validé'
AND supprime_oltp = FALSE
GROUP BY categorie_normalisee
ORDER BY total DESC LIMIT 10;
"""

Q_REVENUS_CATEGORIE = """
SELECT
    categorie_normalisee,
    COUNT(*)                                AS nb,
    SUM(montant)                            AS total
FROM analytique.fait_finance
WHERE type_transaction = 'Revenu'
AND statut_validation = 'Validé'
AND supprime_oltp = FALSE
GROUP BY categorie_normalisee
ORDER BY total DESC;
"""

Q_FINANCE_MENSUELLE = """
SELECT
    dt.annee, dt.mois, dt.mois_nom,
    SUM(CASE WHEN ff.type_transaction = 'Revenu'
             AND ff.statut_validation = 'Validé'
        THEN ff.montant ELSE 0 END)         AS revenus,
    SUM(CASE WHEN ff.type_transaction = 'Dépense'
             AND ff.statut_validation = 'Validé'
        THEN ff.montant ELSE 0 END)         AS depenses,
    SUM(CASE WHEN ff.type_transaction = 'Revenu'
                  AND ff.statut_validation = 'Validé'
             THEN ff.montant
             WHEN ff.type_transaction = 'Dépense'
                  AND ff.statut_validation = 'Validé'
             THEN -ff.montant ELSE 0 END)   AS solde
FROM analytique.fait_finance ff
JOIN analytique.dim_temps dt ON dt.date_id = ff.date_id
WHERE ff.type_transaction != 'Apport/Dette'
AND ff.supprime_oltp = FALSE
GROUP BY dt.annee, dt.mois, dt.mois_nom
ORDER BY dt.annee, dt.mois;
"""

# ── FINANCE — TRANSACTIONS SUPPRIMÉES (historique audit) ──
Q_TRANSACTIONS_SUPPRIMEES = """
SELECT
    ff.finance_id,
    ff.type_transaction,
    ff.statut_validation,
    ff.montant,
    ff.date_transaction,
    ff.description,
    ff.categorie_normalisee,
    ff.user_name
FROM analytique.fait_finance ff
WHERE ff.supprime_oltp = TRUE
ORDER BY ff.date_transaction DESC;
"""

# ── STOCKS ───────────────────────────
Q_STOCKS_DETAIL = """
SELECT
    reference_eclosion,
    date_entree_stock,
    statut_stock,
    quantite_initiale,
    poussins_vendus,
    quantite_restante,
    taux_ecoulement,
    (CURRENT_DATE - date_entree_stock)      AS jours_en_stock
FROM analytique.fait_stock
ORDER BY date_entree_stock DESC;
"""

Q_KPI_STOCK = """
SELECT
    SUM(poussins_vendus)                    AS total_vendus,
    SUM(quantite_restante)                  AS total_restants,
    ROUND(AVG(taux_ecoulement)::numeric,2)  AS taux_ecoulement_moyen
FROM analytique.fait_stock;
"""

Q_STOCKS_ALERTES = """
SELECT
    reference_eclosion,
    quantite_restante,
    taux_ecoulement,
    (CURRENT_DATE - date_entree_stock)      AS jours_en_stock,
    CASE
        WHEN taux_ecoulement >= 95
            THEN 'Épuisé'
        WHEN taux_ecoulement < 20
            AND (CURRENT_DATE - date_entree_stock) > 5
            THEN 'Critique'
        WHEN taux_ecoulement < 50
            AND (CURRENT_DATE - date_entree_stock) > 7
            THEN 'Lenteur'
        ELSE 'Normal'
    END                                     AS alerte
FROM analytique.fait_stock
WHERE COALESCE(statut_stock, 'Actif') != 'Terminé'
ORDER BY taux_ecoulement ASC;
"""

Q_RENTABILITE_CYCLES = """
SELECT
    fp.numero_fichier,
    fp.poussins_commercialisables,
    fs.poussins_vendus,
    fs.taux_ecoulement,
    fv_ca.ca_cycle,
    ROUND((fv_ca.ca_cycle
        /NULLIF(fp.cout_total_oeufs,0))
        ::numeric,2)                        AS ratio_ca_cout
FROM analytique.fait_production fp
LEFT JOIN analytique.fait_stock fs
    ON fs.cycle_id = fp.cycle_id
LEFT JOIN (
    SELECT cycle_id, SUM(montant) AS ca_cycle
    FROM analytique.fait_ventes GROUP BY cycle_id
) fv_ca ON fv_ca.cycle_id = fp.cycle_id
WHERE fp.cout_total_oeufs > 0
ORDER BY ratio_ca_cout DESC NULLS LAST;
"""

# ── AUDIT ────────────────────────────
Q_ACTIVITE_PAR_USER = """
SELECT
    user_email,
    user_role,
    COUNT(*)                                AS nb_actions,
    COUNT(DISTINCT DATE(timestamp_action))  AS jours_actif
FROM analytique.fait_activite
GROUP BY user_email, user_role
ORDER BY nb_actions DESC;
"""

Q_ACTIONS_PAR_TYPE = """
SELECT
    action,
    resource,
    COUNT(*)                                AS nb
FROM analytique.fait_activite
GROUP BY action, resource
ORDER BY nb DESC LIMIT 15;
"""

Q_ACTIVITE_PAR_JOUR = """
SELECT
    TO_CHAR(timestamp_action,'Day')         AS jour,
    EXTRACT(ISODOW FROM timestamp_action)   AS num_jour,
    COUNT(*)                                AS nb_actions
FROM analytique.fait_activite
GROUP BY TO_CHAR(timestamp_action,'Day'),
    EXTRACT(ISODOW FROM timestamp_action)
ORDER BY num_jour;
"""

Q_ALERTES_SECURITE = """
SELECT
    user_email,
    action,
    resource,
    details,
    timestamp_action
FROM analytique.fait_activite
WHERE action = 'SECURITY_ALERT'
ORDER BY timestamp_action DESC;
"""

Q_ACTIONS_SUSPECTES = """
SELECT
    user_email,
    action,
    resource,
    details,
    timestamp_action
FROM analytique.fait_activite
WHERE action ILIKE '%delete%'
OR action ILIKE '%reject%'
OR details ILIKE '%supprim%'
ORDER BY timestamp_action DESC
LIMIT 20;
"""

# ── SAAS ─────────────────────────────
Q_FERMES = """
SELECT
    f.id, f.nom,
    f.plan_abonnement,
    f.is_active,
    a.statut                                AS statut_abonnement,
    DATE(a.date_debut)                      AS debut_abonnement,
    DATE(a.date_fin)                        AS fin_abonnement
FROM public.fermes f
LEFT JOIN public.abonnements a ON a.ferme_id = f.id
ORDER BY f.id;
"""

Q_PROFILS = """
SELECT
    f.nom                                   AS ferme,
    p.role,
    COUNT(*)                                AS nb_profils,
    COUNT(CASE WHEN p.is_active=TRUE
        THEN 1 END)                         AS profils_actifs
FROM public.fermes f
LEFT JOIN public.profil p ON p.tenant_id = f.id
GROUP BY f.nom, p.role
ORDER BY f.nom, nb_profils DESC;
"""