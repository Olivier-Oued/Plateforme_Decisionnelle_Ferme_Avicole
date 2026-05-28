# 🐔 Plateforme Décisionnelle Mali Élevage

> Projet réalisé dans le cadre d'un stage Data Engineering  
> chez **OUED Services** (5 rue de Ponthieu 75008 Paris, France) — Mai/Juillet 2026

---

## 📌 Contexte

OUED Services édite une application SaaS de gestion de fermes avicoles
(**Mali Élevage**) utilisée en mode multi-tenant par plusieurs fermes
clientes. Les données opérationnelles existaient dans une base PostgreSQL
(Heroku / Amazon RDS) mais étaient exploitées de manière fragmentée,
sans vision croisée ni indicateurs consolidés.

**Objectif :** Construire une plateforme de données décisionnelle complète
— de l'extraction jusqu'au dashboard interactif.

---

## 🏗️ Architecture

```
PostgreSQL OLTP (Heroku/Amazon RDS)
         ↓  READ ONLY — zéro modification sur la base de production
Schéma analytique (PostgreSQL)
    ├── 8 Tables de faits
    └── 6 Dimensions
         ↓
Dashboard Streamlit (connexion directe PostgreSQL)
```

---

## 📦 Schéma en étoile

### Tables de faits (8)

| Table | Source | Lignes |
|---|---|---|
| `fait_ventes` | commandes + clients | 367 |
| `fait_transferts_internes` | commandes (Interne) | 23 |
| `fait_commandes_archivees` | commandes (Supprimé) | 9 |
| `fait_production` | incubation_cycles + incubation_results | 17 |
| `fait_finance` | finance + finance_allocations | 1 099 |
| `fait_elevage` | lots_volailles + suivi_quotidien_lots | 16 |
| `fait_stock` | stock_poussins + commandes | 17 |
| `fait_activite` | activity_logs | 2 245 |

### Dimensions (6)

| Dimension | Source | Lignes |
|---|---|---|
| `dim_temps` | commandes + finance + incubation | 373 |
| `dim_ferme` | fermes | 1 |
| `dim_client` | clients | 80 |
| `dim_produit` | Créée manuellement | 6 |
| `dim_employe` | employes | 22 |
| `dim_machine` | machines_incubation | 1 |

---

## 📊 KPIs validés — 31 sur 6 domaines

| Domaine | KPIs | Résultats clés |
|---|---|---|
| 🛒 Ventes | 6 | CA : 225M XOF · Recouvrement : 97.53% · 75 clients |
| 🥚 Production | 5 | Taux éclosion : 74.6% · +22pts avec machine |
| 💰 Finance | 5 | Revenus : 246M XOF · Solde opérationnel : +2.5M XOF |
| 📦 Stocks | 5 | 70 271 vendus · 45 679 restants · taux écoulement 63.71% |
| 🔍 Audit | 5 | 2 245 actions · 12 utilisateurs · 17 alertes sécurité |
| ☁️ SaaS | 5 | 2 fermes · 9 profils actifs · adoption 7j/7 |

---

## 🔧 Anomalies détectées et corrigées (12)

| Anomalie | Table source | Correction appliquée |
|---|---|---|
| CYCLE-CREDIT (oeufs_incubes=0) | incubation_cycles | Exclu via filtre ETL |
| LOT-CREDIT (taille=999999) | lots_volailles | Exclu via filtre ETL |
| poussins_vendus = 0 partout | stock_poussins | Recalculé depuis commandes |
| quantite_restante statique | stock_oeufs | Recalculé depuis incubation_cycles |
| Jointure impossible numero_lot | commandes | Jointure via incubation_cycle_id |
| Catégories finance dupliquées | finance | Normalisées via CASE WHEN |
| Produits noms différents | commandes | Normalisés dans dim_produit |
| Achat Oeufs classé en vente | commandes | Isolé dans dim_produit |
| Vente poulets classée en dépense | finance | Signalé — correction manuelle |
| dim_employe doublons x4 | employes + profil | Suppression jointure profil |
| masque_vente filtre trop large | lots_volailles | Filtre ciblé par nom/taille |
| 9 commandes supprimées masquées | commandes | Isolées dans fait_commandes_archivees |

---

## 🚀 Stack technique

```
Base de données  : PostgreSQL (Heroku / Amazon RDS)
Langage          : Python 3.14
ETL              : SQL avancé + pandas + psycopg2 + SQLAlchemy
Dashboard        : Streamlit + Plotly
Gestion projet   : Scrum · Taiga · 7 sprints · 35 US · 109 story points
Versioning       : Git / GitHub
```

---

## 📁 Structure du projet

```
dashboard_mali_elevage/
│
├── app.py                  ← Page d'accueil principale
├── config.py               ← Connexion PostgreSQL (credentials exclus)
├── config.example.py       ← Template de connexion à copier
├── requirements.txt        ← Dépendances Python
│
├── pages/
│   ├── 1_Ventes.py         ← Domaine Ventes (6 KPIs)
│   ├── 2_Production.py     ← Domaine Production (5 KPIs)
│   ├── 3_Finance.py        ← Domaine Finance (5 KPIs)
│   ├── 4_Stocks.py         ← Domaine Stocks (5 KPIs)
│   ├── 5_Audit.py          ← Domaine Audit (5 KPIs)
│   └── 6_SaaS.py           ← Domaine SaaS (5 KPIs)
│
├── utils/
│   └── queries.py          ← Toutes les requêtes SQL analytiques
│
└── assets/
    └── style.css           ← Charte graphique Mali Élevage
```

---

## ⚙️ Installation

```bash
# 1. Cloner le repo
git clone https://github.com/Olivier-Oued/plateforme-decisionnelle-mali-elevage.git
cd plateforme-decisionnelle-mali-elevage

# 2. Installer les dépendances
pip install -r dashboard_mali_elevage/requirements.txt

# 3. Configurer la connexion PostgreSQL
cp dashboard_mali_elevage/config.example.py dashboard_mali_elevage/config.py
# Éditer config.py et renseigner vos credentials DATABASE_URL

# 4. Lancer le dashboard
cd dashboard_mali_elevage
python -m streamlit run app.py
```

---

## 📈 Insights stratégiques découverts

- **Machine 1 → +22pts de taux d'éclosion** soit +1.4M XOF de CA supplémentaire par cycle
- **99% des revenus dépensés** — marge nette de 1.01% à surveiller en priorité
- **17 SECURITY_ALERT** détectées depuis le 02/05/2026 — à investiguer immédiatement
- **SOMAPAV** = client VIP — 13% du CA total à lui seul (4 commandes seulement)
- **97% des paiements en espèces** — risque opérationnel majeur à digitaliser

---

## 👤 Auteur

**OUEDRAOGO Olivier**  
Stagiaire Data Engineer — OUED Services, Le Blanc-Mesnil (93)  
Master 1 Data Engineering — INGETIS Paris  
Stage : Mai — Juillet 2026

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Olivier_Ouedraogo-0077B5?style=flat&logo=linkedin)](https://linkedin.com/in/olivier-ouedraogo)
[![GitHub](https://img.shields.io/badge/GitHub-Olivier--Oued-181717?style=flat&logo=github)](https://github.com/Olivier-Oued)

---

## ⚠️ Confidentialité

Les credentials de connexion PostgreSQL, les données clients et les
transactions financières réelles ne sont pas inclus dans ce repo.  
Copiez `config.example.py` vers `config.py` et renseignez vos propres
credentials pour connecter votre base de données.
