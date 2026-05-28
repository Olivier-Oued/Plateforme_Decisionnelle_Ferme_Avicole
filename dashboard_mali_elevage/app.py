import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import run_query, COLORS, PLOTLY_COLORS
from utils.queries import (
    Q_KPI_GLOBAL, Q_KPI_VENTES,
    Q_KPI_PRODUCTION, Q_KPI_STOCK
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
# SIDEBAR
# ══════════════════════════════════════
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 20px 0'>
            <h1 style='color:white; font-size:28px'>🐔 Mali Élevage</h1>
            <p style='color:#A5D6A7; font-size:13px'>Plateforme Décisionnelle</p>
            <hr style='border-color:#2E7D32'>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style='color:#A5D6A7; font-size:12px; padding:8px'>
            📊 Navigation
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style='color:white; font-size:13px; padding:8px;
             background:#2E7D32; border-radius:6px; margin:4px 0'>
            🏠 Tableau de bord
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style='color:#A5D6A7; font-size:12px;
             padding:8px 0; margin-top:16px'>
            ℹ️ Données au 22/05/2026<br>
            🔒 tenant_id = 1<br>
            📦 14 tables analytiques
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# EN-TÊTE
# ══════════════════════════════════════
st.markdown("""
    <div style='background: linear-gradient(135deg, #1B5E20, #2E7D32);
         padding: 24px 32px; border-radius: 12px; margin-bottom: 24px'>
        <h1 style='color:white; margin:0; font-size:28px'>
            🐔 Mali-Élevage Siège — Tableau de Bord Décisionnel
        </h1>
        <p style='color:#A5D6A7; margin:6px 0 0; font-size:14px'>
            Vue globale · 6 domaines · 31 KPIs · Données en temps réel
        </p>
    </div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# CHARGEMENT DONNÉES
# ══════════════════════════════════════
with st.spinner("Chargement des données..."):
    df_finance  = run_query(Q_KPI_GLOBAL)
    df_ventes   = run_query(Q_KPI_VENTES)
    df_prod     = run_query(Q_KPI_PRODUCTION)
    df_stock    = run_query(Q_KPI_STOCK)

# ══════════════════════════════════════
# KPIs GLOBAUX — LIGNE 1
# ══════════════════════════════════════
st.markdown("### 📊 Indicateurs Clés Globaux")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    ca = df_ventes['ca_total'][0]
    st.metric(
        label="💰 Chiffre d'Affaires",
        value=f"{ca/1_000_000:.1f}M XOF",
        delta=f"{df_ventes['nb_commandes'][0]} commandes"
    )

with col2:
    taux = float(df_ventes['taux_recouvrement'][0])
    st.metric(
        label="📈 Taux de Recouvrement",
        value=f"{taux}%",
        delta=f"Créances : {df_ventes['total_creances'][0]/1000:.0f}K XOF"
    )

with col3:
    eclosion = float(df_prod['taux_eclosion_moyen'][0])
    st.metric(
        label="🥚 Taux d'Éclosion Moyen",
        value=f"{eclosion}%",
        delta=f"{df_prod['total_poussins'][0]:,} poussins produits"
    )

with col4:
    solde = float(df_finance['solde_operationnel'][0])
    st.metric(
        label="💵 Solde Opérationnel",
        value=f"{solde/1_000_000:.2f}M XOF",
        delta=f"Marge : {solde/float(df_finance['total_revenus'][0])*100:.2f}%"
    )

# ══════════════════════════════════════
# KPIs LIGNE 2
# ══════════════════════════════════════
col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric(
        label="👥 Clients Actifs",
        value=f"{df_ventes['nb_clients'][0]}",
        delta=f"Total encaissé : {df_ventes['total_encaisse'][0]/1_000_000:.1f}M XOF"
    )

with col6:
    st.metric(
        label="🔄 Cycles Production",
        value=f"{df_prod['total_cycles'][0]}",
        delta=f"Taux perte : {df_prod['taux_perte_moyen'][0]}%"
    )

with col7:
    st.metric(
        label="📦 Poussins en Stock",
        value=f"{df_stock['total_restants'][0]:,}",
        delta=f"Écoulement : {df_stock['taux_ecoulement_moyen'][0]}%"
    )

with col8:
    revenus = float(df_finance['total_revenus'][0])
    depenses = float(df_finance['total_depenses'][0])
    st.metric(
        label="📉 Dépenses / Revenus",
        value=f"{depenses/revenus*100:.1f}%",
        delta=f"Revenus : {revenus/1_000_000:.1f}M XOF"
    )

# ══════════════════════════════════════
# GRAPHIQUES GLOBAUX
# ══════════════════════════════════════
st.markdown("---")
st.markdown("### 📈 Vue Financière Globale")

col_left, col_right = st.columns(2)

with col_left:
    # Revenus vs Dépenses — jauge
    fig_gauge = go.Figure()

    fig_gauge.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=float(df_finance['solde_operationnel'][0]),
        title={"text": "Solde Opérationnel (XOF)"},
        delta={"reference": 0, "valueformat": ",.0f"},
        gauge={
            "axis": {"range": [-10_000_000, 30_000_000]},
            "bar": {"color": COLORS["primary"]},
            "steps": [
                {"range": [-10_000_000, 0],    "color": "#FFEBEE"},
                {"range": [0, 10_000_000],     "color": "#E8F5E9"},
                {"range": [10_000_000, 30_000_000], "color": "#C8E6C9"},
            ],
            "threshold": {
                "line": {"color": COLORS["danger"], "width": 3},
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
    # Répartition CA par domaine
    labels = ["Revenus", "Dépenses", "Solde"]
    values = [
        float(df_finance['total_revenus'][0]),
        float(df_finance['total_depenses'][0]),
        abs(float(df_finance['solde_operationnel'][0]))
    ]
    colors_bar = [COLORS["primary"], COLORS["danger"], COLORS["secondary"]]

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
        yaxis=dict(gridcolor="#E8F5E9")
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ══════════════════════════════════════
# ALERTES GLOBALES
# ══════════════════════════════════════
st.markdown("---")
st.markdown("### 🚨 Alertes Importantes")

col_a1, col_a2, col_a3 = st.columns(3)

with col_a1:
    st.markdown("""
        <div class='alert-danger'>
            🚨 <strong>Sécurité</strong><br>
            17 SECURITY_ALERT détectées<br>
            depuis le 02/05/2026
        </div>
    """, unsafe_allow_html=True)

with col_a2:
    st.markdown("""
        <div class='alert-warning'>
            ⚠️ <strong>Stock</strong><br>
            ECL-2026-014 : 10 590 poussins<br>
            seulement 7% écoulés en 4 jours
        </div>
    """, unsafe_allow_html=True)

with col_a3:
    st.markdown("""
        <div class='alert-warning'>
            ⚠️ <strong>Finance</strong><br>
            Marge nette : 1.01%<br>
            99% des revenus dépensés
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# FOOTER
# ══════════════════════════════════════
st.markdown("---")
st.markdown("""
    <div style='text-align:center; color:#888; font-size:12px; padding:16px'>
        🐔 Mali Élevage SARL · Plateforme Décisionnelle · Sprint 6<br>
        Développé par OUEDRAOGO Olivier · Master 1 Data Engineering · INGETIS Paris · Mai 2026
    </div>
""", unsafe_allow_html=True)