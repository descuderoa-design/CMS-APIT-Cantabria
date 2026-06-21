"""
CMS Turístico de Cantabria
Guías turísticos · Recursos y Restaurantes
"""

import streamlit as st
import pandas as pd
from datetime import date
import textwrap
from urllib.parse import quote

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CMS Cantabria",
    page_icon="🏔️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

SHEET_ID  = "1J1T4vS736sotTVP9KgdSje0OxlBvFU_7alO4Mwap5YY"
EMAIL     = "info@apitcantabria.com"

URLS = {
    "recursos":                  f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=recursos",
    "contenidos_recursos":       f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=contenidos-recursos",
    "restaurantes":              f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=restaurantes",
    "experiencias_restaurantes": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=experiencias_restaurantes",
}

# ─────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────
@st.cache_data(ttl=600)
def load_data() -> dict:
    date_cols = {
        "recursos":                  ["ultima_actualizacion"],
        "contenidos_recursos":       ["actualizado", "fecha_inicio", "fecha_fin"],
        "restaurantes":              [],
        "experiencias_restaurantes": ["fecha"],
    }
    dfs = {}
    for key, url in URLS.items():
        df = pd.read_csv(url, parse_dates=date_cols[key])
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        dfs[key] = df
    return dfs


def load_local_data() -> dict:
    xl = pd.read_excel("recursos_y_restaurantes.xlsx", sheet_name=None)
    mapping = {
        "recursos":                  "recursos",
        "contenidos-recursos":       "contenidos_recursos",
        "restaurantes":              "restaurantes",
        "experiencias_restaurantes": "experiencias_restaurantes",
    }
    dfs = {}
    for sheet, key in mapping.items():
        df = xl[sheet].copy()
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        dfs[key] = df
    return dfs


@st.cache_data(ttl=600)
def get_data() -> dict:
    try:
        if SHEET_ID == "TU_GOOGLE_SHEET_ID":
            raise ValueError("Sheet ID no configurado")
        return load_data()
    except Exception:
        return load_local_data()

# ─────────────────────────────────────────────
# GMAIL LINK
# ─────────────────────────────────────────────
def gmail_link(asunto: str, cuerpo: str) -> str:
    base = "https://mail.google.com/mail/?view=cm&fs=1"
    cuerpo = cuerpo.replace("\n", "%0A")

    return (
        base +
        f"&to={quote(EMAIL)}"
        f"&su={quote(asunto)}"
        f"&body={cuerpo}"
    )

# ─────────────────────────────────────────────
# HELPERS FECHA
# ─────────────────────────────────────────────
DIAS_ES = {
    0: "lunes", 1: "martes", 2: "miércoles",
    3: "jueves", 4: "viernes", 5: "sábado", 6: "domingo",
}


def fila_es_fecha(row: pd.Series, fecha: date) -> bool:
    try:
        inicio = pd.to_datetime(row.get("fecha_inicio")).date() if pd.notna(row.get("fecha_inicio")) else date.min
        fin    = pd.to_datetime(row.get("fecha_fin")).date()    if pd.notna(row.get("fecha_fin"))    else date.max
        if not (inicio <= fecha <= fin):
            return False
    except Exception:
        pass

    dias_str = str(row.get("dias_semana", "") or "")
    if dias_str.strip():
        dia = DIAS_ES[fecha.weekday()]
        dias = [d.strip().lower() for d in dias_str.split("-")]
        if dia not in dias:
            return False
    return True


def filtrar_contenido(df: pd.DataFrame, recurso: str, fecha: date) -> pd.DataFrame:
    sub = df[df["recurso"] == recurso].copy()
    mask = sub.apply(lambda r: fila_es_fecha(r, fecha), axis=1)
    return sub[mask]


def html(s: str) -> str:
    return textwrap.dedent(s).strip()

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
def inject_css():
    st.markdown(html("""
    <style>
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .block-container { max-width: 680px; padding: 1rem 1rem 4rem; }
    .section-header { background: linear-gradient(135deg,#1a4a6b,#0d7c9e);
        color:white;padding:0.75rem 1rem;border-radius:10px;margin-bottom:1rem;}
    .card { background:#fff;border:1px solid #e5e9ef;border-radius:12px;
        padding:1rem;margin-bottom:0.85rem;}
    .card-title { font-weight:700; }
    .badge { background:#e0f2fe;padding:0.15rem 0.6rem;border-radius:20px;font-size:0.7rem;}
    .report-btn { font-size:0.75rem;color:#0d7c9e;text-decoration:none;margin-right:0.6rem;}
    .report-row { margin-top:0.5rem;border-top:1px solid #eee;padding-top:0.5rem;}
    .disclaimer { font-size:0.75rem;color:#78350f;background:#fffbeb;padding:0.5rem;border-radius:8px;}
    </style>
    """), unsafe_allow_html=True)

# ─────────────────────────────────────────────
# REPORT EMAILS
# ─────────────────────────────────────────────
def build_report_links_recurso(nombre):
    asunto_error = f"[CMS Cantabria] Corrección de datos: {nombre}"
    cuerpo_error = f"""Hola,

He detectado un dato incorrecto en el recurso «{nombre}».

Descripción del error:
[...]

Gracias."""
    
    asunto_nuevo = "[CMS Cantabria] Nuevo recurso turístico"
    cuerpo_nuevo = """Hola,

Quiero proponer un nuevo recurso turístico.

Nombre:
Municipio:
Tipo:
Web:
Descripción:

Gracias."""

    return f"""
    <div class="report-row">
        <a class="report-btn" href="{gmail_link(asunto_error, cuerpo_error)}">✏️ Corregir datos</a>
        <a class="report-btn" href="{gmail_link(asunto_nuevo, cuerpo_nuevo)}">➕ Nuevo recurso</a>
    </div>
    """


def build_report_links_restaurante(nombre):
    asunto = f"[CMS Cantabria] Corrección restaurante: {nombre}"
    cuerpo = f"""Hola,

He detectado un error en el restaurante «{nombre}».

Descripción del error:
[...]

Gracias."""

    return f"""
    <div class="report-row">
        <a class="report-btn" href="{gmail_link(asunto, cuerpo)}">✏️ Corregir datos</a>
    </div>
    """

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    inject_css()

    st.title("🏔️ CMS Cantabria")

    dfs = get_data()

    tab_rec, tab_rest = st.tabs(["Recursos", "Restaurantes"])

    # ───── RECURSOS
    with tab_rec:
        st.markdown('<div class="section-header">Recursos turísticos</div>', unsafe_allow_html=True)

        for _, r in dfs["recursos"].iterrows():
            st.markdown(f"""
            <div class="card">
                <div class="card-title">{r['recurso']}</div>
                <div class="badge">{r.get('municipio','')}</div>
                {build_report_links_recurso(r['recurso'])}
            </div>
            """, unsafe_allow_html=True)

    # ───── RESTAURANTES
    with tab_rest:
        st.markdown('<div class="section-header">Restaurantes</div>', unsafe_allow_html=True)

        for _, r in dfs["restaurantes"].iterrows():
            st.markdown(f"""
            <div class="card">
                <div class="card-title">🍽️ {r['restaurante']}</div>
                <div class="badge">{r.get('municipio','')}</div>
                {build_report_links_restaurante(r['restaurante'])}
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
