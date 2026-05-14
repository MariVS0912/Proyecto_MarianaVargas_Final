import streamlit as st
import pandas as pd
from influxdb_client import InfluxDBClient
import plotly.express as px

# =====================================================
# CONFIGURACIÓN STREAMLIT
# =====================================================

st.set_page_config(
    page_title="Weather Mood Window",
    layout="wide"
)

# =====================================================
# ESTILOS CSS
# =====================================================

st.markdown("""
<style>

.stApp {
    background-color: #0b1220;
    color: white;
}

.big-title {
    font-size: 50px;
    font-weight: bold;
    color: #7dd3fc;
}

.mood-box {
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 20px;
    color: white;
}

.metric-card {
    background-color: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# TÍTULO
# =====================================================

st.markdown(
    '<p class="big-title">🌧️ Weather Mood Window</p>',
    unsafe_allow_html=True
)

st.write(
    "Sistema interactivo de visualización emocional del ambiente en tiempo real"
)

# =====================================================
# DATOS INFLUXDB
# =====================================================

INFLUXDB_URL =  "https://us-east-1-1.aws.cloud2.influxdata.com/"
INFLUXDB_TOKEN = "JoKdx3OFaBCFPmYQgiVWE8hjrtJ0lDkjwWZzT9djWJlvg98rtTgF9iRgKhQtAkKIA2UQsU6zsrJlv1BH6lfsVw=="
INFLUXDB_ORG = "miguelcmo"
INFLUXDB_BUCKET = "iot_telemetry_data"

client = InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)

query_api = client.query_api()

query = f'''
from(bucket: "{INFLUXDB_BUCKET}")
  |> range(start: -1h)
'''

result = query_api.query_data_frame(query)

# =====================================================
# VALIDACIÓN
# =====================================================

if len(result) == 0:
    st.warning("No hay datos disponibles")
    st.stop()

# =====================================================
# LIMPIEZA DE DATOS
# =====================================================

if isinstance(result, list):
    df = pd.concat(result)
else:
    df = result

if '_field' not in df.columns:
    st.warning("No se encontraron datos válidos")
    st.stop()

pivot_df = df.pivot_table(
    index='_time',
    columns='_field',
    values='_value',
    aggfunc='mean'
).reset_index()

pivot_df = pivot_df.dropna()

# =====================================================
# VARIABLES ACTUALES
# =====================================================

latest = pivot_df.iloc[-1]

temperature = latest['temperature']
humidity = latest['humidity']

accel = (
    abs(latest['accelX']) +
    abs(latest['accelY']) +
    abs(latest['accelZ'])
)

# =====================================================
# ESTADO EMOCIONAL
# =====================================================

if accel > 20:
    mood = "⛈️ CAÓTICO"
    background = "#3b0a0a"

elif humidity > 80:
    mood = "🌫️ NOSTÁLGICO"
    background = "#1e293b"

elif temperature > 30:
    mood = "🔥 INTENSO"
    background = "#451a03"

else:
    mood = "🌌 RELAJADO"
    background = "#0f172a"

# =====================================================
# PANEL PRINCIPAL
# =====================================================

st.markdown(
    f"""
    <div class="mood-box" style="background:{background};">
        <h1>{mood}</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================
# MÉTRICAS
# =====================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🌡️ Temperatura",
        f"{temperature:.2f} °C"
    )

with col2:
    st.metric(
        "💧 Humedad",
        f"{humidity:.2f} %"
    )

with col3:
    st.metric(
        "⚡ Movimiento",
        f"{accel:.2f}"
    )

# =====================================================
# ALERTAS
# =====================================================

if temperature > 30:
    st.error("🔥 Alta temperatura detectada")

if humidity > 80:
    st.warning("🌫️ Humedad elevada")

if accel > 20:
    st.error("⚡ Movimiento brusco detectado")

# =====================================================
# GRÁFICA TEMPERATURA
# =====================================================

st.subheader("📈 Temperatura")

fig_temp = px.line(
    pivot_df,
    x='_time',
    y='temperature'
)

st.plotly_chart(
    fig_temp,
    use_container_width=True
)

# =====================================================
# GRÁFICA HUMEDAD
# =====================================================

st.subheader("💧 Humedad")

fig_hum = px.line(
    pivot_df,
    x='_time',
    y='humidity'
)

st.plotly_chart(
    fig_hum,
    use_container_width=True
)

# =====================================================
# MOVIMIENTO
# =====================================================

pivot_df['movement'] = (
    abs(pivot_df['accelX']) +
    abs(pivot_df['accelY']) +
    abs(pivot_df['accelZ'])
)

st.subheader("⚡ Intensidad de Movimiento")

fig_mov = px.area(
    pivot_df,
    x='_time',
    y='movement'
)

st.plotly_chart(
    fig_mov,
    use_container_width=True
)

# =====================================================
# ATMÓSFERA VISUAL
# =====================================================

st.subheader("🌦️ Estado del Ambiente")

if mood == "⛈️ CAÓTICO":
    st.markdown("## ⚡ Tormenta digital activa")

elif mood == "🌫️ NOSTÁLGICO":
    st.markdown("## 🌧️ Ambiente húmedo y neblinoso")

elif mood == "🔥 INTENSO":
    st.markdown("## ☀️ Temperatura elevada")

else:
    st.markdown("## 🌌 Ambiente tranquilo")
