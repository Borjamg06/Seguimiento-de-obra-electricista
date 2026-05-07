import streamlit as st
import pandas as pd
from datetime import date
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
import io

# --- CONFIGURACIÓN Y LOGO ---
st.set_page_config(page_title="Seguimiento de Obra - Electricista", layout="centered")
# Nota: Asegúrate de tener una imagen llamada 'logo_empresa.png' en tu GitHub 
# st.image("logo_empresa.png", width=200) 
st.title("🏗️ Seguimiento de Obra")

# --- LISTADO DE TAREAS [cite: 11-23, 29-33] ---
tareas_electricidad = [
    "Trazado y marcado de cajas, tubos y cuadros", "Ejecución rozas en paredes y techos",
    "Montaje de soportes", "Colocación tubos y conductos", "Tendido de cables",
    "Identificación y etiquetado", "Conexionado de cables en bornes o regletas",
    "Instalación y conexionado de mecanismos", "Fijación de carril DIN y mecanismos en cuadro",
    "Cableado interno del cuadro eléctrico", "Configuración de equipos domóticos",
    "Conexionado de sensores/actuadores", "Pruebas de continuidad",
    "Pruebas de aislamiento", "Verificación de tierras", "Programación del automatismo",
    "Pruebas de funcionamiento"
]

# --- ESTADOS DE AVANCE [cite: 34-40] ---
estados_avance = [
    "Avance de la tarea en torno al 25% aprox.",
    "Avance de la tarea en torno al 50% aprox.",
    "Avance de la tarea en torno al 75% aprox.",
    "OK, finalizado sin errores",
    "Finalizado, pero con errores pendientes de corregir",
    "Finalizado y corregidos los errores"
]

# --- FORMULARIO DE ENTRADA [cite: 41, 42] ---
with st.form("registro_obra"):
    nombre_trabajador = st.text_input("Nombre del Trabajador")
    fecha_envio = st.date_input("Fecha del informe", value=date.today())
    tarea_seleccionada = st.selectbox("Selecciona la tarea realizada:", tareas_electricidad)
    estado_seleccionado = st.selectbox("Estado de la tarea:", estados_avance)
    
    submit_button = st.form_submit_button("Registrar Tarea")

# --- GESTIÓN DE DATOS (EXCEL) [cite: 43] ---
if "datos_obra" not in st.session_state:
    st.session_state.datos_obra = pd.DataFrame(columns=["Fecha", "Trabajador", "Tarea", "Estado"])

if submit_button:
    nuevo_registro = {
        "Fecha": fecha_envio,
        "Trabajador": nombre_trabajador,
        "Tarea": tarea_seleccionada,
        "Estado": estado_seleccionado
    }
    st.session_state.datos_obra = pd.concat([st.session_state.datos_obra, pd.DataFrame([nuevo_registro])], ignore_index=True)
    st.success("¡Registro añadido con éxito!")

# Mostrar tabla actual
st.subheader("Registros actuales")
st.dataframe(st.session_state.datos_obra)

# --- EXPORTACIÓN Y ENVÍO POR EMAIL ---
if not st.session_state.datos_obra.empty:
    # 1. Crear el Excel en memoria
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        st.session_state.datos_obra.to_excel(writer, index=False, sheet_name='Seguimiento')
    excel_data = output.getvalue()

    # 2. Botón para descargar (con key para evitar errores)
    st.download_button(
        label="📥 Descargar Excel",
        data=excel_data,
        file_name=f"seguimiento_{date.today()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="boton_descarga_excel"
    )

    # 3. Botón para enviar por correo
    if st.button("📧 Enviar Excel por Correo", key="boton_enviar_email"):
        try:
            email_user = st.secrets["email"]["usuario"]
            email_password = st.secrets["email"]["password"]
            email_destinatario = st.secrets["email"]["destinatario"]

            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = email_destinatario
            msg['Subject'] = f"Reporte de Obra - {nombre_trabajador}"

            msg.attach(MIMEText(f"Envío de informe de: {nombre_trabajador}", 'plain'))
            
            part = MIMEApplication(excel_data, Name="seguimiento.xlsx")
            part['Content-Disposition'] = 'attachment; filename="seguimiento.xlsx"'
            msg.attach(part)

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email_user, email_password)
            server.send_message(msg)
            server.quit()

            st.success("✅ ¡Correo enviado con éxito a la profesora!")
        except Exception as e:
            st.error(f"Error al enviar: {e}")
