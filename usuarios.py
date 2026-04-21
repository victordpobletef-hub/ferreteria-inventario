import streamlit as st
import pandas as pd

def registrar_nuevo_usuario(conn, user, clave, rol):
    try:
        df_actual = conn.read(worksheet="Usuarios", ttl=0)
        nueva_fila = pd.DataFrame([{"Usuario": user, "Clave": clave, "Rol": rol}])
        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
        conn.update(worksheet="Usuarios", data=df_final)
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

def borrar_usuario(conn, usuario_a_borrar):
    try:
        df_actual = conn.read(worksheet="Usuarios", ttl=0)
        # Filtramos: dejamos todos menos el que queremos borrar
        df_final = df_actual[df_actual['Usuario'] != usuario_a_borrar]
        
        if len(df_actual) == len(df_final):
            st.error("No se encontró el usuario.")
            return False
            
        conn.update(worksheet="Usuarios", data=df_final)
        return True
    except Exception as e:
        st.error(f"Error al borrar: {e}")
        return False

def vista_usuarios(conn):
    st.header("👤 Gestión de Usuarios y Roles")
    
    # --- Pestañas para organizar ---
    tab1, tab2 = st.tabs(["➕ Registrar Nuevo", "🗑️ Eliminar Usuario"])

    with tab1:
        with st.form("form_registro"):
            u = st.text_input("Nombre de usuario")
            p = st.text_input("Contraseña", type="password")
            r = st.selectbox("Rol", ["Vendedor", "Supervisor", "Administrador", "Observador"])
            if st.form_submit_button("Registrar Usuario"):
                if u and p:
                    if registrar_nuevo_usuario(conn, u, p, r):
                        st.success(f"¡Usuario {u} creado!")
                        st.rerun()
                else:
                    st.warning("Completa todos los campos.")

    with tab2:
        df_usuarios = conn.read(worksheet="Usuarios", ttl=0)
        lista_usuarios = df_usuarios['Usuario'].tolist()
        
        # Evitar que el admin se borre a sí mismo por accidente
        if st.session_state.usuario_actual in lista_usuarios:
            lista_usuarios.remove(st.session_state.usuario_actual)

        u_borrar = st.selectbox("Selecciona usuario a eliminar:", lista_usuarios)
        
        if st.button("Confirmar Eliminación", type="primary"):
            if borrar_usuario(conn, u_borrar):
                st.success(f"Usuario {u_borrar} eliminado correctamente.")
                st.rerun()

    # Mostrar lista abajo
    st.divider()
    st.subheader("📋 Usuarios actuales")
    st.dataframe(df_usuarios[['Usuario', 'Rol']], use_container_width=True, hide_index=True)
