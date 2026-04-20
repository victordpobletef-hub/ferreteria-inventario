import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de la App
st.set_page_config(page_title="Ferretería Pro", layout="wide")

# 2. Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Login
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acceso al Sistema")
    user = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if user == "admin" and clave == "1234":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
else:
    st.sidebar.title("🛠️ Ferretería Universal")
    menu = st.sidebar.radio("Menú", ["Inventario", "Ventas", "Usuarios"])

    # Cargar datos de la hoja "Productos"
    try:
        df = conn.read(worksheet="Productos", ttl=0) # ttl=0 para que no use caché y sea rápido
    except:
        st.error("No se pudo leer la hoja 'Productos'. Revisa el nombre de la pestaña en Google Sheets.")
        st.stop()

    if menu == "Inventario":
        st.header("📦 Control de Inventario")
        st.dataframe(df, use_container_width=True)
        
        with st.expander("➕ Agregar nuevo producto"):
            with st.form("nuevo"):
                nom = st.text_input("Nombre del Item")
                pre = st.number_input("Precio", min_value=0.0)
                sto = st.number_input("Stock", min_value=0)
                if st.form_submit_button("Guardar en Nube"):
                    new_row = pd.DataFrame([{"ID": len(df)+1, "Nombre": nom, "Precio": pre, "Stock": sto}])
                    df_updated = pd.concat([df, new_row], ignore_index=True)
                    conn.update(worksheet="Productos", data=df_updated)
                    st.success("¡Producto Guardado!")
                    st.rerun()

    elif menu == "Ventas":
        st.header("🛒 Registrar Venta")
        # Selector de producto dinámico desde tu lista real
        prod_lista = df['Nombre'].tolist()
        seleccion = st.selectbox("Selecciona producto para vender:", prod_lista)
        
        if st.button(f"Vender 1 unidad de {seleccion}"):
            # Lógica para descontar stock
            df.loc[df['Nombre'] == seleccion, 'Stock'] -= 1
            conn.update(worksheet="Productos", data=df)
            st.success(f"Venta registrada: {seleccion} (-1)")
            st.rerun()

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
