import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import run_query, COLORS, PLOTLY_COLORS
from utils.queries import (
    Q_KPI_VENTES, Q_CA_PAR_PRODUIT,
    Q_CA_PAR_MOIS, Q_TOP_CLIENTS,
    Q_MOYEN_PAIEMENT, Q_CLIENTS_DETTES
)

# ══════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════
st.set_page_config(
    page_title="Ventes — Mali Élevage",
    page_icon="🛒",
    layout="wide"
)

def load_css():
    css_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "assets", "style.css"
    )
    with open(css_path, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ══════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding:20px 0'>
            <h1 style='color:white; font-size:28px'>🐔 Mali Élevage</h1>
            <p style='color:#A5D6A7; font-size:13px'>Plateforme Décisionnelle</p>
            <hr style='border-color:#2E7D32'>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style='color:#A5D6A7; font-size:12px; padding:8px 0; margin-top:8px'>
            ℹ️ Données au 22/05/2026<br>
            🔒 tenant_id = 1<br>
            🛒 367 commandes analysées
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# EN-TÊTE
# ══════════════════════════════════════
st.markdown("""
    <div style='background:linear-gradient(135deg,#0D47A1,#1565C0);
         padding:24px 32px; border-radius:12px; margin-bottom:24px'>
        <h1 style='color:white; margin:0; font-size:28px'>
            🛒 Analyse des Ventes
        </h1>
        <p style='color:#BBDEFB; margin:6px 0 0; font-size:14px'>
            CA · Produits · Clients · Évolution temporelle · Recouvrement
        </p>
    </div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
# CHARGEMENT DONNÉES
# ══════════════════════════════════════
with st.spinner("Chargement des données ventes..."):
    df_kpi      = run_query(Q_KPI_VENTES)
    df_produit  = run_query(Q_CA_PAR_PRODUIT)
    df_mois     = run_query(Q_CA_PAR_MOIS)
    df_clients  = run_query(Q_TOP_CLIENTS)
    df_paiement = run_query(Q_MOYEN_PAIEMENT)
    df_dettes   = run_query(Q_CLIENTS_DETTES)

# ══════════════════════════════════════
# KPIs VENTES
# ══════════════════════════════════════
st.markdown("### 📊 Indicateurs Clés Ventes")
st.markdown("---")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "💰 CA Total",
        f"{float(df_kpi['ca_total'][0])/1_000_000:.1f}M XOF",
        f"{df_kpi['nb_commandes'][0]} commandes"
    )
with col2:
    st.metric(
        "✅ Total Encaissé",
        f"{float(df_kpi['total_encaisse'][0])/1_000_000:.1f}M XOF",
    )
with col3:
    st.metric(
        "⚠️ Créances",
        f"{float(df_kpi['total_creances'][0])/1000:.0f}K XOF",
        delta_color="inverse"
    )
with col4:
    st.metric(
        "📈 Taux Recouvrement",
        f"{df_kpi['taux_recouvrement'][0]}%"
    )
with col5:
    st.metric(
        "👥 Clients Actifs",
        f"{df_kpi['nb_clients'][0]}"
    )

# ══════════════════════════════════════
# CA PAR PRODUIT + MOYEN PAIEMENT
# ══════════════════════════════════════
st.markdown("---")
st.markdown("### 📦 Répartition du CA")

col_left, col_right = st.columns(2)

with col_left:
    fig_pie = px.pie(
        df_produit,
        values="ca_total",
        names="produit_normalise",
        title="CA par Produit",
        color_discrete_sequence=PLOTLY_COLORS,
        hole=0.4
    )
    fig_pie.update_layout(
        height=350,
        paper_bgcolor="white",
        margin=dict(t=40, b=20, l=20, r=20)
    )
    fig_pie.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    fig_pay = px.bar(
        df_paiement,
        x="moyen_paiement",
        y="total",
        title="CA par Moyen de Paiement",
        color="moyen_paiement",
        color_discrete_sequence=PLOTLY_COLORS,
        text=df_paiement["total"].apply(
            lambda x: f"{x/1_000_000:.1f}M"
        )
    )
    fig_pay.update_layout(
        height=350,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(t=40, b=20, l=20, r=20),
        yaxis=dict(gridcolor="#E8F5E9")
    )
    fig_pay.update_traces(textposition="outside")
    st.plotly_chart(fig_pay, use_container_width=True)

# ══════════════════════════════════════
# ÉVOLUTION CA PAR MOIS
# ══════════════════════════════════════
st.markdown("---")
st.markdown("### 📈 Évolution mensuelle du CA")

df_mois["periode"] = (
    df_mois["mois_nom"].str[:3] + " "
    + df_mois["annee"].astype(str)
)

fig_line = go.Figure()
fig_line.add_trace(go.Bar(
    x=df_mois["periode"],
    y=df_mois["ca_mensuel"],
    name="CA Mensuel",
    marker_color=COLORS["primary"],
    text=df_mois["ca_mensuel"].apply(
        lambda x: f"{x/1_000_000:.1f}M"
    ),
    textposition="outside"
))
fig_line.add_trace(go.Scatter(
    x=df_mois["periode"],
    y=df_mois["encaisse_mensuel"],
    name="Encaissé",
    mode="lines+markers",
    line=dict(color=COLORS["secondary"], width=2),
    marker=dict(size=6)
))
fig_line.add_trace(go.Bar(
    x=df_mois["periode"],
    y=df_mois["creances_mensuel"],
    name="Créances",
    marker_color=COLORS["danger"],
    opacity=0.7
))
fig_line.update_layout(
    height=400,
    paper_bgcolor="white",
    plot_bgcolor="white",
    barmode="overlay",
    legend=dict(
        orientation="h",
        yanchor="bottom", y=1.02,
        xanchor="right", x=1
    ),
    yaxis=dict(gridcolor="#E8F5E9"),
    margin=dict(t=40, b=60, l=20, r=20)
)
st.plotly_chart(fig_line, use_container_width=True)

# ══════════════════════════════════════
# TOP 10 CLIENTS
# ══════════════════════════════════════
st.markdown("---")
st.markdown("### 👥 Top 10 Clients")

col_table, col_chart = st.columns([3, 2])

with col_table:
    df_clients_display = df_clients.copy()
    df_clients_display["ca_total"] = df_clients_display[
        "ca_total"
    ].apply(lambda x: f"{x:,.0f} XOF")
    df_clients_display["dette_actuelle"] = df_clients_display[
        "dette_actuelle"
    ].apply(lambda x: f"{x:,.0f} XOF")
    df_clients_display["taux_recouvrement"] = df_clients_display[
        "taux_recouvrement"
    ].apply(lambda x: f"{x}%")
    df_clients_display.columns = [
        "Client", "Commandes",
        "CA Total", "Dette", "Taux Rec."
    ]
    st.dataframe(
        df_clients_display,
        use_container_width=True,
        hide_index=True
    )

with col_chart:
    fig_clients = px.bar(
        df_clients.head(5),
        x="ca_total",
        y="client",
        orientation="h",
        title="Top 5 Clients",
        color="ca_total",
        color_continuous_scale=[
            COLORS["light"],
            COLORS["primary"]
        ]
    )
    fig_clients.update_layout(
        height=350,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(t=40, b=20, l=20, r=20),
        xaxis=dict(gridcolor="#E8F5E9")
    )
    st.plotly_chart(fig_clients, use_container_width=True)

# ══════════════════════════════════════
# CLIENTS AVEC DETTES
# ══════════════════════════════════════
st.markdown("---")
st.markdown("### 🚨 Clients avec Dettes Ouvertes")

if len(df_dettes) > 0:
    for _, row in df_dettes.iterrows():
        jours = (
            pd.Timestamp.now() -
            pd.to_datetime(row["derniere_commande"])
        ).days
        color = "danger" if jours > 30 else "warning"
        st.markdown(f"""
            <div class='alert-{color}'>
                <strong>{row['client']}</strong> —
                Dette : <strong>{row['dette']:,.0f} XOF</strong> —
                Dernière commande : {row['derniere_commande']} —
                {jours} jours sans remboursement
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div class='alert-success'>
            ✅ Aucune dette en cours — tous les clients sont à jour
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# FOOTER
# ══════════════════════════════════════
st.markdown("---")
st.markdown("""
    <div style='text-align:center; color:#888;
         font-size:12px; padding:16px'>
        🛒 Ventes · Mali Élevage SARL ·
        Plateforme Décisionnelle · Mai 2026
    </div>
""", unsafe_allow_html=True)