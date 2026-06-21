# CMS Turístico de Cantabria 🏔️

Panel para guías turísticos con datos en tiempo real desde Google Sheets.

## Estructura del proyecto

```
cms_cantabria/
├── app.py               ← Aplicación principal Streamlit
├── requirements.txt     ← Dependencias Python
└── README.md
```

---

## 1 · Preparar Google Sheets

1. Abre tu Google Sheets con las 4 hojas:
   - `recursos`
   - `contenidos-recursos`
   - `restaurantes`
   - `experiencias_restaurantes`

2. **Publica el documento**: Archivo → Compartir → Publicar en la web → selecciona *Toda la hoja de cálculo* → formato CSV → Publicar.

3. Copia el **ID** de la URL de tu Sheet:
   ```
   https://docs.google.com/spreadsheets/d/<<ESTE_ES_EL_ID>>/edit
   ```

4. En `app.py`, reemplaza la línea:
   ```python
   SHEET_ID = "TU_GOOGLE_SHEET_ID"
   ```
   con tu ID real.

---

## 2 · Prueba local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run app.py
```

> Si `SHEET_ID` no está configurado, la app carga automáticamente el fichero local `recursos_y_restaurantes.xlsx` (útil para desarrollo).

---

## 3 · Subir a GitHub

```bash
# Desde la carpeta del proyecto
git init
git add .
git commit -m "feat: CMS Cantabria inicial"

# Crear repo en github.com y enlazar
git remote add origin https://github.com/TU_USUARIO/cms-cantabria.git
git branch -M main
git push -u origin main
```

---

## 4 · Desplegar en Streamlit Cloud

1. Ve a **[share.streamlit.io](https://share.streamlit.io)** e inicia sesión con GitHub.
2. Pulsa **"New app"**.
3. Selecciona el repositorio `cms-cantabria`, rama `main`, archivo `app.py`.
4. Pulsa **"Deploy"** → en ~2 minutos tendrás la URL pública.

### Variables de entorno (opcional)
Si quieres mantener el `SHEET_ID` fuera del código:

- En Streamlit Cloud: **App settings → Secrets**:
  ```toml
  SHEET_ID = "1abc...xyz"
  ```
- En `app.py` léelo con:
  ```python
  SHEET_ID = st.secrets.get("SHEET_ID", "TU_GOOGLE_SHEET_ID")
  ```

---

## Lógica de temporada

| Temporada | Meses          |
|-----------|----------------|
| Alta      | Jun · Jul · Ago · Sep |
| Media     | Abr · May · Oct |
| Baja      | Ene · Feb · Mar · Nov · Dic |

El filtrado de contenidos combina:
- Rango `fecha_inicio` – `fecha_fin` de cada fila
- Campo `dias_semana` (ej: `lunes-martes-miércoles`)

Solo se muestran las filas que aplican a **hoy**.
