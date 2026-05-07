import streamlit as st
import pandas as pd
from datetime import date
import os

# Configuración de la página
st.set_page_config(page_title="Control de Obra Eléctrica", layout="wide")

st.title("⚡ Seguimiento de Obra - Electricista")

# Archivo de base de datos local (CSV)
DB_FILE = "registro_obras.csv"

# Función para cargar datos
def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Fecha", "Obra", "Tarea", "Estado"])

df = cargar_datos()

# --- FORMULARIO DE ENTRADA ---
with st.sidebar:
    st.header("Registrar Nueva Tarea")
    with st.form("form_tarea"):
        fecha = st.date_input("Fecha", date.today())
        obra = st.text_input("Nombre de la Obra/Cliente")
        tarea = st.selectbox("Tarea Realizada", [
            "Cableado", "Montaje de Cuadros", "Instalación de Mecanismos", 
            "Rozas y Tubos", "Pruebas de Continuidad", "Acometida"
        ])
        estado = st.radio("Estado", ["Pendiente", "En Proceso", "Finalizado"])
        
        btn_guardar = st.form_submit_button("Guardar Tarea")

if btn_guardar:
    nueva_fila = pd.DataFrame([[fecha, obra, tarea, estado]], columns=df.columns)
    df = pd.concat([df, nueva_fila], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.success("¡Tarea guardada con éxito!")

# --- VISUALIZACIÓN ---
st.subheader("📋 Historial de Trabajos")
st.dataframe(df, use_container_width=True)

# Métricas rápidas
col1, col2 = st.columns(2)
col1.metric("Total Tareas", len(df))
col2.metric("Finalizadas", len(df[df["Estado"] == "Finalizado"]))
