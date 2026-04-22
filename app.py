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
    """Trae los datos de la pestaña Inventario con las 10 columnas"""
    try:
        df = conn.read(worksheet="Inventario", ttl=0)
        df = df.iloc[:, :10] 
        df.columns = ['ID', 'Nombre', 'Precio', 'Costo', 'Stock', 'Codigo Barra', 'Grupo', 'Material', 'Granel', 'Ganancia']
        
        # Limpieza de tipos de datos
        df['ID'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int)
        df['Stock'] = pd.to_numeric(df['Stock'], errors='coerce').fillna(0).astype(int)
        df['Codigo Barra'] = df['Codigo Barra'].astype(str).replace(r'\.0$', '', regex=True).replace('nan', '')
        
        return df.dropna(subset=['Nombre'])
    except Exception as e:
        st.error(f"Error cargando inventario: {e}")
        return None

def validar_login(user, clave):
    """Valida usuario y contraseña contra la pestaña Usuarios"""
    try:
        df_usuarios = conn.read(worksheet="Usuarios", ttl=0)
        u_input = str(user).strip().lower()
        p_input = str(clave).strip()
        
        for index, row in df_usuarios.iterrows():
            if str(row['Usuario']).strip().lower() == u_input and str(row['Clave']).strip() == p_input:
                st.session_state.rol = str(row['Rol']).strip()
                return True
        return False
    except Exception as e:
        st.error(f"Error en validación: {e}")
        return False

# ==========================================
# 3. COMPONENTES DE LA INTERFAZ (VISTAS)
# ==========================================

def vista_ventas(df):
    st.header("🛒 Registro de Ventas")
    
    # Buscador doble
    busqueda = st.text_input("🔍 Busca por Nombre, Marca o escanea Código de Barra:")
    
    # Filtro dinámico
    prod_filt = df[
        df['Nombre'].str.contains(busqueda, case=False, na=False) | 
        df['Codigo Barra'].str.contains(busqueda, na=False)
    ]

    if not prod_filt.empty:
        seleccion = st.selectbox("Selecciona el producto:", prod_filt['Nombre'])
        info = prod_filt[prod_filt['Nombre'] == seleccion].iloc[0]
        
        stock_actual = int(info['Stock'])
        precio_u = float(info['Precio'])

        c1, c2 = st.columns(2)
        c1.metric("Stock Disponible", f"{stock_actual} un.")
        c2.metric("Precio Unitario", f"${precio_u:,.0f}")

        # Cantidad (solo permite hasta el stock disponible)
        cantidad = st.number_input("Cantidad a vender:", min_value=1, max_value=stock_actual if stock_actual > 0 else 1, value=1)
        total = cantidad * precio_u

        if stock_actual <= 0:
            st.error("❌ Producto sin stock disponible.")
        else:
            st.subheader(f"Total a Cobrar: ${total:,.0f}")
            
            if st.button("🚀 Confirmar Venta", type="primary"):
                try:
                    # Actualizar stock en el DataFrame original
                    df.loc[df['ID'] == info['ID'], 'Stock'] = stock_actual - cantidad
                    conn.update(worksheet="Inventario", data=df)
                    
                    st.success(f"✅ Venta confirmada. Stock actualizado.")
                    st.balloons()
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al actualizar stock: {e}")
    else:
        st.warning("No se encontraron productos.")

# ==========================================
# 4. FLUJO PRINCIPAL (LOGIN Y NAVEGACIÓN)
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
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
else:
    # Sidebar: Navegación según Rol
    st.sidebar.title(f"👤 {st.session_state.usuario_actual}")
    st.sidebar.write(f"Rol: {st.session_state.rol}")
    
    opciones = ["Ventas"]
    if st.session_state.rol in ["Administrador", "Supervisor"]:
        opciones.insert(0, "Gestión Inventario")
    if st.session_state.rol == "Administrador":
        opciones.append("Usuarios")
    
    menu = st.sidebar.radio("Ir a:", opciones)
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    # Carga de datos para las vistas
    datos = cargar_inventario()

    if datos is not None:
        if menu == "Gestión Inventario":
            inventario_admin.vista_admin_inventario(conn)
        elif menu == "Ventas":
            vista_ventas(datos)
        elif menu == "Usuarios":
            usuarios.vista_usuarios(conn)
