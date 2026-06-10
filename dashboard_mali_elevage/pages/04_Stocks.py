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
    Q_KPI_STOCK, Q_STOCKS_DETAIL,
    Q_STOCKS_ALERTES, Q_RENTABILITE_CYCLES
)

# ══════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════
st.set_page_config(
    page_title="Stocks — Mali Élevage",
    page_icon="📦",
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
with st.spinner("Chargement des données stocks..."):
    df_kpi     = run_query(Q_KPI_STOCK)
    df_detail  = run_query(Q_STOCKS_DETAIL)
    df_alertes = run_query(Q_STOCKS_ALERTES)
    df_rentab  = run_query(Q_RENTABILITE_CYCLES)

total_lots     = int(df_detail.shape[0])
lots_actifs    = int(df_detail[df_detail["statut_stock"].fillna("Actif") != "Terminé"].shape[0])
lots_termines  = total_lots - lots_actifs
total_vendus   = int(df_kpi["total_vendus"][0])
total_restants = int(df_kpi["total_restants"][0])
total_entres   = total_vendus + total_restants
taux_ecoul     = float(df_kpi["taux_ecoulement_moyen"][0])
pct_restant    = total_restants / total_entres * 100

df_critiques = df_alertes[df_alertes["alerte"] == "Critique"]
df_lenteur   = df_alertes[df_alertes["alerte"] == "Lenteur"]
nb_alertes   = len(df_critiques) + len(df_lenteur)

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
    st.page_link("pages/04_Stocks.py",
        label=f"📦 Stocks {'🔴 ' + str(nb_alertes) if nb_alertes > 0 else ''}",
        use_container_width=True
    )
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
    <div style='background:#004D40;padding:20px 28px;
         border-radius:12px;margin-bottom:20px;
         display:flex;align-items:center;justify-content:space-between'>
        <div>
            <div style='font-size:11px;font-weight:600;
                 color:rgba(255,255,255,0.4);letter-spacing:1px;
                 text-transform:uppercase;margin-bottom:6px'>
                Mali-Élevage Siège
            </div>
            <div style='font-size:20px;font-weight:600;color:white;line-height:1.2'>
                Gestion des Stocks
            </div>
            <div style='color:rgba(255,255,255,0.5);margin-top:4px;font-size:12px'>
                Poussins · Alertes · Vitesse de vente · Rentabilité par cycle
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
# KPIs STOCKS
# ══════════════════════════════════════
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Indicateurs clés stocks
    </div>
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total lots",
        f"{total_lots}",
        f"{lots_actifs} actifs · {lots_termines} terminés"
    )
with col2:
    st.metric(
        "Poussins vendus",
        f"{total_vendus:,}",
        "depuis entrée en stock"
    )
with col3:
    st.metric(
        "Poussins restants",
        f"{total_restants:,}",
        delta_color="inverse"
    )
with col4:
    st.metric("Taux d'écoulement", f"{taux_ecoul}%")
with col5:
    st.metric(
        "% stock restant",
        f"{pct_restant:.1f}%",
        delta_color="inverse"
    )

# ══════════════════════════════════════
# ALERTES STOCKS
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Alertes stocks actifs
    </div>
""", unsafe_allow_html=True)

df_alertes_actives = df_alertes[df_alertes["alerte"].isin(["Critique", "Lenteur"])]

if len(df_alertes_actives) > 0:
    for _, row in df_alertes_actives.iterrows():
        alerte    = row["alerte"]
        jours     = int(row["jours_en_stock"])
        taux      = float(row["taux_ecoulement"])
        ref       = row["reference_eclosion"]
        rest      = int(row["quantite_restante"])
        css_class = "alert-danger" if alerte == "Critique" else "alert-warning"
        emoji     = "🚨" if alerte == "Critique" else "⚠️"
        st.markdown(f"""
            <div class='{css_class}'>
                {emoji} <strong>{ref}</strong> —
                {rest:,} poussins restants —
                Taux écoulement : <strong>{taux}%</strong> —
                {jours} jours en stock —
                Statut : <strong>{alerte}</strong>
            </div>
        """, unsafe_allow_html=True)
else:
    df_actifs_norm = df_alertes[df_alertes["alerte"] == "Normal"]
    if len(df_actifs_norm) > 0:
        st.markdown(f"""
            <div class='alert-success'>
                ✅ <strong>{len(df_actifs_norm)} lot(s) actif(s)</strong>
                — tous en bonne vitesse d'écoulement
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class='alert-success'>
                ✅ Aucun lot actif en ce moment
            </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════
# DÉTAIL PAR LOT
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Détail par lot
    </div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns(2)

with col_left:
    df_actifs_chart = df_detail[df_detail["statut_stock"] != "Terminé"].copy()
    if len(df_actifs_chart) > 0:
        fig_actifs = go.Figure()
        for _, row in df_actifs_chart.iterrows():
            fig_actifs.add_trace(go.Bar(
                name=row["reference_eclosion"],
                x=[row["reference_eclosion"]],
                y=[row["taux_ecoulement"]],
                text=f"{row['taux_ecoulement']}%",
                textposition="outside",
                marker_color=COLORS["primary"] if row["taux_ecoulement"] >= 50 else COLORS["warning"]
            ))
        fig_actifs.update_layout(
            title="Taux d'écoulement — Lots actifs",
            height=320, paper_bgcolor="white", plot_bgcolor="white",
            showlegend=False,
            yaxis=dict(gridcolor="#E8F5E9", range=[0, 100]),
            margin=dict(t=40, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_actifs, use_container_width=True)
    else:
        st.info("Aucun lot actif actuellement")

with col_right:
    fig_pie = go.Figure(go.Pie(
        labels=["Vendus", "Restants"],
        values=[total_vendus, total_restants],
        hole=0.4,
        marker_colors=[COLORS["primary"], COLORS["warning"]]
    ))
    fig_pie.update_layout(
        title="Répartition Vendus vs Restants",
        height=320, paper_bgcolor="white",
        margin=dict(t=40, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ══════════════════════════════════════
# VITESSE DE VENTE
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Vitesse de vente par lot
    </div>
""", unsafe_allow_html=True)

df_vitesse = df_detail.copy()
df_vitesse["jours_en_stock"] = df_vitesse["jours_en_stock"].astype(int)
df_vitesse["vitesse"] = (
    df_vitesse["poussins_vendus"] /
    df_vitesse["jours_en_stock"].replace(0, 1)
).round(1)

fig_vitesse = px.bar(
    df_vitesse.sort_values("vitesse", ascending=False),
    x="reference_eclosion", y="vitesse",
    title="Poussins vendus par jour (vitesse d'écoulement)",
    color="vitesse",
    color_continuous_scale=[COLORS["warning"], COLORS["primary"]],
    text="vitesse"
)
fig_vitesse.update_layout(
    height=380, paper_bgcolor="white", plot_bgcolor="white",
    coloraxis_showscale=False, xaxis_tickangle=-30,
    yaxis=dict(gridcolor="#E8F5E9"),
    margin=dict(t=40, b=80, l=20, r=20)
)
fig_vitesse.update_traces(texttemplate="%{text:.0f}/j", textposition="outside")
st.plotly_chart(fig_vitesse, use_container_width=True)

# ══════════════════════════════════════
# RENTABILITÉ PAR CYCLE
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Rentabilité croisée stock → production → ventes
    </div>
""", unsafe_allow_html=True)

df_rent = df_rentab.dropna(subset=["ratio_ca_cout"]).copy()
df_rent["ratio_ca_cout"] = df_rent["ratio_ca_cout"].astype(float)
df_rent["rentable"] = df_rent["ratio_ca_cout"].apply(
    lambda x: "Rentable" if x >= 1 else "Déficitaire"
)

col_chart, col_table = st.columns([2, 3])

with col_chart:
    fig_rent = px.bar(
        df_rent.sort_values("ratio_ca_cout", ascending=True),
        x="ratio_ca_cout", y="numero_fichier",
        orientation="h",
        title="Ratio CA/Coût par cycle (> 1 = rentable)",
        color="rentable",
        color_discrete_map={
            "Rentable"   : COLORS["primary"],
            "Déficitaire": COLORS["danger"]
        },
        text="ratio_ca_cout"
    )
    fig_rent.add_vline(
        x=1, line_dash="dash",
        line_color=COLORS["warning"], line_width=2,
        annotation_text="Seuil rentabilité",
        annotation_position="top"
    )
    fig_rent.update_layout(
        height=420, paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(gridcolor="#E8F5E9"),
        margin=dict(t=60, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_rent.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    st.plotly_chart(fig_rent, use_container_width=True)

with col_table:
    colonnes_dispo = df_rent.columns.tolist()
    cols_voulues = [
        "numero_fichier", "poussins_commercialisables",
        "poussins_vendus", "taux_ecoulement",
        "ca_cycle", "ratio_ca_cout", "rentable"
    ]
    cols_affichage  = [c for c in cols_voulues if c in colonnes_dispo]
    df_rent_display = df_rent[cols_affichage].copy()

    if "ca_cycle" in df_rent_display.columns:
        df_rent_display["ca_cycle"] = df_rent_display["ca_cycle"].apply(
            lambda x: f"{x:,.0f} XOF"
        )
    if "taux_ecoulement" in df_rent_display.columns:
        df_rent_display["taux_ecoulement"] = df_rent_display["taux_ecoulement"].apply(
            lambda x: f"{x}%"
        )

    labels_map = {
        "numero_fichier"             : "Cycle",
        "poussins_commercialisables" : "Produits",
        "poussins_vendus"            : "Vendus",
        "taux_ecoulement"            : "Écoulement",
        "ca_cycle"                   : "CA Cycle",
        "ratio_ca_cout"              : "Ratio",
        "rentable"                   : "Statut"
    }
    df_rent_display.columns = [labels_map[c] for c in cols_affichage]
    st.dataframe(df_rent_display, use_container_width=True, hide_index=True, height=420)

nb_rentable    = len(df_rent[df_rent["rentable"] == "Rentable"])
nb_deficitaire = len(df_rent[df_rent["rentable"] == "Déficitaire"])

col_r1, col_r2 = st.columns(2)
with col_r1:
    st.markdown(f"""
        <div class='alert-success'>
            ✅ <strong>{nb_rentable} cycles rentables</strong>
            sur {len(df_rent)} analysés (ratio CA/coût > 1)
        </div>
    """, unsafe_allow_html=True)
with col_r2:
    st.markdown(f"""
        <div class='alert-warning'>
            ⚠️ <strong>{nb_deficitaire} cycles déficitaires</strong>
            — la plupart sont encore en cours de vente,
            le ratio va s'améliorer
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# TABLEAU DÉTAIL COMPLET
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Tableau détail complet — tous les lots
    </div>
""", unsafe_allow_html=True)

df_full = df_detail.copy()
df_full["poussins_vendus"]   = df_full["poussins_vendus"].apply(lambda x: f"{x:,}")
df_full["quantite_initiale"] = df_full["quantite_initiale"].apply(lambda x: f"{x:,}")
df_full["quantite_restante"] = df_full["quantite_restante"].apply(lambda x: f"{x:,}")
df_full["taux_ecoulement"]   = df_full["taux_ecoulement"].apply(lambda x: f"{x}%")
df_full["jours_en_stock"]    = df_full["jours_en_stock"].apply(lambda x: f"{int(x)}j")

df_full = df_full[[
    "reference_eclosion", "date_entree_stock",
    "statut_stock", "quantite_initiale",
    "poussins_vendus", "quantite_restante",
    "taux_ecoulement", "jours_en_stock"
]]
df_full.columns = [
    "Référence", "Date entrée", "Statut",
    "Initial", "Vendus", "Restants",
    "Écoulement", "Jours"
]
st.dataframe(df_full, use_container_width=True, hide_index=True)

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