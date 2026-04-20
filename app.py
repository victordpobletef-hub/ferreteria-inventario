import streamlit as st
import pandas as pd

# 1. Configuración de la App
st.set_page_config(page_title="Ferretería Universal", layout="wide")

# 2. Función de carga ultra rápida (Lee el CSV publicado)
def cargar_datos():
    try:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        # Cargamos directamente el CSV desde el link de publicación
        df = pd.read_csv(url)
        # Limpiamos nombres de columnas por si acaso
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al conectar con el inventario: {e}")
        return None

# 3. Sistema de Login
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acceso - Ferretería Universal")
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
    st.sidebar.title("🛠️ Menú")
    menu = st.sidebar.radio("Ir a:", ["Inventario", "Ventas", "Usuarios"])

    df = cargar_datos()

    if df is not None:
        if menu == "Inventario":
            st.header("📦 Inventario en Tiempo Real")
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.info("💡 Para añadir o editar productos, hazlo en tu Google Sheet y los cambios se verán aquí al refrescar.")

        elif menu == "Ventas":
            st.header("🛒 Registro de Ventas")
            # Selector dinámico basado en tu Excel
            if 'Nombre' in df.columns:
                lista_prod = df['Nombre'].tolist()
                seleccion = st.selectbox("Producto a vender:", lista_prod)
                cantidad = st.number_input("Cantidad:", min_value=1, value=1)
                
                if st.button(f"Confirmar Venta de {seleccion}"):
                    st.success(f"Venta registrada localmente: {cantidad} unidad(es) de {seleccion}")
                    st.warning("Nota: Por ahora, descuenta el stock manualmente en tu Google Sheet.")
            else:
                st.error("No se encontró la columna 'Nombre' en el Excel.")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
