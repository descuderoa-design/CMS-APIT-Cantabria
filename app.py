"""
CMS Turístico de Cantabria
Recursos y Restaurantes
Formularios internos + Google Apps Script + Google Sheets
"""

import streamlit as st
import pandas as pd
from datetime import date
import textwrap
import requests

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="CMS Cantabria",
    page_icon="🏔️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

SHEET_ID = "1J1T4vS736sotTVP9KgdSje0OxlBvFU_7alO4Mwap5YY"

URLS = {
    "recursos": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=recursos",
    "contenidos_recursos": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=contenidos-recursos",
    "restaurantes": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=restaurantes",
    "experiencias_restaurantes": f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=experiencias_restaurantes",
}

# ─────────────────────────────────────────────
# GOOGLE APPS SCRIPT
# ─────────────────────────────────────────────

def post_to_apps_script(payload: dict):
    payload["token"] = st.secrets["APPS_SCRIPT_TOKEN"]

    response = requests.post(
        st.secrets["APPS_SCRIPT_URL"],
        json=payload,
        timeout=10
    )

    response.raise_for_status()
    result = response.json()

    if not result.get("ok"):
        raise RuntimeError(result.get("error", "Error desconocido"))

    return result


def save_incidencia(data: dict):
    payload = {
        "accion": "incidencia",
        "usuario_nombre": st.session_state.get("guia", ""),
        "tipo": data["tipo"],
        "categoria": data["categoria"],
        "nombre": data["nombre"],
        "municipio": data.get("municipio", ""),
        "asunto": data["asunto"],
        "descripcion": data["descripcion"],
    }

    return post_to_apps_script(payload)


def save_resena_restaurante(data: dict):
    payload = {
        "accion": "nueva_resena_restaurante",
        "restaurante": data["restaurante"],
        "fecha": data["fecha"],
        "guia": st.session_state.get("guia", ""),
        "num_personas": data["num_personas"],
        "precio_por_persona": data["precio_por_persona"],
        "rating": data["rating"],
        "comentario": data["comentario"],
    }

    return post_to_apps_script(payload)


# ─────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────

@st.cache_data(ttl=600)
def load_data():
    dfs = {}

    for key, url in URLS.items():
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        dfs[key] = df

    return dfs


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

DIAS_ES = {
    0: "lunes",
    1: "martes",
    2: "miércoles",
    3: "jueves",
    4: "viernes",
    5: "sábado",
    6: "domingo",
}


def html(s: str) -> str:
    return textwrap.dedent(s).strip()


def fila_es_fecha(row: pd.Series, fecha: date) -> bool:
    try:
        inicio = (
            pd.to_datetime(row.get("fecha_inicio")).date()
            if pd.notna(row.get("fecha_inicio"))
            else date.min
        )
        fin = (
            pd.to_datetime(row.get("fecha_fin")).date()
            if pd.notna(row.get("fecha_fin"))
            else date.max
        )

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

    if sub.empty:
        return sub

    mask = sub.apply(lambda r: fila_es_fecha(r, fecha), axis=1)
    return sub[mask]


# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────

def inject_css():
    st.markdown(html("""
    <style>
    .block-container {
        max-width: 720px;
        padding: 1rem 1rem 4rem;
    }

    .section-header {
        background: linear-gradient(135deg, #1a4a6b 0%, #0d7c9e 100%);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        font-weight: 600;
    }

    .card {
        background: #ffffff;
        border: 1px solid #e5e9ef;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 1px 4px rgba(0,0,0,.06);
    }

    .card-title {
        font-weight: 700;
        font-size: 1rem;
        color: #1a2e40;
        margin-bottom: 0.4rem;
    }

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

    .badge-green {
        background: #dcfce7;
        color: #15803d;
    }

    .badge-amber {
        background: #fef9c3;
        color: #92400e;
    }

    .bloque {
        background: #f4f8fc;
        border-left: 3px solid #0d7c9e;
        border-radius: 0 8px 8px 0;
        padding: 0.55rem 0.8rem;
        margin-bottom: 0.45rem;
    }

    .bloque-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: #0d7c9e;
        text-transform: uppercase;
    }

    .bloque-subtipo {
        font-weight: 600;
        color: #1a2e40;
        font-size: 0.87rem;
    }

    .bloque-contenido {
        color: #374151;
        font-size: 0.87rem;
    }

    .disclaimer {
        background: #fffbeb;
        border: 1px solid #fcd34d;
        border-radius: 8px;
        padding: 0.55rem 0.8rem;
        margin-top: 0.6rem;
        font-size: 0.78rem;
        color: #78350f;
    }

    .no-results {
        text-align: center;
        color: #9ca3af;
        padding: 2rem 1rem;
        font-size: 0.9rem;
    }
    </style>
    """), unsafe_allow_html=True)


# ─────────────────────────────────────────────
# BLOQUES HTML
# ─────────────────────────────────────────────

def build_bloque(bloque_tipo, subtipo, contenido, fuente):
    fuente_html = (
        f'<br><small style="color:#9ca3af">Fuente: {fuente}</small>'
        if fuente else ""
    )

    return (
        '<div class="bloque">'
        f'<div class="bloque-label">{bloque_tipo}</div>'
        f'<div class="bloque-subtipo">{subtipo}</div>'
        f'<div class="bloque-contenido">{contenido}{fuente_html}</div>'
        '</div>'
    )


def build_disclaimer(web, ultima_act):
    web_link = f' · <a href="{web}" target="_blank">Web oficial</a>' if web else ""

    if pd.notna(ultima_act) and ultima_act:
        try:
            fecha_act = pd.to_datetime(ultima_act).strftime("%d/%m/%Y")
            act_str = f" · Última actualización: <strong>{fecha_act}</strong>"
        except Exception:
            act_str = ""
    else:
        act_str = ""

    return (
        '<div class="disclaimer">'
        '<strong>Aviso:</strong> Esta información puede estar desactualizada. '
        'Contrástala con la fuente oficial antes de usarla.'
        f'{web_link}{act_str}'
        '</div>'
    )


def build_resena(r_stars, guia, fecha_str, n_p, comentario):
    return (
        '<div style="border-top:1px solid #e5e9ef;'
        'padding-top:0.5rem;margin-top:0.5rem;">'
        f'<div style="font-size:0.78rem;color:#6b7a8d;">'
        f'{r_stars} · {guia} · {fecha_str} · {n_p} pax'
        '</div>'
        f'<div style="font-size:0.85rem;color:#374151;margin-top:0.2rem;">'
        f'{comentario}'
        '</div>'
        '</div>'
    )


# ─────────────────────────────────────────────
# IDENTIFICACIÓN SIMPLE
# ─────────────────────────────────────────────

def pedir_nombre_guia():
    if "guia" not in st.session_state:
        st.session_state.guia = ""

    st.session_state.guia = st.text_input(
        "Nombre del guía",
        value=st.session_state.guia,
        placeholder="Nombre y apellidos"
    )

    if not st.session_state.guia.strip():
        st.info("Indica tu nombre para poder enviar incidencias, propuestas o reseñas.")


# ─────────────────────────────────────────────
# FORMULARIOS
# ─────────────────────────────────────────────

def formulario_incidencia(tipo, categoria, nombre, municipio=""):
    with st.expander("Reportar dato incorrecto", expanded=False):
        with st.form(f"form_{tipo}_{categoria}_{nombre}"):

            descripcion = st.text_area(
                "¿Qué dato es incorrecto o falta?",
                placeholder="Ejemplo: el horario ha cambiado, el precio ya no es correcto o falta indicar el cierre semanal."
            )

            enviar = st.form_submit_button("Enviar")

            if enviar:
                if not st.session_state.get("guia", "").strip():
                    st.warning("Indica primero tu nombre.")
                    return

                if not descripcion.strip():
                    st.warning("Describe brevemente el problema.")
                    return

                try:
                    save_incidencia({
                        "tipo": tipo,
                        "categoria": categoria,
                        "nombre": nombre,
                        "municipio": municipio,
                        "asunto": f"Corrección de {tipo}: {nombre}",
                        "descripcion": descripcion,
                    })

                    st.success("Incidencia registrada correctamente.")

                except Exception as e:
                    st.error(f"No se pudo registrar la incidencia: {e}")


def formulario_nuevo_recurso():
    with st.expander("Proponer nuevo recurso turístico", expanded=False):
        with st.form("form_nuevo_recurso"):

            nombre = st.text_input("Nombre del recurso")
            municipio = st.text_input("Municipio")
            descripcion = st.text_area(
                "Información básica",
                placeholder="Indica por qué debe añadirse, web oficial si la conoces, horarios o cualquier dato útil."
            )

            enviar = st.form_submit_button("Enviar")

            if enviar:
                if not st.session_state.get("guia", "").strip():
                    st.warning("Indica primero tu nombre.")
                    return

                if not nombre.strip():
                    st.warning("El nombre del recurso es obligatorio.")
                    return

                try:
                    save_incidencia({
                        "tipo": "recurso",
                        "categoria": "nuevo",
                        "nombre": nombre,
                        "municipio": municipio,
                        "asunto": f"Nuevo recurso turístico: {nombre}",
                        "descripcion": descripcion,
                    })

                    st.success("Propuesta registrada correctamente.")

                except Exception as e:
                    st.error(f"No se pudo registrar la propuesta: {e}")


def formulario_nuevo_restaurante():
    with st.expander("Proponer nuevo restaurante", expanded=False):
        with st.form("form_nuevo_restaurante"):

            nombre = st.text_input("Nombre del restaurante")
            municipio = st.text_input("Municipio")
            descripcion = st.text_area(
                "Información básica",
                placeholder="Indica si admite grupos, precio aproximado, experiencia con grupos o cualquier dato útil."
            )

            enviar = st.form_submit_button("Enviar")

            if enviar:
                if not st.session_state.get("guia", "").strip():
                    st.warning("Indica primero tu nombre.")
                    return

                if not nombre.strip():
                    st.warning("El nombre del restaurante es obligatorio.")
                    return

                try:
                    save_incidencia({
                        "tipo": "restaurante",
                        "categoria": "nuevo",
                        "nombre": nombre,
                        "municipio": municipio,
                        "asunto": f"Nuevo restaurante: {nombre}",
                        "descripcion": descripcion,
                    })

                    st.success("Propuesta registrada correctamente.")

                except Exception as e:
                    st.error(f"No se pudo registrar la propuesta: {e}")


def formulario_nueva_resena_restaurante(nombre, municipio=""):
    with st.expander("Añadir reseña", expanded=False):
        with st.form(f"form_resena_{nombre}"):

            fecha_visita = st.date_input(
                "Fecha",
                value=date.today(),
                format="DD/MM/YYYY"
            )

            n_personas = st.number_input(
                "Personas",
                min_value=1,
                step=1
            )

            precio = st.text_input(
                "Precio por persona",
                placeholder="Ejemplo: 22"
            )

            rating = st.slider(
                "Valoración",
                min_value=1,
                max_value=5,
                value=4
            )

            comentario = st.text_area(
                "Comentario",
                placeholder="Breve valoración de la experiencia."
            )

            enviar = st.form_submit_button("Guardar reseña")

            if enviar:
                if not st.session_state.get("guia", "").strip():
                    st.warning("Indica primero tu nombre.")
                    return

                if not comentario.strip():
                    st.warning("El comentario es obligatorio.")
                    return

                try:
                    save_resena_restaurante({
                        "restaurante": nombre,
                        "fecha": fecha_visita.strftime("%d/%m/%Y"),
                        "num_personas": int(n_personas),
                        "precio_por_persona": precio,
                        "rating": int(rating),
                        "comentario": comentario,
                    })

                    st.success("Reseña registrada correctamente.")
                    st.cache_data.clear()

                except Exception as e:
                    st.error(f"No se pudo registrar la reseña: {e}")


# ─────────────────────────────────────────────
# MÓDULO RECURSOS
# ─────────────────────────────────────────────

def modulo_recursos(dfs):
    recursos_df = dfs["recursos"]
    contenidos_df = dfs["contenidos_recursos"]

    hoy = date.today()
    fecha_max = date(hoy.year + 2, hoy.month, hoy.day)

    col_fecha, col_muni = st.columns([1, 1])

    with col_fecha:
        fecha_sel = st.date_input(
            "Consultar fecha",
            value=hoy,
            min_value=hoy,
            max_value=fecha_max,
            format="DD/MM/YYYY",
            key="rec_fecha",
        )

    with col_muni:
        municipios = ["Todos"] + sorted(recursos_df["municipio"].dropna().unique())
        muni = st.selectbox("Municipio", municipios, key="rec_muni")

    df_fil = recursos_df.copy()

    if "activo" in df_fil.columns:
        df_fil = df_fil[df_fil["activo"] == True]

    if muni != "Todos":
        df_fil = df_fil[df_fil["municipio"] == muni]

    if "prioridad" in df_fil.columns:
        df_fil = df_fil.sort_values(["prioridad", "recurso"])
    else:
        df_fil = df_fil.sort_values("recurso")

    formulario_nuevo_recurso()

    if df_fil.empty:
        st.markdown(
            '<div class="no-results">No hay recursos para los filtros seleccionados.</div>',
            unsafe_allow_html=True
        )
        return

    st.markdown(f"**{len(df_fil)} recurso(s) encontrado(s)**")

    for _, rec in df_fil.iterrows():
        nombre = rec["recurso"]
        municipio = rec.get("municipio", "")
        tipo_rec = rec.get("tipo", "")
        web = rec.get("web_oficial", "")
        ultima_act = rec.get("ultima_actualizacion", None)

        contenido_fecha = filtrar_contenido(contenidos_df, nombre, fecha_sel)

        if not contenido_fecha.empty:
            bloques_html = ""

            for bloque_tipo, grupo in contenido_fecha.groupby("bloque"):
                for _, fila in grupo.iterrows():
                    bloques_html += build_bloque(
                        bloque_tipo,
                        fila.get("subtipo", "") or "",
                        fila.get("contenido", "") or "",
                        fila.get("fuente", "") or "",
                    )
        else:
            bloques_html = (
                '<small style="color:#9ca3af">'
                'Sin datos disponibles para la fecha seleccionada.'
                '</small>'
            )

        web_str = str(web) if pd.notna(web) else ""

        st.markdown(f"""
        <div class="card">
            <div class="card-title">🏛️ {nombre}</div>
            <div>
                <span class="badge">{municipio}</span>
                <span class="badge badge-amber">{tipo_rec}</span>
            </div>
            {bloques_html}
            {build_disclaimer(web_str, ultima_act)}
        </div>
        """, unsafe_allow_html=True)

        formulario_incidencia(
            tipo="recurso",
            categoria="correccion",
            nombre=nombre,
            municipio=municipio
        )


# ─────────────────────────────────────────────
# MÓDULO RESTAURANTES
# ─────────────────────────────────────────────

def modulo_restaurantes(dfs):
    rest_df = dfs["restaurantes"]
    exp_df = dfs["experiencias_restaurantes"]

    if not exp_df.empty and "rating" in exp_df.columns:
        rating_medio = (
            exp_df.groupby("restaurante")["rating"]
            .agg(rating_medio="mean", n_resenas="count")
            .reset_index()
        )
        rest_df = rest_df.merge(rating_medio, on="restaurante", how="left")
    else:
        rest_df["rating_medio"] = None
        rest_df["n_resenas"] = 0

    municipios = ["Todos"] + sorted(rest_df["municipio"].dropna().unique())
    muni = st.selectbox("Municipio", municipios, key="rest_muni")

    df_fil = rest_df.copy()

    if muni != "Todos":
        df_fil = df_fil[df_fil["municipio"] == muni]

    df_fil = df_fil.sort_values(
        "rating_medio",
        ascending=False,
        na_position="last"
    )

    formulario_nuevo_restaurante()

    if df_fil.empty:
        st.markdown(
            '<div class="no-results">No hay restaurantes para los filtros seleccionados.</div>',
            unsafe_allow_html=True
        )
        return

    st.markdown(f"**{len(df_fil)} restaurante(s) encontrado(s)**")

    for _, row in df_fil.iterrows():
        nombre = row["restaurante"]
        municipio = row.get("municipio", "")
        grupos = row.get("admite_grupos", "")
        precio = row.get("precio_menu_grupos", None)
        rating = row.get("rating_medio", None)
        n_res = int(row.get("n_resenas", 0)) if pd.notna(row.get("n_resenas")) else 0

        if pd.notna(rating):
            estrellas = int(round(rating))
            stars_str = "⭐" * estrellas + "☆" * (5 - estrellas)
            rating_html = (
                f'<span>{stars_str}</span> '
                f'<strong>{rating:.1f}/5</strong> '
                f'<small style="color:#9ca3af">({n_res} reseña(s))</small>'
            )
        else:
            rating_html = '<small style="color:#9ca3af">Sin reseñas aún</small>'

        precio_html = (
            f'<span class="badge badge-green">Menú grupo: {precio} €/p.</span>'
            if pd.notna(precio) else ""
        )

        grupos_badge = (
            '<span class="badge badge-green">Grupos</span>'
            if str(grupos).upper() in ["SÍ", "SI", "YES"]
            else ""
        )

        resenas = exp_df[exp_df["restaurante"] == nombre].copy()

        if "fecha" in resenas.columns:
            resenas["fecha"] = pd.to_datetime(resenas["fecha"], errors="coerce")
            resenas = resenas.sort_values("fecha", ascending=False)

        resenas_html = ""

        for _, res in resenas.head(3).iterrows():
            fecha_str = (
                pd.to_datetime(res["fecha"]).strftime("%d/%m/%Y")
                if pd.notna(res.get("fecha"))
                else ""
            )

            r_stars = "⭐" * int(res.get("rating", 0))

            resenas_html += build_resena(
                r_stars,
                res.get("guia", ""),
                fecha_str,
                res.get("num_personas", ""),
                res.get("comentario", ""),
            )

        if not resenas_html:
            resenas_html = '<small style="color:#9ca3af">Sin reseñas registradas.</small>'

        st.markdown(f"""
        <div class="card">
            <div class="card-title">🍽️ {nombre}</div>
            <div>
                <span class="badge">{municipio}</span>
                {grupos_badge}
                {precio_html}
            </div>
            <div style="margin-top:0.5rem;margin-bottom:0.5rem;">
                {rating_html}
            </div>
            {resenas_html}
        </div>
        """, unsafe_allow_html=True)

        formulario_incidencia(
            tipo="restaurante",
            categoria="correccion",
            nombre=nombre,
            municipio=municipio
        )

        formulario_nueva_resena_restaurante(
            nombre=nombre,
            municipio=municipio
        )


# ─────────────────────────────────────────────
# APP PRINCIPAL
# ─────────────────────────────────────────────

def main():
    inject_css()

    st.markdown(html("""
    <div style="text-align:center;padding:1.2rem 0 0.5rem;">
        <div style="font-size:2rem;">🏔️</div>
        <div style="font-weight:700;font-size:1.35rem;color:#1a2e40;">
            CMS Cantabria
        </div>
        <div style="color:#6b7a8d;font-size:0.82rem;margin-top:0.2rem;">
            Panel de Guías Turísticos
        </div>
    </div>
    """), unsafe_allow_html=True)

    pedir_nombre_guia()

    try:
        with st.spinner("Cargando datos…"):
            dfs = load_data()

    except Exception as e:
        st.error(f"No se pudieron cargar los datos: {e}")
        return

    col_ref, _ = st.columns([1, 3])

    with col_ref:
        if st.button("Actualizar datos"):
            st.cache_data.clear()
            st.rerun()

    st.divider()

    tab_rec, tab_rest = st.tabs(["Recursos", "Restaurantes"])

    with tab_rec:
        st.markdown(
            '<div class="section-header">Recursos Turísticos</div>',
            unsafe_allow_html=True
        )
        modulo_recursos(dfs)

    with tab_rest:
        st.markdown(
            '<div class="section-header">Restaurantes</div>',
            unsafe_allow_html=True
        )
        modulo_restaurantes(dfs)

    st.markdown(
        '<div style="text-align:center;color:#9ca3af;'
        'font-size:0.72rem;margin-top:2rem;padding-bottom:1rem;">'
        'CMS Cantabria · Datos actualizados desde Google Sheets'
        '</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
