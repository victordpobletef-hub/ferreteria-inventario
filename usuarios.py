import streamlit as st
import pandas as pd

def registrar_nuevo_usuario(conn, user, clave, rol):
    """Guarda un usuario en la pestaña Usuarios"""
    try:
        # Leemos con ttl=0 para tener siempre lo último
        df_actual = conn.read(worksheet="Usuarios", ttl=0)
        nueva_fila = pd.DataFrame([{"Usuario": user, "Clave": clave, "Rol": rol}])
        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
        conn.update(worksheet="Usuarios", data=df_final)
        return True
    except Exception as e:
        st.error(f"Error al guardar en Excel: {e}")
        return False

def vista_usuarios(conn):
    """Interfaz visual de la gestión de usuarios"""
    st.header("👤 Gestión de Usuarios y Roles")
    
    with st.form("form_registro"):
        u = st.text_input("Nombre de usuario")
        p = st.text_input("Contraseña", type="password")
        # Aquí están tus nuevos roles
        r = st.selectbox("Rol", ["Vendedor", "Supervisor", "Administrador", "Observador"])
        
        if st.form_submit_button("Registrar Usuario"):
            if u and p:
                if registrar_nuevo_usuario(conn, u, p, r):
                    st.success(f"¡Usuario {u} creado como {r}!")
                    st.balloons()
            else:
                st.warning("Completa todos los campos.")

    # Mostrar tabla de usuarios actuales para control
    if st.checkbox("Ver usuarios registrados"):
        df_usuarios = conn.read(worksheet="Usuarios", ttl=0)
        st.table(df_usuarios[['Usuario', 'Rol']])
