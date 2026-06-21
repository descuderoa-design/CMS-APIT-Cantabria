"""
CMS Turístico de Cantabria
Guías turísticos · Recursos y Restaurantes
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CMS Cantabria",
    page_icon="🏔️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# GOOGLE SHEETS CSV URLS
# Reemplaza los GID con los tuyos reales
# ─────────────────────────────────────────────
SHEET_ID = "1J1T4vS736sotTVP9KgdSje0OxlBvFU_7alO4Mwap5YY"

URLS = {
    "recursos":                  f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=recursos",
    "contenidos_recursos":       f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=contenidos-recursos",
    "restaurantes":              f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=restaurantes",
    "experiencias_restaurantes": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=experiencias_restaurantes",
}

# ─────────────────────────────────────────────
# CARGA DE DATOS (con caché de 10 minutos)
# ─────────────────────────────────────────────
@st.cache_data(ttl=600)
def load_data() -> dict[str, pd.DataFrame]:
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


def load_local_data() -> dict[str, pd.DataFrame]:
    """Fallback: carga desde el xlsx local durante desarrollo."""
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
def get_data() -> dict[str, pd.DataFrame]:
    try:
        if SHEET_ID == "TU_GOOGLE_SHEET_ID":
            raise ValueError("Sheet ID no configurado")
        return load_data()
    except Exception:
        return load_local_data()


# ─────────────────────────────────────────────
# HELPERS DE FECHA / TEMPORADA
# ─────────────────────────────────────────────
DIAS_ES = {
    0: "lunes", 1: "martes", 2: "miércoles",
    3: "jueves", 4: "viernes", 5: "sábado", 6: "domingo",
}

def temporada_actual(hoy: date) -> str:
    """Devuelve 'alta', 'media' o 'baja' según mes."""
    mes = hoy.month
    if mes in (6, 7, 8, 9):
        return "alta"
    if mes in (4, 5, 10):
        return "media"
    return "baja"


def fila_es_hoy(row: pd.Series, hoy: date) -> bool:
    """True si la fila de contenido aplica a la fecha de hoy."""
    try:
        inicio = pd.to_datetime(row.get("fecha_inicio")).date() if pd.notna(row.get("fecha_inicio")) else date.min
        fin    = pd.to_datetime(row.get("fecha_fin")).date()    if pd.notna(row.get("fecha_fin"))    else date.max
        if not (inicio <= hoy <= fin):
            return False
    except Exception:
        pass

    dias_str = str(row.get("dias_semana", "") or "")
    if dias_str.strip():
        dia_hoy = DIAS_ES[hoy.weekday()]
        dias = [d.strip().lower() for d in dias_str.split("-")]
        if dia_hoy not in dias:
            return False
    return True


def filtrar_contenido(df: pd.DataFrame, recurso: str, hoy: date) -> pd.DataFrame:
    sub = df[df["recurso"] == recurso].copy()
    mask = sub.apply(lambda r: fila_es_hoy(r, hoy), axis=1)
    return sub[mask]


# ─────────────────────────────────────────────
# ESTILOS
# ─────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    /* ── Fuente & fondo ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ── Contenedor central estrecho (móvil-first) ── */
    .block-container { max-width: 680px; padding: 1rem 1rem 4rem; }

    /* ── Header de sección ── */
    .section-header {
        background: linear-gradient(135deg, #1a4a6b 0%, #0d7c9e 100%);
        color: white;
        padding: 0.75rem 1.1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        font-weight: 600;
        font-size: 1.05rem;
        letter-spacing: 0.02em;
    }

    /* ── Card genérico ── */
    .card {
        background: #ffffff;
        border: 1px solid #e5e9ef;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 1px 4px rgba(0,0,0,.06);
    }
    .card-title {
        font-weight: 700;
        font-size: 1rem;
        color: #1a2e40;
        margin-bottom: 0.25rem;
    }
    .card-meta {
        font-size: 0.78rem;
        color: #6b7a8d;
        margin-bottom: 0.6rem;
    }

    /* ── Bloque de contenido (horario/tarifa) ── */
    .bloque {
        background: #f4f8fc;
        border-left: 3px solid #0d7c9e;
        border-radius: 0 8px 8px 0;
        padding: 0.55rem 0.8rem;
        margin-bottom: 0.55rem;
    }
    .bloque-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: #0d7c9e;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .bloque-subtipo { font-weight: 600; color: #1a2e40; font-size: 0.88rem; }
    .bloque-contenido { color: #374151; font-size: 0.88rem; }

    /* ── Rating stars ── */
    .stars { color: #f59e0b; font-size: 1rem; }
    .rating-num { font-weight: 700; color: #1a2e40; font-size: 0.9rem; }

    /* ── Badge ── */
    .badge {
        display: inline-block;
        background: #e0f2fe;
        color: #0369a1;
        border-radius: 20px;
        padding: 0.15rem 0.65rem;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 0.3rem;
        margin-bottom: 0.2rem;
    }
    .badge-green { background: #dcfce7; color: #15803d; }
    .badge-amber { background: #fef9c3; color: #92400e; }

    /* ── Temporada banner ── */
    .temporada-alta  { background:#dcfce7; color:#15803d; border:1px solid #86efac; }
    .temporada-media { background:#fef9c3; color:#92400e; border:1px solid #fcd34d; }
    .temporada-baja  { background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; }
    .temporada-badge {
        border-radius: 8px; padding: 0.4rem 0.9rem;
        font-size: 0.8rem; font-weight: 600; margin-bottom: 1rem;
        display: inline-block;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.45rem 1.1rem;
        font-weight: 600;
        font-size: 0.88rem;
    }

    /* ── Selectbox label ── */
    label { font-weight: 600 !important; font-size: 0.83rem !important; color: #374151 !important; }

    /* ── Link ── */
    a { color: #0d7c9e !important; }

    /* ── No results ── */
    .no-results {
        text-align: center; color: #9ca3af;
        padding: 2rem 1rem; font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MÓDULO RECURSOS
# ─────────────────────────────────────────────
def modulo_recursos(dfs: dict, hoy: date):
    recursos_df   = dfs["recursos"]
    contenidos_df = dfs["contenidos_recursos"]

    temp = temporada_actual(hoy)
    temp_label = {"alta": "🌞 Temporada Alta", "media": "🍂 Temporada Media", "baja": "❄️ Temporada Baja"}[temp]
    dia_label  = DIAS_ES[hoy.weekday()].capitalize()

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(
            f'<span class="temporada-badge temporada-{temp}">{temp_label}</span>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<span class="temporada-badge temporada-media">📅 {dia_label}, {hoy.strftime("%d/%m/%Y")}</span>',
            unsafe_allow_html=True,
        )

    # Filtros
    municipios = ["Todos"] + sorted(recursos_df["municipio"].dropna().unique())
    col_m, col_t = st.columns(2)
    with col_m:
        muni = st.selectbox("Municipio", municipios, key="rec_muni")
    with col_t:
        tipos = ["Todos"] + sorted(recursos_df["tipo"].dropna().unique())
        tipo  = st.selectbox("Tipo", tipos, key="rec_tipo")

    df_fil = recursos_df[recursos_df["activo"] == True].copy()
    if muni != "Todos":
        df_fil = df_fil[df_fil["municipio"] == muni]
    if tipo != "Todos":
        df_fil = df_fil[df_fil["tipo"] == tipo]

    df_fil = df_fil.sort_values(["prioridad", "recurso"])

    if df_fil.empty:
        st.markdown('<div class="no-results">No hay recursos para los filtros seleccionados.</div>', unsafe_allow_html=True)
        return

    st.markdown(f"**{len(df_fil)} recurso(s) encontrado(s)**")

    for _, rec in df_fil.iterrows():
        nombre    = rec["recurso"]
        municipio = rec.get("municipio", "")
        tipo_rec  = rec.get("tipo", "")
        web       = rec.get("web_oficial", "")

        contenido_hoy = filtrar_contenido(contenidos_df, nombre, hoy)

        # Agrupar bloques por bloque (horario / tarifa / acceso…)
        bloques_html = ""
        if not contenido_hoy.empty:
            for bloque_tipo, grupo in contenido_hoy.groupby("bloque"):
                for _, fila in grupo.iterrows():
                    subtipo   = fila.get("subtipo", "") or ""
                    contenido = fila.get("contenido", "") or ""
                    fuente    = fila.get("fuente", "") or ""
                    bloques_html += f"""
                    <div class="bloque">
                        <div class="bloque-label">{bloque_tipo}</div>
                        <div class="bloque-subtipo">{subtipo}</div>
                        <div class="bloque-contenido">{contenido}
                            {"<br><small style='color:#9ca3af'>Fuente: " + fuente + "</small>" if fuente else ""}
                        </div>
                    </div>"""
        else:
            bloques_html = "<small style='color:#9ca3af'>Sin datos disponibles para hoy.</small>"

        web_link = f'<a href="{web}" target="_blank">🔗 Web oficial</a>' if pd.notna(web) and web else ""

        st.markdown(f"""
        <div class="card">
            <div class="card-title">🏛️ {nombre}</div>
            <div class="card-meta">
                <span class="badge">{municipio}</span>
                <span class="badge badge-amber">{tipo_rec}</span>
                {web_link}
            </div>
            {bloques_html}
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MÓDULO RESTAURANTES
# ─────────────────────────────────────────────
def modulo_restaurantes(dfs: dict):
    rest_df  = dfs["restaurantes"]
    exp_df   = dfs["experiencias_restaurantes"]

    # Rating medio por restaurante
    rating_medio = (
        exp_df.groupby("restaurante")["rating"]
        .agg(rating_medio="mean", n_resenas="count")
        .reset_index()
    )
    rest_df = rest_df.merge(rating_medio, on="restaurante", how="left")

    # Filtros
    municipios = ["Todos"] + sorted(rest_df["municipio"].dropna().unique())
    col_m, col_g = st.columns(2)
    with col_m:
        muni = st.selectbox("Municipio", municipios, key="rest_muni")
    with col_g:
        solo_grupos = st.toggle("Solo admite grupos", value=False)

    df_fil = rest_df.copy()
    if muni != "Todos":
        df_fil = df_fil[df_fil["municipio"] == muni]
    if solo_grupos:
        df_fil = df_fil[df_fil["admite_grupos"].str.upper().isin(["SÍ", "SI", "YES", "TRUE", "S"])]

    df_fil = df_fil.sort_values("rating_medio", ascending=False, na_position="last")

    if df_fil.empty:
        st.markdown('<div class="no-results">No hay restaurantes para los filtros seleccionados.</div>', unsafe_allow_html=True)
        return

    st.markdown(f"**{len(df_fil)} restaurante(s) encontrado(s)**")

    for _, row in df_fil.iterrows():
        nombre   = row["restaurante"]
        municipio = row.get("municipio", "")
        grupos   = row.get("admite_grupos", "")
        precio   = row.get("precio_menu_grupos", None)
        rating   = row.get("rating_medio", None)
        n_res    = int(row.get("n_resenas", 0)) if pd.notna(row.get("n_resenas")) else 0

        # Estrellas visuales
        if pd.notna(rating):
            estrellas = int(round(rating))
            stars_html = "⭐" * estrellas + "☆" * (5 - estrellas)
            rating_html = f'<span class="stars">{stars_html}</span> <span class="rating-num">{rating:.1f}/5</span> <small style="color:#9ca3af">({n_res} reseña{"s" if n_res != 1 else ""})</small>'
        else:
            rating_html = '<small style="color:#9ca3af">Sin reseñas aún</small>'

        precio_html = f'<span class="badge badge-green">Menú grupo: {int(precio)}€/p.</span>' if pd.notna(precio) else ""
        grupos_badge = '<span class="badge badge-green">✓ Grupos</span>' if str(grupos).upper() in ["SÍ", "SI", "YES"] else ""

        # Reseñas del restaurante
        resenas = exp_df[exp_df["restaurante"] == nombre].sort_values("fecha", ascending=False)
        resenas_html = ""
        for _, res in resenas.head(3).iterrows():
            fecha_str = pd.to_datetime(res["fecha"]).strftime("%d/%m/%Y") if pd.notna(res.get("fecha")) else ""
            guia      = res.get("guia", "")
            comentario = res.get("comentario", "")
            n_p        = res.get("num_personas", "")
            r_stars    = "⭐" * int(res.get("rating", 0))
            resenas_html += f"""
            <div style="border-top:1px solid #e5e9ef; padding-top:0.5rem; margin-top:0.5rem;">
                <div style="font-size:0.78rem; color:#6b7a8d;">{r_stars} · {guia} · {fecha_str} · {n_p} pax</div>
                <div style="font-size:0.85rem; color:#374151; margin-top:0.2rem;">{comentario}</div>
            </div>"""

        st.markdown(f"""
        <div class="card">
            <div class="card-title">🍽️ {nombre}</div>
            <div class="card-meta">
                <span class="badge">{municipio}</span>
                {grupos_badge}
                {precio_html}
            </div>
            <div style="margin-bottom:0.5rem;">{rating_html}</div>
            {resenas_html if resenas_html else '<small style="color:#9ca3af">Sin reseñas registradas.</small>'}
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# APP PRINCIPAL
# ─────────────────────────────────────────────
def main():
    inject_css()

    # Header
    st.markdown("""
    <div style="text-align:center; padding: 1.2rem 0 0.5rem;">
        <div style="font-size:2rem;">🏔️</div>
        <div style="font-weight:700; font-size:1.35rem; color:#1a2e40; letter-spacing:-0.01em;">CMS Cantabria</div>
        <div style="color:#6b7a8d; font-size:0.82rem; margin-top:0.2rem;">Panel de Guías Turísticos</div>
    </div>
    """, unsafe_allow_html=True)

    # Carga de datos
    with st.spinner("Cargando datos…"):
        dfs = get_data()

    hoy = date.today()

    # Botón de recarga
    col_ref, _ = st.columns([1, 3])
    with col_ref:
        if st.button("🔄 Actualizar datos"):
            st.cache_data.clear()
            st.rerun()

    st.divider()

    # Navegación por pestañas
    tab_rec, tab_rest = st.tabs(["🏛️ Recursos", "🍽️ Restaurantes"])

    with tab_rec:
        st.markdown('<div class="section-header">🏛️ Recursos Turísticos</div>', unsafe_allow_html=True)
        modulo_recursos(dfs, hoy)

    with tab_rest:
        st.markdown('<div class="section-header">🍽️ Restaurantes</div>', unsafe_allow_html=True)
        modulo_restaurantes(dfs)

    # Footer
    st.markdown("""
    <div style="text-align:center; color:#9ca3af; font-size:0.72rem; margin-top:2rem; padding-bottom:1rem;">
        CMS Cantabria · Datos actualizados desde Google Sheets
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
