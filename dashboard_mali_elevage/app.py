import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from config import run_query, COLORS, PLOTLY_COLORS
from utils.queries import (
    Q_KPI_GLOBAL, Q_KPI_VENTES,
    Q_KPI_PRODUCTION, Q_KPI_STOCK,
    Q_ALERTES_SECURITE, Q_STOCKS_ALERTES
)

# ══════════════════════════════════════
# CONFIGURATION PAGE
# ══════════════════════════════════════
st.set_page_config(
    page_title="Mali Élevage — Dashboard",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════
# CSS PERSONNALISÉ
# ══════════════════════════════════════
def load_css():
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ══════════════════════════════════════
# AUTHENTIFICATION — LOCAL ou CLOUD
# ══════════════════════════════════════
try:
    _has_secrets = "credentials" in st.secrets
except Exception:
    _has_secrets = False

if _has_secrets:
    # Streamlit Cloud — secrets.toml
    credentials = {
        "usernames": {
            user: dict(data)
            for user, data in st.secrets["credentials"]["usernames"].items()
        }
    }
    cookie_name   = st.secrets["cookie"]["name"]
    cookie_key    = st.secrets["cookie"]["key"]
    cookie_expiry = st.secrets["cookie"]["expiry_days"]
else:
    # Local — config.yaml
    with open("config.yaml", encoding="utf-8") as f:
        config = yaml.load(f, Loader=SafeLoader)
    credentials   = config["credentials"]
    cookie_name   = config["cookie"]["name"]
    cookie_key    = config["cookie"]["key"]
    cookie_expiry = config["cookie"]["expiry_days"]

authenticator = stauth.Authenticate(
    credentials, cookie_name, cookie_key, cookie_expiry
)

authenticator.login(location="main")

if st.session_state["authentication_status"] is False:
    st.markdown("""
        <div style='display:flex;flex-direction:column;align-items:center;
             justify-content:center;min-height:60vh;gap:16px'>
            <div style='font-size:48px'>🐔</div>
            <div style='font-size:22px;font-weight:600;color:#0F3D1E'>
                Mali Élevage
            </div>
            <div style='font-size:14px;color:#666'>Plateforme Décisionnelle</div>
        </div>
    """, unsafe_allow_html=True)
    st.error("❌ Identifiant ou mot de passe incorrect")
    st.stop()
elif st.session_state["authentication_status"] is None:
    st.markdown("""
        <div style='display:flex;flex-direction:column;align-items:center;
             justify-content:center;min-height:60vh;gap:16px'>
            <div style='font-size:48px'>🐔</div>
            <div style='font-size:22px;font-weight:600;color:#0F3D1E'>
                Mali Élevage
            </div>
            <div style='font-size:14px;color:#666'>
                Plateforme Décisionnelle · Veuillez vous connecter
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════
# DATE DYNAMIQUE
# ══════════════════════════════════════
derniere_maj = datetime.now().strftime("%d/%m/%Y à %Hh%M")

# ══════════════════════════════════════
# CHARGEMENT DONNÉES — AVANT SIDEBAR
# ══════════════════════════════════════
with st.spinner("Chargement des données..."):
    df_finance        = run_query(Q_KPI_GLOBAL)
    df_ventes         = run_query(Q_KPI_VENTES)
    df_prod           = run_query(Q_KPI_PRODUCTION)
    df_stock          = run_query(Q_KPI_STOCK)
    df_alertes        = run_query(Q_ALERTES_SECURITE)
    df_stocks_alertes = run_query(Q_STOCKS_ALERTES)

# Calculs globaux
solde    = float(df_finance['solde_operationnel'][0])
revenus  = float(df_finance['total_revenus'][0])
depenses = float(df_finance['total_depenses'][0])
marge    = solde / revenus * 100

# Alertes dynamiques
nb_alertes_sec       = len(df_alertes)
date_premiere_alerte = str(df_alertes['timestamp_action'].min())[:10] if nb_alertes_sec > 0 else "N/A"
df_critiques         = df_stocks_alertes[df_stocks_alertes["alerte"] == "Critique"]
df_lenteur           = df_stocks_alertes[df_stocks_alertes["alerte"] == "Lenteur"]
nb_stock_alertes     = len(df_critiques) + len(df_lenteur)

# ══════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════
with st.sidebar:

    # ── BRAND ──
    st.markdown("""
        <div style='padding:20px 16px 14px;
             border-bottom:0.5px solid rgba(255,255,255,0.1)'>
            <div style='display:inline-flex;align-items:center;gap:6px;
                 background:rgba(255,255,255,0.08);
                 border:0.5px solid rgba(255,255,255,0.15);
                 border-radius:20px;padding:4px 10px 4px 8px;margin-bottom:10px'>
                <span style='width:6px;height:6px;border-radius:50%;
                      background:#4CAF50;display:inline-block'></span>
                <span style='font-size:10px;color:rgba(255,255,255,0.5);
                      letter-spacing:1px'>PLATEFORME DÉCISIONNELLE</span>
            </div>
            <div style='font-size:18px;font-weight:600;color:white;
                 line-height:1.2'>🐔 Mali Élevage</div>
            <div style='font-size:12px;color:rgba(255,255,255,0.4);margin-top:2px'>
                Tableau de bord analytique
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── UTILISATEUR ──
    initiales = "".join([
        n[0].upper() for n in st.session_state["name"].split()[:2]
    ])
    st.markdown(f"""
        <div style='padding:12px 16px;display:flex;align-items:center;gap:10px;
             border-bottom:0.5px solid rgba(255,255,255,0.08)'>
            <div style='width:34px;height:34px;border-radius:50%;background:#1B6B32;
                 display:flex;align-items:center;justify-content:center;
                 font-size:12px;font-weight:600;color:#A8E6BF;flex-shrink:0'>
                {initiales}
            </div>
            <div>
                <div style='font-size:13px;font-weight:500;color:white'>
                    {st.session_state["name"]}
                </div>
                <div style='font-size:11px;color:rgba(255,255,255,0.4)'>
                    @{st.session_state["username"]}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── NAVIGATION LABEL ──
    st.markdown("""
        <div style='font-size:10px;font-weight:600;
             color:rgba(255,255,255,0.3);letter-spacing:1.2px;
             text-transform:uppercase;padding:14px 16px 4px'>
            Navigation
        </div>
    """, unsafe_allow_html=True)

    # ── NAVIGATION CLICABLE — st.page_link ──
    st.page_link(
        "app.py",
        label="🏠 Tableau de bord",
        use_container_width=True
    )
    st.page_link(
        "pages/1_Ventes.py",
        label="🛒 Ventes",
        use_container_width=True
    )
    st.page_link(
        "pages/02_Productions.py",
        label="🥚 Productions",
        use_container_width=True
    )
    st.page_link(
        "pages/03_Finance.py",
        label="💰 Finance",
        use_container_width=True
    )
    st.page_link(
        "pages/04_Stocks.py",
        label=f"📦 Stocks {'🔴 ' + str(nb_stock_alertes) if nb_stock_alertes > 0 else ''}",
        use_container_width=True
    )
    st.page_link(
        "pages/05_Audit.py",
        label=f"🔍 Audit {'🔴 ' + str(nb_alertes_sec) if nb_alertes_sec > 0 else ''}",
        use_container_width=True
    )
    st.page_link(
        "pages/06_SaaS.py",
        label="☁️ SaaS",
        use_container_width=True
    )

    # ── FOOTER SIDEBAR ──
    st.markdown(f"""
        <div style='padding:14px 16px;margin-top:8px;
             border-top:0.5px solid rgba(255,255,255,0.08)'>
            <div style='font-size:11px;color:rgba(255,255,255,0.3);line-height:1.8'>
                <span style='display:inline-block;width:6px;height:6px;
                      border-radius:50%;background:#4CAF50;
                      margin-right:5px;vertical-align:middle'></span>
                ETL : {derniere_maj}<br>
                <span style='margin-left:11px'>
                    tenant_id = 1 · 14 tables
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    authenticator.logout("🚪 Déconnexion", location="sidebar")

# ══════════════════════════════════════
# EN-TÊTE PAGE
# ══════════════════════════════════════
st.markdown(f"""
    <div style='background:#0F3D1E;padding:20px 28px;
         border-radius:12px;margin-bottom:20px;
         display:flex;align-items:center;justify-content:space-between'>
        <div>
            <div style='font-size:11px;font-weight:600;
                 color:rgba(255,255,255,0.4);letter-spacing:1px;
                 text-transform:uppercase;margin-bottom:6px'>
                Mali-Élevage Siège
            </div>
            <div style='font-size:20px;font-weight:600;color:white;line-height:1.2'>
                Tableau de Bord Décisionnel
            </div>
            <div style='color:rgba(255,255,255,0.5);margin-top:4px;font-size:12px'>
                Vue globale · 6 domaines · 31 KPIs
            </div>
        </div>
        <div style='display:flex;align-items:center;gap:6px;
             background:rgba(255,255,255,0.08);
             border:0.5px solid rgba(255,255,255,0.15);
             border-radius:20px;padding:7px 14px'>
            <span style='width:7px;height:7px;border-radius:50%;
                  background:#4CAF50;display:inline-block'></span>
            <span style='font-size:12px;color:rgba(255,255,255,0.65)'>
                Données en temps réel
            </span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# KPIs GLOBAUX — LIGNE 1
# ══════════════════════════════════════
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Indicateurs clés globaux
    </div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    ca = df_ventes['ca_total'][0]
    st.metric(
        label="Chiffre d'Affaires",
        value=f"{ca/1_000_000:.1f}M XOF",
        delta=f"{df_ventes['nb_commandes'][0]} commandes"
    )
with col2:
    taux = float(df_ventes['taux_recouvrement'][0])
    st.metric(
        label="Taux de Recouvrement",
        value=f"{taux}%",
        delta=f"Créances : {df_ventes['total_creances'][0]/1000:.0f}K XOF"
    )
with col3:
    eclosion = float(df_prod['taux_eclosion_moyen'][0])
    st.metric(
        label="Taux d'Éclosion Moyen",
        value=f"{eclosion}%",
        delta=f"{df_prod['total_poussins'][0]:,} poussins produits"
    )
with col4:
    st.metric(
        label="Solde Opérationnel",
        value=f"{solde/1_000_000:.2f}M XOF",
        delta=f"Marge : {marge:.2f}%"
    )

# ── LIGNE 2 ──
col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric(
        label="Clients Actifs",
        value=f"{df_ventes['nb_clients'][0]}",
        delta=f"Encaissé : {df_ventes['total_encaisse'][0]/1_000_000:.1f}M XOF"
    )
with col6:
    st.metric(
        label="Cycles Production",
        value=f"{df_prod['total_cycles'][0]}",
        delta=f"Taux perte : {df_prod['taux_perte_moyen'][0]}%"
    )
with col7:
    st.metric(
        label="Poussins en Stock",
        value=f"{df_stock['total_restants'][0]:,}",
        delta=f"Écoulement : {df_stock['taux_ecoulement_moyen'][0]}%"
    )
with col8:
    st.metric(
        label="Dépenses / Revenus",
        value=f"{depenses/revenus*100:.1f}%",
        delta=f"Revenus : {revenus/1_000_000:.1f}M XOF"
    )

# ══════════════════════════════════════
# VUE FINANCIÈRE
# ══════════════════════════════════════
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Vue financière globale
    </div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns(2)

with col_left:
    fig_gauge = go.Figure()
    fig_gauge.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=solde,
        title={"text": "Solde Opérationnel (XOF)"},
        delta={"reference": 0, "valueformat": ",.0f"},
        gauge={
            "axis": {"range": [-10_000_000, 30_000_000]},
            "bar": {"color": "#0F3D1E"},
            "steps": [
                {"range": [-10_000_000, 0],         "color": "#FFEBEE"},
                {"range": [0, 10_000_000],           "color": "#E8F5E9"},
                {"range": [10_000_000, 30_000_000],  "color": "#C8E6C9"},
            ],
            "threshold": {
                "line": {"color": "#C62828", "width": 3},
                "thickness": 0.75,
                "value": 0
            }
        }
    ))
    fig_gauge.update_layout(
        height=280,
        margin=dict(t=40, b=20, l=20, r=20),
        paper_bgcolor="white"
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_right:
    labels     = ["Revenus", "Dépenses", "Solde"]
    values     = [revenus, depenses, abs(solde)]
    colors_bar = ["#1B5E20", "#C62828", "#4CAF50"]
    fig_bar = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=colors_bar,
        text=[f"{v/1_000_000:.1f}M" for v in values],
        textposition="outside"
    ))
    fig_bar.update_layout(
        title="Revenus vs Dépenses vs Solde (XOF)",
        height=280,
        margin=dict(t=40, b=20, l=20, r=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        yaxis=dict(gridcolor="#F0F4F0")
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ══════════════════════════════════════
# ALERTES
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Alertes importantes
    </div>
""", unsafe_allow_html=True)

col_a1, col_a2, col_a3 = st.columns(3)

with col_a1:
    st.markdown(f"""
        <div style='background:#FFF5F5;border:0.5px solid #FFCDD2;
             border-left:4px solid #C62828;border-radius:8px;
             padding:14px 16px'>
            <div style='font-size:11px;font-weight:600;color:#C62828;
                 text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px'>
                🔒 Sécurité
            </div>
            <div style='font-size:20px;font-weight:600;color:#B71C1C;
                 line-height:1'>{nb_alertes_sec}</div>
            <div style='font-size:12px;color:#7f0000;margin-top:4px'>
                alertes depuis le {date_premiere_alerte}
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_a2:
    if len(df_critiques) > 0:
        ref     = df_critiques.iloc[0]["reference_eclosion"]
        restant = int(df_critiques.iloc[0]["quantite_restante"])
        taux_e  = float(df_critiques.iloc[0]["taux_ecoulement"])
        jours   = int(df_critiques.iloc[0]["jours_en_stock"])
        st.markdown(f"""
            <div style='background:#FFF5F5;border:0.5px solid #FFCDD2;
                 border-left:4px solid #C62828;border-radius:8px;
                 padding:14px 16px'>
                <div style='font-size:11px;font-weight:600;color:#C62828;
                     text-transform:uppercase;letter-spacing:0.5px;
                     margin-bottom:6px'>📦 Stock Critique</div>
                <div style='font-size:14px;font-weight:600;color:#B71C1C;
                     line-height:1.3'>{ref}</div>
                <div style='font-size:12px;color:#7f0000;margin-top:4px'>
                    {restant:,} poussins · {taux_e}% en {jours}j
                </div>
            </div>
        """, unsafe_allow_html=True)
    elif len(df_lenteur) > 0:
        ref    = df_lenteur.iloc[0]["reference_eclosion"]
        taux_e = float(df_lenteur.iloc[0]["taux_ecoulement"])
        st.markdown(f"""
            <div style='background:#FFFBF0;border:0.5px solid #FFE082;
                 border-left:4px solid #E65100;border-radius:8px;
                 padding:14px 16px'>
                <div style='font-size:11px;font-weight:600;color:#E65100;
                     text-transform:uppercase;letter-spacing:0.5px;
                     margin-bottom:6px'>📦 Stock Lent</div>
                <div style='font-size:14px;font-weight:600;color:#BF360C;
                     line-height:1.3'>{ref}</div>
                <div style='font-size:12px;color:#BF360C;margin-top:4px'>
                    {taux_e}% d'écoulement détecté
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='background:#F1FBF1;border:0.5px solid #C8E6C9;
                 border-left:4px solid #2E7D32;border-radius:8px;
                 padding:14px 16px'>
                <div style='font-size:11px;font-weight:600;color:#2E7D32;
                     text-transform:uppercase;letter-spacing:0.5px;
                     margin-bottom:6px'>📦 Stocks</div>
                <div style='font-size:14px;font-weight:600;color:#1B5E20'>
                    Tout normal
                </div>
                <div style='font-size:12px;color:#1B5E20;margin-top:4px'>
                    Tous les lots s'écoulent bien
                </div>
            </div>
        """, unsafe_allow_html=True)

with col_a3:
    alert_color = "#C62828" if marge < 2 else "#E65100"
    alert_bg    = "#FFF5F5" if marge < 2 else "#FFFBF0"
    alert_bd    = "#FFCDD2" if marge < 2 else "#FFE082"
    text_color  = "#7f0000" if marge < 2 else "#BF360C"
    st.markdown(f"""
        <div style='background:{alert_bg};border:0.5px solid {alert_bd};
             border-left:4px solid {alert_color};border-radius:8px;
             padding:14px 16px'>
            <div style='font-size:11px;font-weight:600;color:{alert_color};
                 text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px'>
                💰 Finance
            </div>
            <div style='font-size:20px;font-weight:600;color:{alert_color};
                 line-height:1'>{marge:.2f}%</div>
            <div style='font-size:12px;color:{text_color};margin-top:4px'>
                marge nette · {depenses/revenus*100:.1f}% dépensés
            </div>
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# FOOTER
# ══════════════════════════════════════
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
st.markdown(f"""
    <div style='text-align:center;color:#AAA;font-size:11px;
         padding:14px;border-top:0.5px solid #E0E8E0'>
        Mali Élevage SARL · Plateforme Décisionnelle · Sprint 7 ·
        ETL : {derniere_maj} ·
        OUEDRAOGO Olivier · Master 1 Data Engineering · INGETIS Paris
    </div>
""", unsafe_allow_html=True)