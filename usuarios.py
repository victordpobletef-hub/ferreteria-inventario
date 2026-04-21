import streamlit as st
import pandas as pd

# --- FUNCIONES DE LÓGICA ---

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

def actualizar_usuario(conn, usuario_nombre, nueva_clave, nuevo_rol):
    try:
        df = conn.read(worksheet="Usuarios", ttl=0)
        df.loc[df['Usuario'] == usuario_nombre, ['Clave', 'Rol']] = [nueva_clave, nuevo_rol]
        conn.update(worksheet="Usuarios", data=df)
        return True
    except Exception as e:
        st.error(f"Error al actualizar: {e}")
        return False

def borrar_usuario(conn, usuario_a_borrar):
    try:
        df_actual = conn.read(worksheet="Usuarios", ttl=0)
        df_final = df_actual[df_actual['Usuario'] != usuario_a_borrar]
        conn.update(worksheet="Usuarios", data=df_final)
        return True
    except Exception as e:
        st.error(f"Error al borrar: {e}")
        return False

# --- INTERFAZ VISUAL ---

def vista_usuarios(conn):
    st.header("👤 Panel de Control de Personal")
    
    # Leemos datos
    df_usuarios = conn.read(worksheet="Usuarios", ttl=0)
    
    # Pestañas con iconos para que se vea mejor
    tab1, tab2, tab3 = st.tabs(["➕ Registrar", "📝 Editar", "🗑️ Eliminar"])

    with tab1:
        with st.form("form_registro"):
            u = st.text_input("Nombre de usuario", key="reg_user")
            p = st.text_input("Contraseña", type="password", key="reg_pass")
            r = st.selectbox("Rol", ["Vendedor", "Supervisor", "Administrador", "Observador"], key="reg_rol")
            if st.form_submit_button("Registrar Usuario"):
                if u and p:
                    if registrar_nuevo_usuario(conn, u, p, r):
                        st.success(f"¡Usuario {u} creado!")
                        st.rerun()
                else:
                    st.warning("Faltan datos.")

    with tab2:
        lista_u = df_usuarios['Usuario'].tolist()
        if lista_u:
            u_selec = st.selectbox("Selecciona usuario a editar:", lista_u, key="sel_edit")
            datos = df_usuarios[df_usuarios['Usuario'] == u_selec].iloc[0]
            
            with st.form("form_editar"):
                nueva_p = st.text_input("Nueva Contraseña", value=str(datos['Clave']), key="edit_pass")
                nuevo_r = st.selectbox("Cambiar Rol", 
                                      ["Vendedor", "Supervisor", "Administrador", "Observador"],
                                      index=["Vendedor", "Supervisor", "Administrador", "Observador"].index(datos['Rol']),
                                      key="edit_rol")
                if st.form_submit_button("Guardar Cambios"):
                    if actualizar_usuario(conn, u_selec, nueva_p, nuevo_r):
                        st.success("Actualizado correctamente.")
                        st.rerun()
        else:
            st.write("No hay usuarios para editar.")

    with tab3:
        lista_u_del = df_usuarios['Usuario'].tolist()
        # Evitar que se borre a sí mismo
        yo = st.session_state.get('usuario_actual', '')
        if yo in lista_u_del:
            lista_u_del.remove(yo)
            
        if lista_u_del:
            u_borrar = st.selectbox("Selecciona usuario a eliminar:", lista_u_del, key="sel_del")
            if st.button("Confirmar Eliminación", type="primary", key="btn_del"):
                if borrar_usuario(conn, u_borrar):
                    st.success(f"Usuario {u_borrar} eliminado.")
                    st.rerun()
        else:
            st.write("No hay otros usuarios para eliminar.")

    # Tabla resumen siempre visible
    st.divider()
    st.subheader("📋 Lista de Personal")
    st.dataframe(df_usuarios[['Usuario', 'Rol']], use_container_width=True, hide_index=True)
