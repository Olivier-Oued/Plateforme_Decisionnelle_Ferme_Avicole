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
    Q_FERMES, Q_PROFILS,
    Q_ALERTES_SECURITE
)

# ══════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════
st.set_page_config(
    page_title="SaaS — Mali Élevage",
    page_icon="☁️",
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
with st.spinner("Chargement des données SaaS..."):
    df_fermes  = run_query(Q_FERMES)
    df_profils = run_query(Q_PROFILS)
    df_alertes = run_query(Q_ALERTES_SECURITE)

nb_fermes        = len(df_fermes)
nb_profils_actif = int(df_profils["profils_actifs"].sum())
nb_alertes_sec   = len(df_alertes)
today            = pd.Timestamp.now().date()

expires = df_fermes[df_fermes["fin_abonnement"].notna()].copy()
expires["fin_abonnement"] = pd.to_datetime(expires["fin_abonnement"]).dt.date
nb_expires    = len(expires[expires["fin_abonnement"] < today])
ferme_expiree = expires[expires["fin_abonnement"] < today]

if len(ferme_expiree) > 0:
    fin_exp      = ferme_expiree["fin_abonnement"].min()
    jours_retard = (today - fin_exp).days
else:
    fin_exp      = None
    jours_retard = 0

date_premiere_alerte = (
    str(df_alertes['timestamp_action'].min())[:10]
    if nb_alertes_sec > 0 else "N/A"
)

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
    <div style='background:#880E4F;padding:20px 28px;
         border-radius:12px;margin-bottom:20px;
         display:flex;align-items:center;justify-content:space-between'>
        <div>
            <div style='font-size:11px;font-weight:600;
                 color:rgba(255,255,255,0.4);letter-spacing:1px;
                 text-transform:uppercase;margin-bottom:6px'>
                Mali-Élevage Siège
            </div>
            <div style='font-size:20px;font-weight:600;color:white;line-height:1.2'>
                Tableau de Bord SaaS
            </div>
            <div style='color:rgba(255,255,255,0.5);margin-top:4px;font-size:12px'>
                Fermes · Abonnements · Profils · Adoption · Alertes
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
# KPIs SAAS
# ══════════════════════════════════════
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Indicateurs clés SaaS
    </div>
""", unsafe_allow_html=True)

nb_fermes_active = len(df_fermes[df_fermes["is_active"] == 1])
nb_profils_total = int(df_profils["nb_profils"].sum())

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total fermes",
        f"{nb_fermes}",
        f"{nb_fermes_active} actives"
    )
with col2:
    st.metric(
        "Total profils",
        f"{nb_profils_total}",
        f"{nb_profils_actif} actifs"
    )
with col3:
    plans = df_fermes["plan_abonnement"].value_counts()
    st.metric(
        "Plans actifs",
        f"{len(plans)} types",
        " · ".join(plans.index.tolist())
    )
with col4:
    st.metric(
        "Abonnements expirés",
        f"{nb_expires}",
        delta_color="inverse" if nb_expires > 0 else "normal"
    )

if nb_expires > 0 and len(ferme_expiree) > 0:
    nom_ferme = ferme_expiree.iloc[0]["nom"]
    st.markdown(f"""
        <div class='alert-warning'>
            ⚠️ <strong>{nb_expires} abonnement(s) expiré(s)</strong> —
            {nom_ferme} : abonnement expiré depuis le {fin_exp}.
            À régulariser auprès de l'équipe.
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# DÉTAIL FERMES ET ABONNEMENTS
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Détail des fermes et abonnements
    </div>
""", unsafe_allow_html=True)

for _, ferme in df_fermes.iterrows():
    statut_emoji = "✅" if ferme["is_active"] == 1 else "❌"
    fin = ferme["fin_abonnement"]
    if pd.notna(fin):
        fin_date = pd.to_datetime(fin).date()
        expire_label = (
            f"⚠️ Expiré depuis le {fin_date}"
            if fin_date < today
            else f"✅ Valide jusqu'au {fin_date}"
        )
        expire_color = "warning" if fin_date < today else "success"
    else:
        expire_label = "Sans date de fin définie"
        expire_color = "info"

    st.markdown(f"""
        <div style='background:#FAFAFA;border:1px solid #E0E0E0;
             border-left:6px solid {"#1B5E20" if ferme["is_active"]==1 else "#B71C1C"};
             border-radius:8px;padding:16px 20px;margin:12px 0'>
            <div style='display:flex;justify-content:space-between'>
                <div>
                    <div style='margin:0;color:#1A1A1A;font-size:16px;font-weight:600'>
                        {statut_emoji} {ferme["nom"]}
                    </div>
                    <p style='margin:6px 0 0;color:#555;font-size:14px'>
                        Plan : <strong>{ferme["plan_abonnement"]}</strong> ·
                        Statut : <strong>{ferme["statut_abonnement"] or "Non défini"}</strong>
                    </p>
                    <p style='margin:4px 0 0;color:#888;font-size:13px'>
                        Début : {ferme["debut_abonnement"] or "N/A"} ·
                        Fin : {ferme["fin_abonnement"] or "N/A"}
                    </p>
                </div>
                <div style='text-align:right;align-self:center'>
                    <span style='background:#{"E8F5E9" if expire_color=="success" else "FFF8E1" if expire_color=="warning" else "E3F2FD"};
                         color:#{"1B5E20" if expire_color=="success" else "E65100" if expire_color=="warning" else "0D47A1"};
                         padding:6px 14px;border-radius:20px;font-size:13px;font-weight:600'>
                        {expire_label}
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# PROFILS PAR FERME ET RÔLE
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Profils utilisateurs par ferme
    </div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns(2)

with col_left:
    fig_profils = px.bar(
        df_profils.sort_values("nb_profils", ascending=True),
        x="nb_profils", y="role",
        orientation="h",
        color="ferme",
        title="Profils par rôle et ferme",
        color_discrete_sequence=PLOTLY_COLORS,
        text="nb_profils",
        barmode="group"
    )
    fig_profils.update_layout(
        height=380, paper_bgcolor="white", plot_bgcolor="white",
        xaxis=dict(gridcolor="#FCE4EC"),
        margin=dict(t=40, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig_profils.update_traces(textposition="outside")
    st.plotly_chart(fig_profils, use_container_width=True)

with col_right:
    df_mali = df_profils[df_profils["ferme"].str.contains("Mali", na=False)].copy()
    if len(df_mali) > 0:
        actifs   = int(df_mali["profils_actifs"].sum())
        inactifs = int(df_mali["nb_profils"].sum()) - actifs
        fig_pie  = go.Figure(go.Pie(
            labels=["Profils actifs", "Profils inactifs"],
            values=[actifs, inactifs],
            hole=0.4,
            marker_colors=[COLORS["primary"], COLORS["warning"]]
        ))
        fig_pie.update_layout(
            title="Profils actifs — Mali-Élevage Siège",
            height=380, paper_bgcolor="white",
            margin=dict(t=40, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:8px'>
        Tableau détail profils
    </div>
""", unsafe_allow_html=True)
df_profils_display = df_profils.copy()
df_profils_display.columns = ["Ferme", "Rôle", "Nb profils", "Profils actifs"]
st.dataframe(df_profils_display, use_container_width=True, hide_index=True)

# ══════════════════════════════════════
# ANALYSE ADOPTION
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Analyse d'adoption
    </div>
""", unsafe_allow_html=True)

col_a1, col_a2, col_a3 = st.columns(3)

with col_a1:
    st.markdown("""
        <div style='background:#E8F5E9;border-left:4px solid #1B5E20;
             border-radius:8px;padding:16px;text-align:center'>
            <div style='font-size:24px;font-weight:700;color:#1B5E20'>7j/7</div>
            <p style='color:#555;margin:8px 0 0;font-size:14px'>
                Application utilisée tous les jours<br>
                <strong>154 jours actifs sur 180</strong>
            </p>
        </div>
    """, unsafe_allow_html=True)

with col_a2:
    st.markdown("""
        <div style='background:#E8F5E9;border-left:4px solid #1B5E20;
             border-radius:8px;padding:16px;text-align:center'>
            <div style='font-size:24px;font-weight:700;color:#1B5E20'>85%</div>
            <p style='color:#555;margin:8px 0 0;font-size:14px'>
                Taux d'utilisation quotidienne<br>
                <strong>Adoption totale de l'équipe</strong>
            </p>
        </div>
    """, unsafe_allow_html=True)

with col_a3:
    st.markdown(f"""
        <div style='background:#FFF8E1;border-left:4px solid #F57F17;
             border-radius:8px;padding:16px;text-align:center'>
            <div style='font-size:24px;font-weight:700;color:#E65100'>
                {nb_alertes_sec}
            </div>
            <p style='color:#555;margin:8px 0 0;font-size:14px'>
                Alertes sécurité depuis {date_premiere_alerte}<br>
                <strong>À investiguer immédiatement</strong>
            </p>
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# RECOMMANDATIONS
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Recommandations
    </div>
""", unsafe_allow_html=True)

recommandations = [
    ("🚨", "danger",
     f"Investiguer les {nb_alertes_sec} SECURITY_ALERT depuis {date_premiere_alerte}",
     "Identifier les utilisateurs concernés et les causes — rythme d'1 alerte/jour"),
]

if nb_expires > 0:
    recommandations.append((
        "⚠️", "warning",
        "Régulariser l'abonnement Mali-Élevage Siège",
        f"Abonnement expiré depuis le {fin_exp} — {jours_retard} jours de retard"
    ))

recommandations += [
    ("⚠️", "warning",
     "Consolider les 2 comptes de M. Noël OUEDRAOGO",
     "noeoued@mali-elevage.com (admin) + noeoued@gmail.com (superadmin) — fusionner en un seul"),
    ("💡", "success",
     "Développer la base clients SaaS",
     f"{nb_fermes} ferme(s) actuellement — potentiel de croissance important"),
    ("💡", "success",
     "Documenter les rôles et permissions",
     f"{nb_profils_total} profils · {len(df_profils['role'].unique())} rôles — créer un guide utilisateur par rôle"),
]

for emoji, css, titre, detail in recommandations:
    st.markdown(f"""
        <div class='alert-{css}'>
            {emoji} <strong>{titre}</strong><br>
            <span style='font-size:13px'>{detail}</span>
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