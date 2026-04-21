import streamlit as st
import pandas as pd

# --- FUNCIONES DE LÓGICA ---

def actualizar_usuario(conn, usuario_nombre, nueva_clave, nuevo_rol):
    try:
        df = conn.read(worksheet="Usuarios", ttl=0)
        # Buscamos la fila y actualizamos los valores
        df.loc[df['Usuario'] == usuario_nombre, ['Clave', 'Rol']] = [nueva_clave, nuevo_rol]
        conn.update(worksheet="Usuarios", data=df)
        return True
    except Exception as e:
        st.error(f"Error al actualizar: {e}")
        return False

# ... (Mantén aquí tus funciones registrar_nuevo_usuario y borrar_usuario) ...

def vista_usuarios(conn):
    st.header("👤 Panel de Control de Personal")
    
    # Leemos los datos una sola vez para todas las pestañas
    df_usuarios = conn.read(worksheet="Usuarios", ttl=0)
    
    tab1, tab2, tab3 = st.tabs(["➕ Registrar", "📝 Editar", "🗑️ Eliminar"])

    with tab1:
        # ... (Tu código de registro que ya funciona) ...
        pass

    with tab2:
        st.subheader("Modificar datos de usuario")
        lista_u = df_usuarios['Usuario'].tolist()
        u_selec = st.selectbox("Selecciona usuario a editar:", lista_u, key="edit_select")
        
        # Obtenemos datos actuales del usuario seleccionado para rellenar el formulario
        datos_usuario = df_usuarios[df_usuarios['Usuario'] == u_selec].iloc[0]
        
        with st.form("form_editar"):
            nueva_p = st.text_input("Nueva Contraseña", value=str(datos_usuario['Clave']))
            nuevo_r = st.selectbox("Cambiar Rol", 
                                  ["Vendedor", "Supervisor", "Administrador", "Observador"],
                                  index=["Vendedor", "Supervisor", "Administrador", "Observador"].index(datos_usuario['Rol']))
            
            if st.form_submit_button("Guardar Cambios"):
                if actualizar_usuario(conn, u_selec, nueva_p, nuevo_r):
                    st.success(f"Usuario {u_selec} actualizado.")
                    st.rerun()

    with tab3:
        # ... (Tu código de borrar que ya funciona) ...
        pass

    # Mostrar lista general al final
    st.divider()
    st.dataframe(df_usuarios[['Usuario', 'Rol']], use_container_width=True, hide_index=True)
