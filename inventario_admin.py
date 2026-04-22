import streamlit as st
import pandas as pd

def vista_admin_inventario(conn):
    st.header("🛠️ Gestión de Productos")
    
    # Cargar datos actuales
    df = conn.read(worksheet="Inventario", ttl=0)
    df = df.iloc[:, :6]
    df.columns = ['ID', 'Nombre', 'Precio', 'Costo', 'Stock', 'Codigo Barra']
    
    tab1, tab2, tab3 = st.tabs(["➕ Añadir Producto", "📝 Modificar", "🗑️ Eliminar"])

    # --- TAB 1: AÑADIR ---
    with tab1:
        with st.form("form_nuevo_prod"):
            col1, col2 = st.columns(2)
            nuevo_id = col1.number_input("ID", min_value=1, value=int(df['ID'].max() + 1) if not df.empty else 1)
            nuevo_nombre = col2.text_input("Nombre del Producto")
            
            p_venta = col1.number_input("Precio Venta", min_value=0, value=0)
            p_costo = col2.number_input("Precio Costo", min_value=0, value=0)
            
            stock_ini = col1.number_input("Stock Inicial", min_value=0, value=0)
            c_barra = col2.text_input("Código de Barra")
            
            if st.form_submit_button("Guardar Nuevo Producto"):
                if nuevo_nombre:
                    nueva_fila = pd.DataFrame([[nuevo_id, nuevo_nombre, p_venta, p_costo, stock_ini, c_barra]], 
                                             columns=df.columns)
                    df_final = pd.concat([df, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Inventario", data=df_final)
                    st.success(f"Producto '{nuevo_nombre}' añadido.")
                    st.rerun()
                else:
                    st.warning("El nombre es obligatorio.")

    # --- TAB 2: MODIFICAR ---
    with tab2:
        if not df.empty:
            prod_edit = st.selectbox("Selecciona producto para editar:", df['Nombre'].tolist(), key="sel_edit_inv")
            datos = df[df['Nombre'] == prod_edit].iloc[0]
            
            with st.form("form_edit_inv"):
                new_n = st.text_input("Nombre", value=datos['Nombre'])
                col_a, col_b = st.columns(2)
                new_p = col_a.number_input("Precio Venta", value=int(datos['Precio']))
                new_c = col_b.number_input("Precio Costo", value=int(datos['Costo']))
                new_s = col_a.number_input("Stock", value=int(datos['Stock']))
                new_cb = col_b.text_input("Código Barra", value=str(datos['Codigo Barra']))
                
                if st.form_submit_button("Actualizar Producto"):
                    df.loc[df['Nombre'] == prod_edit, ['Nombre', 'Precio', 'Costo', 'Stock', 'Codigo Barra']] = [new_n, new_p, new_c, new_s, new_cb]
                    conn.update(worksheet="Inventario", data=df)
                    st.success("Producto actualizado.")
                    st.rerun()

    # --- TAB 3: ELIMINAR ---
    with tab3:
        if not df.empty:
            prod_del = st.selectbox("Selecciona producto para eliminar:", df['Nombre'].tolist(), key="sel_del_inv")
            st.warning(f"¿Estás seguro de eliminar '{prod_del}'?")
            if st.button("Confirmar Eliminación definitiva", type="primary"):
                df_final = df[df['Nombre'] != prod_del]
                conn.update(worksheet="Inventario", data=df_final)
                st.success("Producto eliminado.")
                st.rerun()

    # Resumen visual abajo
    st.divider()
    st.subheader("📋 Estado Actual")
    st.dataframe(df, use_container_width=True, hide_index=True)
