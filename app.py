import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="Ferretería Universal", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 2. FUNCIONES DE LÓGICA (EL "CEREBRO")
# ==========================================

def cargar_inventario():
    """Trae los datos de la pestaña Inventario"""
    try:
        df = conn.read(worksheet="Inventario")
        df = df.iloc[:, :4] 
        df.columns = ['ID', 'Nombre', 'Precio', 'Stock']
        return df.dropna(subset=['Nombre'])
    except Exception as e:
        st.error(f"Error cargando inventario: {e}")
        return None

def registrar_nuevo_usuario(user, clave, rol):
    """Guarda un usuario en la pestaña Usuarios"""
    try:
        df_actual = conn.read(worksheet="Usuarios")
        nueva_fila = pd.DataFrame([{"Usuario": user, "Clave": clave, "Rol": rol}])
        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
        conn.update(worksheet="Usuarios", data=df_final)
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False
        
def validar_login(user, clave):
    """Busca en el Excel si el usuario y clave existen"""
    try:
        df_usuarios = conn.read(worksheet="Usuarios")
        # Buscamos coincidencia exacta de usuario y clave
        # Convertimos a string para evitar errores con números
        filtro = df_usuarios[(df_usuarios['Usuario'].astype(str) == str(user)) & 
                             (df_usuarios['Clave'].astype(str) == str(clave))]
        
        if not filtro.empty:
            # Guardamos el rol en la sesión para usarlo después
            st.session_state.rol = filtro.iloc[0]['Rol']
            return True
        return False
    except Exception as e:
        st.error(f"Error al validar acceso: {e}")
        return False

# ==========================================
# 3. COMPONENTES DE LA INTERFAZ (VISTAS)
# ==========================================

def vista_inventario(df):
    st.header("📦 Inventario en Tiempo Real")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.info("💡 Los cambios en Google Sheets se reflejan al recargar.")

def vista_ventas(df):
    st.header("🛒 Registro de Ventas")
    if 'Nombre' in df.columns:
        lista_prod = df['Nombre'].tolist()
        seleccion = st.selectbox("Producto a vender:", lista_prod)
        cantidad = st.number_input("Cantidad:", min_value=1, value=1)
        
        if st.button(f"Confirmar Venta"):
            st.success(f"Venta registrada: {cantidad} unidad(es) de {seleccion}")
    else:
        st.error("No se encontró la columna 'Nombre'.")

def vista_usuarios():
    st.header("👤 Gestión de Usuarios")
    with st.form("form_registro"):
        u = st.text_input("Nombre de usuario")
        p = st.text_input("Contraseña", type="password")
        r = st.selectbox("Rol", ["Vendedor", "Admin"])
        if st.form_submit_button("Registrar Usuario"):
            if u and p:
                if registrar_nuevo_usuario(u, p, r):
                    st.success(f"¡Usuario {u} creado!")
                    st.balloons()
            else:
                st.warning("Completa todos los campos.")

# ==========================================
# 4. FLUJO PRINCIPAL (EL CONTROLADOR)
# ==========================================

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acceso - Ferretería Universal")
    user = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    
    if st.button("Entrar"):
        if validar_login(user, clave):
            st.session_state.autenticado = True
            st.session_state.usuario_actual = user
            st.success(f"Bienvenido {user}")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
else:
    # App Principal
    st.sidebar.title("🛠️ Menú")
    opciones = ["Inventario", "Ventas"]
    if st.session_state.get('rol') == "Admin":
        opciones.append("Usuarios")
        
    menu = st.sidebar.radio("Ir a:", opciones)
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    datos_inv = cargar_inventario()

    if datos_inv is not None:
        if menu == "Inventario":
            vista_inventario(datos_inv)
        elif menu == "Ventas":
            vista_ventas(datos_inv)
        elif menu == "Usuarios":
            vista_usuarios()
