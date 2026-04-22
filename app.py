import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import usuarios
import inventario_admin 

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="Ferretería Universal", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# ==========================================
# 2. FUNCIONES DE LÓGICA (EL "CEREBRO")
# ==========================================

def cargar_inventario():
    try:
        df = conn.read(worksheet="Inventario", ttl=0)
        df = df.iloc[:, :10] # Ahora leemos 10 columnas
        df.columns = ['ID', 'Nombre', 'Precio', 'Costo', 'Stock', 'Codigo Barra', 'Grupo', 'Material', 'Granel', 'Ganancia']
        
        # --- CÁLCULO AUTOMÁTICO DE GANANCIA ---
        # Convertimos a números por seguridad
        p = pd.to_numeric(df['Precio'], errors='coerce').fillna(0)
        c = pd.to_numeric(df['Costo'], errors='coerce').fillna(0)
        
        # Aplicamos tu fórmula: (Precio / 1.19) - (Precio * 0.038) - Costo
        df['Ganancia'] = (p / 1.19) - (p * 0.038) - c
        
        # Limpieza de ID y Stock
        df['ID'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int)
        df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0).astype(int)
        
        return df.dropna(subset=['Nombre'])
    except Exception as e:
        st.error(f"Error cargando inventario: {e}")
        return None
        
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
    st.header("📦 Inventario Completo")
    # Mostramos todo pero formateamos los precios
    st.dataframe(df.style.format({
        "Precio": "${:,.0f}",
        "Costo": "${:,.0f}",
        "Ganancia": "${:,.0f}" # Sin decimales para que sea más claro
        }), use_container_width=True, hide_index=True)

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
    if st.session_state.get('rol') in ["Administrador", "Supervisor"]:
        opciones.append("Gestión Inventario") # Nuevo botón
    if st.session_state.get('rol') == "Administrador":
        opciones.append("Usuarios")
        
    menu = st.sidebar.radio("Ir a:", opciones)
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    datos_inv = cargar_inventario()

    if menu == "Inventario":
        vista_inventario(datos_inv)
    elif menu == "Ventas":
        vista_ventas(datos_inv)
    elif menu == "Gestión Inventario":
        inventario_admin.vista_admin_inventario(conn) # Llamada al nuevo archivo
    elif menu == "Usuarios":
        usuarios.vista_usuarios(conn)
