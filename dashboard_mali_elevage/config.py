import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# ══════════════════════════════════════
# CONNEXION POSTGRESQL — via st.secrets
# (local : .streamlit/secrets.toml — gitignored
#  cloud : Secrets configurés dans Streamlit Cloud)
# ══════════════════════════════════════
DB_CONFIG = {
    "host"    : st.secrets["database"]["host"],
    "port"    : st.secrets["database"]["port"],
    "database": st.secrets["database"]["database"],
    "user"    : st.secrets["database"]["user"],
    "password": st.secrets["database"]["password"],
}

# psycopg v3 — wheels précompilés disponibles pour Python 3.14
DATABASE_URL = (
    f"postgresql+psycopg://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    f"?sslmode=require"
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

# ══════════════════════════════════════
# CONNEXION CACHÉE — AVEC RECONNEXION AUTO
# ══════════════════════════════════════
@st.cache_resource
def get_engine():
    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10,
        connect_args={
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }
    )

def run_query(sql: str) -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)