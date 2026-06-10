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
    Q_ACTIVITE_PAR_USER, Q_ACTIONS_PAR_TYPE,
    Q_ACTIVITE_PAR_JOUR, Q_ALERTES_SECURITE,
    Q_ACTIONS_SUSPECTES
)

# ══════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════
st.set_page_config(
    page_title="Audit — Mali Élevage",
    page_icon="🔍",
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
with st.spinner("Chargement des données audit..."):
    df_users    = run_query(Q_ACTIVITE_PAR_USER)
    df_actions  = run_query(Q_ACTIONS_PAR_TYPE)
    df_jours    = run_query(Q_ACTIVITE_PAR_JOUR)
    df_alertes  = run_query(Q_ALERTES_SECURITE)
    df_suspects = run_query(Q_ACTIONS_SUSPECTES)

total_actions  = int(df_users["nb_actions"].sum())
nb_users       = int(df_users.shape[0])
nb_types       = int(df_actions["action"].nunique())
nb_alertes_sec = len(df_alertes)
nb_suspects    = len(df_suspects)
nb_roles       = int(df_users["user_role"].nunique())

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
    st.page_link("pages/05_Audit.py",
        label=f"🔍 Audit {'🔴 ' + str(nb_alertes_sec) if nb_alertes_sec > 0 else ''}",
        use_container_width=True
    )
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
    <div style='background:#4527A0;padding:20px 28px;
         border-radius:12px;margin-bottom:20px;
         display:flex;align-items:center;justify-content:space-between'>
        <div>
            <div style='font-size:11px;font-weight:600;
                 color:rgba(255,255,255,0.4);letter-spacing:1px;
                 text-transform:uppercase;margin-bottom:6px'>
                Mali-Élevage Siège
            </div>
            <div style='font-size:20px;font-weight:600;color:white;line-height:1.2'>
                Audit & Traçabilité
            </div>
            <div style='color:rgba(255,255,255,0.5);margin-top:4px;font-size:12px'>
                Activité utilisateurs · Actions suspectes · Alertes sécurité
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
# KPIs AUDIT
# ══════════════════════════════════════
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Indicateurs clés audit
    </div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total actions",
        f"{total_actions:,}",
        "depuis nov. 2025"
    )
with col2:
    st.metric(
        "Utilisateurs actifs",
        f"{nb_users}",
        f"{nb_roles} rôles distincts"
    )
with col3:
    st.metric(
        "Types d'actions",
        f"{nb_types}",
        f"sur {len(df_actions['resource'].unique())} ressources"
    )
with col4:
    st.metric(
        "Alertes sécurité",
        f"{nb_alertes_sec}",
        delta_color="inverse" if nb_alertes_sec > 0 else "normal"
    )

if nb_alertes_sec > 0:
    date_premiere      = str(df_alertes['timestamp_action'].min())[:10]
    nb_users_concernes = df_alertes['user_email'].nunique()
    st.markdown(f"""
        <div class='alert-danger'>
            🚨 <strong>{nb_alertes_sec} SECURITY_ALERT détectées</strong>
            depuis le {date_premiere} —
            {nb_users_concernes} utilisateurs concernés.
            Rythme d'environ 1 alerte par jour.
            À investiguer immédiatement !
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# ACTIVITÉ PAR UTILISATEUR
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Activité par utilisateur
    </div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns(2)

with col_left:
    fig_users = px.bar(
        df_users.sort_values("nb_actions", ascending=True),
        x="nb_actions", y="user_email",
        orientation="h",
        title="Nombre d'actions par utilisateur",
        color="nb_actions",
        color_continuous_scale=[COLORS["light"], COLORS["purple"]],
        text="nb_actions"
    )
    fig_users.update_layout(
        height=380, paper_bgcolor="white", plot_bgcolor="white",
        showlegend=False, coloraxis_showscale=False,
        xaxis=dict(gridcolor="#EDE7F6"),
        margin=dict(t=40, b=20, l=20, r=20)
    )
    fig_users.update_traces(textposition="outside")
    st.plotly_chart(fig_users, use_container_width=True)

with col_right:
    fig_roles = px.pie(
        df_users,
        values="nb_actions", names="user_role",
        title="Répartition actions par rôle",
        color_discrete_sequence=PLOTLY_COLORS,
        hole=0.4
    )
    fig_roles.update_layout(
        height=380, paper_bgcolor="white",
        margin=dict(t=40, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_roles, use_container_width=True)

st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:8px'>
        Détail par utilisateur
    </div>
""", unsafe_allow_html=True)
df_users_display = df_users.copy()
df_users_display.columns = ["Email", "Rôle", "Nb actions", "Jours actif"]
st.dataframe(df_users_display, use_container_width=True, hide_index=True)

# ══════════════════════════════════════
# ACTIONS PAR TYPE
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Actions par type et ressource
    </div>
""", unsafe_allow_html=True)

col_left2, col_right2 = st.columns(2)

with col_left2:
    df_actions["label"] = df_actions.apply(
        lambda r: f"{r['action']} / {r['resource']}", axis=1
    )
    fig_actions = px.bar(
        df_actions.head(10).sort_values("nb", ascending=True),
        x="nb", y="label",
        orientation="h",
        title="Top 10 actions les plus fréquentes",
        color="nb",
        color_continuous_scale=[COLORS["light"], COLORS["purple"]],
        text="nb"
    )
    fig_actions.update_layout(
        height=380, paper_bgcolor="white", plot_bgcolor="white",
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="#EDE7F6"),
        margin=dict(t=40, b=20, l=20, r=20)
    )
    fig_actions.update_traces(textposition="outside")
    st.plotly_chart(fig_actions, use_container_width=True)

with col_right2:
    jours_fr = {
        "Monday   ": "Lundi",    "Tuesday  ": "Mardi",
        "Wednesday": "Mercredi", "Thursday ": "Jeudi",
        "Friday   ": "Vendredi", "Saturday ": "Samedi",
        "Sunday   ": "Dimanche"
    }
    df_jours["jour_fr"] = df_jours["jour"].map(
        lambda x: jours_fr.get(x, x.strip())
    )
    df_jours = df_jours.sort_values("num_jour")
    fig_jours = px.bar(
        df_jours,
        x="jour_fr", y="nb_actions",
        title="Activité par jour de la semaine",
        color="nb_actions",
        color_continuous_scale=[COLORS["light"], COLORS["purple"]],
        text="nb_actions"
    )
    fig_jours.update_layout(
        height=380, paper_bgcolor="white", plot_bgcolor="white",
        coloraxis_showscale=False,
        yaxis=dict(gridcolor="#EDE7F6"),
        margin=dict(t=40, b=20, l=20, r=20)
    )
    fig_jours.update_traces(textposition="outside")
    st.plotly_chart(fig_jours, use_container_width=True)

# ══════════════════════════════════════
# ALERTES SÉCURITÉ
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Alertes de sécurité
    </div>
""", unsafe_allow_html=True)

if len(df_alertes) > 0:
    date_min = str(df_alertes['timestamp_action'].min())[:10]
    date_max = str(df_alertes['timestamp_action'].max())[:10]
    st.markdown(f"""
        <div class='alert-danger'>
            🚨 <strong>{len(df_alertes)} SECURITY_ALERT</strong>
            détectées entre le <strong>{date_min}</strong>
            et le <strong>{date_max}</strong>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    df_alertes_display = df_alertes[[
        "user_email", "action", "resource", "details", "timestamp_action"
    ]].copy()
    df_alertes_display["timestamp_action"] = (
        df_alertes_display["timestamp_action"].astype(str).str[:19]
    )
    df_alertes_display.columns = [
        "Utilisateur", "Action", "Ressource", "Détails", "Timestamp"
    ]
    st.dataframe(df_alertes_display, use_container_width=True, hide_index=True)
else:
    st.markdown("""
        <div class='alert-success'>
            ✅ Aucune alerte de sécurité détectée
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════
# ACTIONS SUSPECTES
# ══════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='font-size:10px;font-weight:600;color:#666;
         letter-spacing:1px;text-transform:uppercase;margin-bottom:10px'>
        Actions suspectes (DELETE / REJECT / ANNUL)
    </div>
""", unsafe_allow_html=True)

if nb_suspects > 0:
    st.markdown(f"""
        <div class='alert-warning'>
            ⚠️ <strong>{nb_suspects} actions suspectes</strong>
            détectées — suppressions, rejets et annulations
        </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    df_suspects_display = df_suspects[[
        "user_email", "action", "resource", "details", "timestamp_action"
    ]].copy()
    df_suspects_display["timestamp_action"] = (
        df_suspects_display["timestamp_action"].astype(str).str[:19]
    )
    df_suspects_display.columns = [
        "Utilisateur", "Action", "Ressource", "Détails", "Timestamp"
    ]
    st.dataframe(df_suspects_display, use_container_width=True, hide_index=True)
else:
    st.markdown("""
        <div class='alert-success'>
            ✅ Aucune action suspecte détectée
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