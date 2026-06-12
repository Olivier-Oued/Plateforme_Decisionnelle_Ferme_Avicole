import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import run_query, COLORS, PLOTLY_COLORS
from utils.queries import (
    Q_KPI_PRODUCTION, Q_PRODUCTION_CYCLES,
    Q_MACHINE_VS_SANS, Q_PRODUCTION_MENSUELLE,
    Q_COUT_PAR_POUSSIN
)

# ══════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════
st.set_page_config(
    page_title="Production — Mali Élevage",
    page_icon="🥚",
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
# DATE DYNAMIQUE
# ══════════════════════════════════════
date_maj     = datetime.now().strftime("%d/%m/%Y")
derniere_maj = datetime.now().strftime("%d/%m/%Y à %Hh%M")

# ══════════════════════════════════════
# CHARGEMENT DONNÉES — AVANT SIDEBAR
# ══════════════════════════════════════
with st.spinner("Chargement des données production..."):
    df_kpi     = run_query(Q_KPI_PRODUCTION)
    df_cycles  = run_query(Q_PRODUCTION_CYCLES)
    df_machine = run_query(Q_MACHINE_VS_SANS)
    df_mensuel = run_query(Q_PRODUCTION_MENSUELLE)
    df_cout    = run_query(Q_COUT_PAR_POUSSIN)

nb_cycles = int(df_kpi['total_cycles'][0])

# ══════════════════════════════════════
# SIDEBAR — MÊME DESIGN QUE app.py
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
    if st.session_state.get("name"):
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

    # ── NAVIGATION CLICABLE ──
    st.page_link("app.py",                  label="🏠 Tableau de bord", use_container_width=True)
    st.page_link("pages/1_Ventes.py",       label="🛒 Ventes",          use_container_width=True)
    st.page_link("pages/02_Productions.py", label="🥚 Production",      use_container_width=True)
    st.page_link("pages/03_Finance.py",     label="💰 Finance",         use_container_width=True)
    st.page_link("pages/04_Stocks.py",      label="📦 Stocks",          use_container_width=True)
    st.page_link("pages/05_Audit.py",       label="🔍 Audit",           use_container_width=True)
    st.page_link("pages/06_SaaS.py",        label="☁️ SaaS",            use_container_width=True)

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

# ══════════════════════════════════════
# EN-TÊTE
# ══════════════════════════════════════
st.markdown(f"""
    <div style='background:#1B5E20;padding:20px 28px;
         border-radius:12px;margin-bottom:20px;
         display:flex;align-items:center;justify-content:space-between'>
        <div>
            <div style='font-size:11px;font-weight:600;
                 color:rgba(255,255,255,0.4);letter-spacing:1px;
                 text-transform:uppercase;margin-bottom:6px'>
                Mali-Élevage Siège
            </div>
            <div style='font-size:20px;font-weight:600;color:white;line-height:1.2'>
                Analyse de la Production
            </div>
            <div style='color:rgba(255,255,255,0.5);margin-top:4px;font-size:12px'>
                Cycles d'incubation · Taux d'éclosion · Machine vs Sans machine · Coûts
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
# KPIs PRODUCTION
# ══════════════════════════════════════
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Indicateurs clés production
    </div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Cycles analysés",
        f"{nb_cycles}",
        "CYCLE-CREDIT exclu"
    )
with col2:
    taux = float(df_kpi['taux_eclosion_moyen'][0])
    st.metric(
        "Taux d'éclosion moyen",
        f"{taux}%",
        delta_color="normal" if taux >= 80 else "inverse"
    )
with col3:
    st.metric(
        "Total poussins produits",
        f"{int(df_kpi['total_poussins'][0]):,}",
    )
with col4:
    perte = float(df_kpi['taux_perte_moyen'][0])
    st.metric(
        "Taux de perte moyen",
        f"{perte}%",
        delta_color="inverse"
    )

# ══════════════════════════════════════
# MACHINE VS SANS MACHINE
# ══════════════════════════════════════
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Machine 1 vs Sans machine
    </div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns(2)

with col_left:
    fig_machine = go.Figure()
    fig_machine.add_trace(go.Bar(
        name="Taux d'éclosion",
        x=df_machine["type_cycle"],
        y=df_machine["taux_eclosion_moyen"],
        marker_color=[COLORS["primary"], COLORS["secondary"]],
        text=df_machine["taux_eclosion_moyen"].apply(lambda x: f"{x}%"),
        textposition="outside"
    ))
    fig_machine.update_layout(
        title="Taux d'éclosion : Machine vs Sans machine",
        height=320,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        yaxis=dict(gridcolor="#E8F5E9", range=[0, 100]),
        margin=dict(t=40, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_machine, use_container_width=True)

with col_right:
    fig_perte = go.Figure()
    fig_perte.add_trace(go.Bar(
        name="Taux de perte",
        x=df_machine["type_cycle"],
        y=df_machine["taux_perte_moyen"],
        marker_color=[COLORS["danger"], COLORS["warning"]],
        text=df_machine["taux_perte_moyen"].apply(lambda x: f"{x}%"),
        textposition="outside"
    ))
    fig_perte.update_layout(
        title="Taux de perte : Machine vs Sans machine",
        height=320,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        yaxis=dict(gridcolor="#E8F5E9"),
        margin=dict(t=40, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_perte, use_container_width=True)

machine_row    = df_machine[df_machine["type_cycle"] == "Avec Machine 1"]
sans_machine_row = df_machine[df_machine["type_cycle"] == "Sans machine"]

if len(machine_row) > 0 and len(sans_machine_row) > 0:
    taux_machine = float(machine_row["taux_eclosion_moyen"].values[0])
    taux_sans    = float(sans_machine_row["taux_eclosion_moyen"].values[0])
    gain         = round(taux_machine - taux_sans, 2)
    st.markdown(f"""
        <div class='alert-success'>
            💡 <strong>Insight stratégique :</strong>
            Machine 1 → taux d'éclosion <strong>{taux_machine}%</strong> vs
            <strong>{taux_sans}%</strong> sans machine — gain de
            <strong>+{gain} points</strong> soit
            <strong>+1.4M XOF de CA supplémentaire par cycle</strong>
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# ÉVOLUTION MENSUELLE
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Évolution mensuelle de la production
    </div>
""", unsafe_allow_html=True)

df_mensuel["periode"] = (
    df_mensuel["mois_nom"].str[:3] + " "
    + df_mensuel["annee"].astype(str)
)

fig_mensuel = go.Figure()
fig_mensuel.add_trace(go.Bar(
    x=df_mensuel["periode"],
    y=df_mensuel["oeufs_incubes"],
    name="Oeufs incubés",
    marker_color=COLORS["info"],
    opacity=0.7
))
fig_mensuel.add_trace(go.Bar(
    x=df_mensuel["periode"],
    y=df_mensuel["poussins_produits"],
    name="Poussins produits",
    marker_color=COLORS["primary"]
))
fig_mensuel.add_trace(go.Scatter(
    x=df_mensuel["periode"],
    y=df_mensuel["taux_eclosion_moyen"],
    name="Taux éclosion %",
    mode="lines+markers",
    yaxis="y2",
    line=dict(color=COLORS["warning"], width=2),
    marker=dict(size=8)
))
fig_mensuel.update_layout(
    height=400,
    paper_bgcolor="white",
    plot_bgcolor="white",
    barmode="group",
    yaxis=dict(title="Nombre d'oeufs / poussins", gridcolor="#E8F5E9"),
    yaxis2=dict(
        title="Taux d'éclosion (%)",
        overlaying="y",
        side="right",
        range=[0, 100]
    ),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(t=40, b=60, l=20, r=60)
)
st.plotly_chart(fig_mensuel, use_container_width=True)

# ══════════════════════════════════════
# CLASSEMENT DES CYCLES
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Classement des cycles par taux d'éclosion
    </div>
""", unsafe_allow_html=True)

col_table, col_chart = st.columns([3, 2])

with col_table:
    df_display = df_cycles[[
        "numero_fichier", "date_incubation",
        "oeufs_incubes", "oeufs_eclos",
        "taux_eclosion", "taux_perte", "machine"
    ]].copy()
    df_display.columns = [
        "Cycle", "Date", "Oeufs incubés",
        "Oeufs éclos", "Taux éclosion %",
        "Taux perte %", "Machine"
    ]
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        height=400
    )

with col_chart:
    fig_top = px.bar(
        df_cycles.head(5),
        x="taux_eclosion",
        y="numero_fichier",
        orientation="h",
        title="Top 5 meilleurs cycles",
        color="taux_eclosion",
        color_continuous_scale=[COLORS["light"], COLORS["primary"]],
        text="taux_eclosion"
    )
    fig_top.update_layout(
        height=320,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(t=40, b=20, l=20, r=20),
        xaxis=dict(gridcolor="#E8F5E9", range=[0, 100])
    )
    fig_top.update_traces(texttemplate="%{text}%", textposition="outside")
    st.plotly_chart(fig_top, use_container_width=True)

# ══════════════════════════════════════
# COÛT PAR POUSSIN
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Coût de production par poussin
    </div>
""", unsafe_allow_html=True)

prix_vente_moyen = 643

fig_cout = px.bar(
    df_cout,
    x="numero_fichier",
    y="cout_par_poussin",
    title="Coût par poussin produit (XOF) — du moins cher au plus cher",
    color="cout_par_poussin",
    color_continuous_scale=[
        COLORS["secondary"], COLORS["warning"], COLORS["danger"]
    ],
    text="cout_par_poussin"
)
fig_cout.add_hline(
    y=prix_vente_moyen,
    line_dash="dash",
    line_color=COLORS["info"],
    annotation_text=f"Prix de vente moyen : {prix_vente_moyen} XOF",
    annotation_position="top right"
)
fig_cout.update_layout(
    height=380,
    paper_bgcolor="white",
    plot_bgcolor="white",
    coloraxis_showscale=False,
    xaxis_tickangle=-30,
    yaxis=dict(gridcolor="#E8F5E9"),
    margin=dict(t=40, b=80, l=20, r=20)
)
fig_cout.update_traces(texttemplate="%{text:.0f}", textposition="outside")
st.plotly_chart(fig_cout, use_container_width=True)

cycles_perte = df_cout[df_cout["cout_par_poussin"] > prix_vente_moyen]
if len(cycles_perte) > 0:
    cycles_liste = " · ".join([
        f"{row['numero_fichier']} ({row['cout_par_poussin']:.2f} XOF)"
        for _, row in cycles_perte.iterrows()
    ])
    st.markdown(f"""
        <div class='alert-warning'>
            ⚠️ <strong>Attention :</strong> Les cycles dont le coût
            par poussin dépasse <strong>{prix_vente_moyen} XOF</strong>
            (prix de vente moyen) sont vendus à perte.<br>
            Surveiller : <strong>{cycles_liste}</strong>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div class='alert-success'>
            ✅ Tous les cycles sont rentables — coût inférieur
            au prix de vente moyen
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