import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de la App
st.set_page_config(page_title="Ferretería Pro", layout="wide")

# 2. Conexión a tu Google Drive
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Sistema de Login Simple
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acceso al Sistema")
    user = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if user == "admin" and clave == "1234": # Aquí puedes validar con tu tabla de usuarios
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
else:
    # --- INTERFAZ PRINCIPAL ---
    st.sidebar.title("🛠️ Ferretería Universal")
    menu = st.sidebar.radio("Menú", ["Inventario", "Ventas", "Usuarios", "Configuración"])

    if menu == "Inventario":
        st.header("📦 Control de Inventario")
        df = conn.read(worksheet="Productos")
        st.dataframe(df, use_container_width=True)
        
        with st.expander("➕ Agregar nuevo producto"):
            with st.form("nuevo"):
                nom = st.text_input("Nombre del Item")
                pre = st.number_input("Precio", min_value=0.0)
                sto = st.number_input("Stock", min_value=0)
                if st.form_submit_button("Guardar en Nube"):
                    # Aquí el código para escribir en Google Sheets
                    st.success("¡Guardado instantáneo!")

    elif menu == "Ventas":
        st.header("🛒 Registrar Venta")
        # Botones rápidos para vender
        col1, col2 = st.columns(2)
        with col1:
            st.button("Vender Martillo (-1)")
            st.button("Vender Clavos x1kg (-1)")

    elif menu == "Usuarios":
        st.header("👥 Gestión de Personal")
        st.write("Aquí puedes agregar o quitar permisos a tus empleados.")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
