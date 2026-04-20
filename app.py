import streamlit as st
import pandas as pd

# 1. Configuración de la App
st.set_page_config(page_title="Ferretería Pro", layout="wide")

# 2. Función para leer datos directamente (Más rápido y sin errores)
def cargar_datos():
    url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    # Forzamos la lectura como CSV para evitar bloqueos de Google
    csv_url = url.replace("/edit#gid=", "/export?format=csv&gid=")
    if "/export" not in csv_url:
        csv_url = url.split("/edit")[0] + "/export?format=csv"
    
    df = pd.read_csv(csv_url)
    df.columns = df.columns.str.strip() # Limpia espacios en títulos
    return df

# 3. Sistema de Login
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acceso al Sistema - Ferretería Universal")
    user = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if user == "admin" and clave == "1234":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
else:
    # --- INTERFAZ PRINCIPAL ---
    st.sidebar.title("🛠️ Menú Principal")
    menu = st.sidebar.radio("Ir a:", ["Inventario", "Ventas", "Usuarios"])

    # Carga de datos inicial
    try:
        df = cargar_datos()
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.stop()

    if menu == "Inventario":
        st.header("📦 Control de Inventario")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        with st.expander("➕ Agregar nuevo producto"):
            st.info("Para agregar productos, por ahora edita directamente tu Google Sheet. Pronto añadiremos el botón de guardado automático.")

    elif menu == "Ventas":
        st.header("🛒 Registrar Venta")
        # Selector dinámico
        productos = df['Nombre'].tolist()
        seleccion = st.selectbox("Selecciona producto:", productos)
        
        if st.button(f"Registrar Venta de {seleccion}"):
            st.warning("⚠️ Función de escritura en desarrollo. Por ahora, registra la venta y descuenta en tu Excel manualmente.")
            st.write(f"Venta confirmada: 1 unidad de {seleccion}")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
