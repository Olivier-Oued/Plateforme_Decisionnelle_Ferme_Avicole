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
    Q_FINANCE_GLOBAL, Q_DEPENSES_CATEGORIE,
    Q_REVENUS_CATEGORIE, Q_FINANCE_MENSUELLE,
    Q_TRANSACTIONS_SUPPRIMEES
)

# ══════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════
st.set_page_config(
    page_title="Finance — Mali Élevage",
    page_icon="💰",
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
with st.spinner("Chargement des données financières..."):
    df_global     = run_query(Q_FINANCE_GLOBAL)
    df_depenses   = run_query(Q_DEPENSES_CATEGORIE)
    df_revenus    = run_query(Q_REVENUS_CATEGORIE)
    df_mensuel    = run_query(Q_FINANCE_MENSUELLE)
    df_supprimees = run_query(Q_TRANSACTIONS_SUPPRIMEES)

revenus         = float(df_global['total_revenus'][0])
revenus_attente = float(df_global['revenus_attente'][0])
revenus_rejetes = float(df_global['revenus_rejetes'][0])
depenses        = float(df_global['total_depenses'][0])
solde           = float(df_global['solde_operationnel'][0])
apport          = float(df_global['total_apport_dette'][0])
marge           = solde / revenus * 100
pct             = depenses / revenus * 100
montant_supprime = float(df_supprimees["montant"].sum()) if len(df_supprimees) > 0 else 0
solde_reel       = solde - montant_supprime
nb_revenus       = int(df_revenus["nb"].sum()) if "nb" in df_revenus.columns else 366
nb_depenses      = int(df_depenses["nb"].sum()) if "nb" in df_depenses.columns else 732

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
    <div style='background:#E65100;padding:20px 28px;
         border-radius:12px;margin-bottom:20px;
         display:flex;align-items:center;justify-content:space-between'>
        <div>
            <div style='font-size:11px;font-weight:600;
                 color:rgba(255,255,255,0.4);letter-spacing:1px;
                 text-transform:uppercase;margin-bottom:6px'>
                Mali-Élevage Siège
            </div>
            <div style='font-size:20px;font-weight:600;color:white;line-height:1.2'>
                Analyse Financière
            </div>
            <div style='color:rgba(255,255,255,0.5);margin-top:4px;font-size:12px'>
                Revenus · Dépenses · Solde · Évolution mensuelle · Catégories
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
# KPIs FINANCE
# ══════════════════════════════════════
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Indicateurs clés finance
    </div>
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Revenus",
        f"{revenus/1_000_000:.1f}M XOF",
        f"{nb_revenus} transactions validées"
    )
with col2:
    st.metric(
        "Total Dépenses",
        f"{depenses/1_000_000:.1f}M XOF",
        f"{nb_depenses} transactions",
        delta_color="inverse"
    )
with col3:
    st.metric(
        "Solde Opérationnel",
        f"+{solde/1_000_000:.2f}M XOF",
        f"Marge : {marge:.2f}%"
    )
with col4:
    st.metric(
        "Apport / Dette",
        f"{apport/1_000_000:.1f}M XOF",
        "Emprunt — hors solde opérat."
    )
with col5:
    st.metric(
        "Dépenses / Revenus",
        f"{pct:.1f}%",
        delta_color="inverse"
    )

if marge < 5:
    st.markdown(f"""
        <div class='alert-danger'>
            🚨 <strong>Alerte marge critique :</strong>
            Seulement <strong>{marge:.2f}%</strong> de marge nette —
            {pct:.1f}% des revenus sont dépensés.
            Toute dépense imprévue peut mettre la trésorerie en difficulté.
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# DÉTAIL REVENUS PAR STATUT
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Détail revenus par statut de validation
    </div>
""", unsafe_allow_html=True)

col_v, col_a, col_r = st.columns(3)

with col_v:
    st.markdown(f"""
        <div class='alert-success'>
            ✅ <strong>Revenus Validés</strong><br>
            <strong style='font-size:18px'>{revenus:,.0f} XOF</strong><br>
            Transactions confirmées — utilisées dans les KPIs
        </div>
    """, unsafe_allow_html=True)

with col_a:
    st.markdown(f"""
        <div class='alert-warning'>
            ⏳ <strong>Revenus En Attente</strong><br>
            <strong style='font-size:18px'>{revenus_attente:,.0f} XOF</strong><br>
            À valider ou rejeter dans l'application
        </div>
    """, unsafe_allow_html=True)

with col_r:
    st.markdown(f"""
        <div class='alert-danger'>
            ❌ <strong>Revenus Rejetés</strong><br>
            <strong style='font-size:18px'>{revenus_rejetes:,.0f} XOF</strong><br>
            Transactions annulées — exclues des calculs
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# TRANSACTIONS SUPPRIMÉES
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Détection des anomalies — transactions supprimées
    </div>
""", unsafe_allow_html=True)

if len(df_supprimees) > 0:
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric(
            "Transactions supprimées",
            f"{len(df_supprimees)}",
            f"{montant_supprime:,.0f} XOF fantômes",
            delta_color="inverse"
        )
    with col_s2:
        st.metric(
            "Solde réel corrigé",
            f"+{solde_reel/1_000_000:.2f}M XOF",
            f"vs {solde/1_000_000:.2f}M XOF affiché"
        )
    st.markdown(f"""
        <div class='alert-danger'>
            👻 <strong>{len(df_supprimees)} transaction(s) supprimée(s) détectée(s)</strong> —
            <strong>{montant_supprime:,.0f} XOF</strong>
            présent(es) dans l'analytique mais effacé(es) de l'application.<br>
            <small>⚠️ Solde réel = <strong>{solde_reel:,.0f} XOF</strong>
            vs Solde affiché = <strong>{solde:,.0f} XOF</strong></small>
        </div>
    """, unsafe_allow_html=True)
    df_supp_display = df_supprimees[[
        "finance_id", "type_transaction",
        "montant", "date_transaction", "description"
    ]].copy()
    df_supp_display["montant"] = df_supp_display["montant"].apply(
        lambda x: f"{x:,.0f} XOF"
    )
    df_supp_display.columns = ["ID", "Type", "Montant", "Date", "Description"]
    st.dataframe(df_supp_display, use_container_width=True, hide_index=True)
else:
    st.markdown("""
        <div class='alert-success'>
            ✅ Aucune transaction supprimée détectée —
            OLTP et OLAP sont parfaitement synchronisés
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# VUE FINANCIÈRE GLOBALE
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Vue financière globale
    </div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns(2)

with col_left:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=solde,
        title={"text": "Solde Opérationnel (XOF)"},
        delta={"reference": 0, "valueformat": ",.0f"},
        number={"valueformat": ",.0f"},
        gauge={
            "axis": {"range": [-20_000_000, 30_000_000]},
            "bar": {"color": COLORS["primary"]},
            "steps": [
                {"range": [-20_000_000, 0],         "color": "#FFEBEE"},
                {"range": [0, 10_000_000],          "color": "#E8F5E9"},
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
        height=300,
        margin=dict(t=60, b=20, l=20, r=20),
        paper_bgcolor="white"
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_right:
    labels = ["Revenus", "Dépenses", "Apport/Dette", "Solde"]
    values = [revenus, depenses, apport, solde]
    colors = [COLORS["primary"], COLORS["danger"], COLORS["info"], COLORS["secondary"]]
    fig_bar = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=colors,
        text=[f"{v/1_000_000:.1f}M" for v in values],
        textposition="outside"
    ))
    fig_bar.update_layout(
        title="Revenus vs Dépenses vs Solde (XOF)",
        height=300,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        yaxis=dict(gridcolor="#E8F5E9"),
        margin=dict(t=40, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ══════════════════════════════════════
# DÉTAIL PAR CATÉGORIE
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Détail par catégorie
    </div>
""", unsafe_allow_html=True)

col_rev, col_dep = st.columns(2)

with col_rev:
    fig_rev = px.bar(
        df_revenus.head(6),
        x="total", y="categorie_normalisee",
        orientation="h", title="Revenus par catégorie",
        color="total",
        color_continuous_scale=[COLORS["light"], COLORS["primary"]],
        text=df_revenus.head(6)["total"].apply(lambda x: f"{x/1_000_000:.1f}M")
    )
    fig_rev.update_layout(
        height=340, paper_bgcolor="white", plot_bgcolor="white",
        showlegend=False, coloraxis_showscale=False,
        xaxis=dict(gridcolor="#E8F5E9"), margin=dict(t=40, b=20, l=20, r=20)
    )
    fig_rev.update_traces(textposition="outside")
    st.plotly_chart(fig_rev, use_container_width=True)

with col_dep:
    fig_dep = px.bar(
        df_depenses.head(6),
        x="total", y="categorie_normalisee",
        orientation="h", title="Dépenses par catégorie",
        color="total",
        color_continuous_scale=["#FFE0B2", COLORS["danger"]],
        text=df_depenses.head(6)["total"].apply(lambda x: f"{x/1_000_000:.1f}M")
    )
    fig_dep.update_layout(
        height=340, paper_bgcolor="white", plot_bgcolor="white",
        showlegend=False, coloraxis_showscale=False,
        xaxis=dict(gridcolor="#FFF3E0"), margin=dict(t=40, b=20, l=20, r=20)
    )
    fig_dep.update_traces(textposition="outside")
    st.plotly_chart(fig_dep, use_container_width=True)

# ══════════════════════════════════════
# ÉVOLUTION MENSUELLE
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Évolution mensuelle revenus vs dépenses
    </div>
""", unsafe_allow_html=True)

df_mensuel["periode"] = (
    df_mensuel["mois_nom"].str[:3] + " " + df_mensuel["annee"].astype(str)
)
df_mensuel["solde_color"] = df_mensuel["solde"].apply(
    lambda x: COLORS["primary"] if x >= 0 else COLORS["danger"]
)

fig_mens = go.Figure()
fig_mens.add_trace(go.Bar(
    x=df_mensuel["periode"], y=df_mensuel["revenus"],
    name="Revenus", marker_color=COLORS["primary"], opacity=0.85
))
fig_mens.add_trace(go.Bar(
    x=df_mensuel["periode"], y=df_mensuel["depenses"],
    name="Dépenses", marker_color=COLORS["danger"], opacity=0.85
))
fig_mens.add_trace(go.Scatter(
    x=df_mensuel["periode"], y=df_mensuel["solde"],
    name="Solde", mode="lines+markers",
    line=dict(color=COLORS["warning"], width=2.5),
    marker=dict(size=8, color=df_mensuel["solde_color"])
))
fig_mens.add_hline(y=0, line_dash="dash", line_color=COLORS["danger"], line_width=1, opacity=0.5)
fig_mens.update_layout(
    height=420, paper_bgcolor="white", plot_bgcolor="white",
    barmode="group",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    yaxis=dict(gridcolor="#E8F5E9"),
    margin=dict(t=40, b=60, l=20, r=20)
)
st.plotly_chart(fig_mens, use_container_width=True)

nb_deficit  = len(df_mensuel[df_mensuel["solde"] < 0])
nb_excedent = len(df_mensuel[df_mensuel["solde"] >= 0])
nb_total    = len(df_mensuel)
meilleur    = df_mensuel.loc[df_mensuel["solde"].idxmax()]
pire        = df_mensuel.loc[df_mensuel["solde"].idxmin()]

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    st.metric("Mois déficitaires",  f"{nb_deficit}/{nb_total}")
with col_s2:
    st.metric("Mois excédentaires", f"{nb_excedent}/{nb_total}")
with col_s3:
    st.metric("Meilleur mois", meilleur["periode"], f"+{meilleur['solde']/1_000_000:.1f}M XOF")
with col_s4:
    st.metric("Pire mois", pire["periode"], f"{pire['solde']/1_000_000:.1f}M XOF", delta_color="inverse")

# ══════════════════════════════════════
# TABLEAUX DÉTAILLÉS
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Tableaux détaillés
    </div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["💚 Revenus par catégorie", "🔴 Dépenses par catégorie"])

with tab1:
    df_rev_display = df_revenus.copy()
    df_rev_display["total"] = df_rev_display["total"].apply(lambda x: f"{x:,.0f} XOF")
    df_rev_display.columns = ["Catégorie", "Nb transactions", "Total revenus"]
    st.dataframe(df_rev_display, use_container_width=True, hide_index=True)

with tab2:
    df_dep_display = df_depenses.copy()
    df_dep_display["total"] = df_dep_display["total"].apply(lambda x: f"{x:,.0f} XOF")
    df_dep_display["pct"]   = df_dep_display["pct"].apply(lambda x: f"{x}%")
    df_dep_display.columns  = ["Catégorie", "Nb transactions", "Total dépenses", "% total"]
    st.dataframe(df_dep_display, use_container_width=True, hide_index=True)

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