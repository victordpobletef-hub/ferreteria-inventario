import streamlit as st
import pandas as pd

def vista_admin_inventario(conn):
    st.header("🛠️ Gestión de Productos")
    
    # 1. Cargar datos (Esto ya lo tenías)
    df = conn.read(worksheet="Inventario", ttl=0)
    # ... (tus líneas de limpieza de columnas aquí) ...

    tab1, tab2, tab3 = st.tabs(["➕ Añadir Producto", "📝 Modificar", "🗑️ Eliminar"])

    # --- AQUÍ PEGAS EL NUEVO CÓDIGO ---
    with tab1:
        st.subheader("🆕 Ingresar Nuevo Producto")
        
        # Cálculo automático del ID
        if not df.empty:
            nuevo_id = int(df['ID'].max()) + 1
        else:
            nuevo_id = 1
        
        st.info(f"Asignando automáticamente el **ID: {nuevo_id}**")

        with st.form("form_nuevo_prod", clear_on_submit=True):
            nuevo_nombre = st.text_input("Nombre del Producto *")
            
            col1, col2 = st.columns(2)
            p_venta = col1.number_input("Precio Venta *", min_value=0, value=0)
            p_costo = col2.number_input("Precio Costo *", min_value=0, value=0)
            
            stock_ini = col1.number_input("Stock Inicial *", min_value=0, value=0)
            c_barra = col2.text_input("Código de Barra (Opcional)")
            
            submit = st.form_submit_button("Guardar en Inventario")

            if submit:
                # Validación estricta
                if not nuevo_nombre:
                    st.error("❌ El nombre del producto es obligatorio.")
                elif p_venta <= 0 or p_costo <= 0:
                    st.error("❌ Los precios deben ser mayores a 0.")
                else:
                    # Guardado
                    nueva_fila = pd.DataFrame([[nuevo_id, nuevo_nombre.strip(), p_venta, p_costo, stock_ini, c_barra.strip()]], 
                                             columns=df.columns)
                    df_final = pd.concat([df, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Inventario", data=df_final)
                    st.success(f"✅ ¡{nuevo_nombre} guardado!")
                    st.rerun()

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
