import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# ══════════════════════════════════════
# TEMPLATE DE CONNEXION POSTGRESQL
# ══════════════════════════════════════
# INSTRUCTIONS :
# 1. Copiez ce fichier : cp config.example.py config.py
# 2. Remplacez les valeurs ci-dessous par vos vrais credentials
# 3. Ne committez JAMAIS config.py sur GitHub (.gitignore le protège)

DATABASE_URL = (
    "postgresql://VOTRE_USER:VOTRE_PASSWORD"
    "@VOTRE_HOST:5432/VOTRE_DATABASE"
    "?sslmode=require"
)

# ══════════════════════════════════════
# COULEURS MALI ÉLEVAGE
# ══════════════════════════════════════
COLORS = {
    "primary"  : "#1B5E20",
    "secondary": "#4CAF50",
    "accent"   : "#81C784",
    "light"    : "#E8F5E9",
    "white"    : "#FFFFFF",
    "text"     : "#212121",
    "warning"  : "#F57F17",
    "danger"   : "#B71C1C",
    "info"     : "#0D47A1",
    "purple"   : "#4527A0",
}

PLOTLY_COLORS = [
    "#1B5E20", "#4CAF50", "#81C784",
    "#0D47A1", "#F57F17", "#B71C1C",
    "#4527A0", "#004D40", "#880E4F"
]

@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL)

def run_query(sql: str) -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql(sql, engine)
