def formulario_incidencia(tipo, categoria, nombre, municipio=""):
    with st.expander("Reportar dato incorrecto", expanded=False):
        with st.form(f"form_{tipo}_{categoria}_{nombre}"):

            guia = st.text_input("Nombre del guía", placeholder="Nombre y apellidos")

            descripcion = st.text_area(
                "¿Qué dato es incorrecto o falta?",
                placeholder="Ejemplo: el horario ha cambiado, el precio ya no es correcto o falta indicar el cierre semanal."
            )

            enviar = st.form_submit_button("Enviar")

            if enviar:
                if not guia.strip():
                    st.warning("Indica tu nombre.")
                    return

                if not descripcion.strip():
                    st.warning("Describe brevemente el problema.")
                    return

                try:
                    save_incidencia({
                        "usuario_nombre": guia,
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
