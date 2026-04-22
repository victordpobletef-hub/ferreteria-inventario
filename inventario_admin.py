import streamlit as st
import pandas as pd

def vista_admin_inventario(conn):
    st.header("🛠️ Gestión de Productos")
    
    # 1. Cargar datos actuales
    df = conn.read(worksheet="Inventario", ttl=0)
    # Forzamos que lea las 9 columnas exactas
    df = df.iloc[:, :9]
    df.columns = ['ID', 'Nombre', 'Precio', 'Costo', 'Stock', 'Codigo Barra', 'Grupo', 'Material', 'Granel']
    
    tab1, tab2, tab3 = st.tabs(["➕ Añadir Producto", "📝 Modificar", "🗑️ Eliminar"])

    # --- TAB 1: AÑADIR ---
    with tab1:
        st.subheader("🆕 Ingresar Nuevo Producto")
        nuevo_id = int(df['ID'].max() + 1) if not df.empty else 1
        st.info(f"ID Automático: {nuevo_id}")

        with st.form("form_nuevo_prod", clear_on_submit=True):
            nombre = st.text_input("Nombre del Producto *")
            
            col1, col2, col3 = st.columns(3)
            p_venta = col1.number_input("Precio Venta *", min_value=0)
            p_costo = col2.number_input("Precio Costo *", min_value=0)
            stock_ini = col3.number_input("Stock Inicial *", min_value=0)
            
            col_a, col_b, col_c = st.columns(3)
            grupo = col_a.selectbox("Grupo", ["Clavos y Anclajes", "Electrico", "Fiting", "Herrajes", "Herramientas", "Hogar", "Jardinería", "Pintura", "Químicos", "Seguridad", "Tornillería"])
            material = col_b.selectbox("Material", ["ARIDO", "BRONCE", "COBRE", "MADERA", "METAL", "OTRO", "PLASTICO", "PVC", "QUIMICO", "SILICONA"])
            granel = col_c.selectbox("Granel", ["No", "Si"])
            
            c_barra = st.text_input("Código de Barra (Opcional)")
            
            if st.form_submit_button("Guardar en Inventario"):
                if nombre and p_venta > 0:
                    nueva_fila = pd.DataFrame([[nuevo_id, nombre.strip(), p_venta, p_costo, stock_ini, c_barra, grupo, material, granel]], 
                                             columns=df.columns)
                    df_final = pd.concat([df, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Inventario", data=df_final)
                    st.success("✅ Producto añadido.")
                    st.rerun()
                else:
                    st.error("❌ El nombre y precio son obligatorios.")

    # --- TAB 2: MODIFICAR ---
    with tab2:
        if not df.empty:
            prod_edit = st.selectbox("Selecciona producto:", df['Nombre'].tolist(), key="edit_sel")
            idx = df[df['Nombre'] == prod_edit].index[0]
            datos = df.loc[idx]
            
            with st.form("form_edit_inv"):
                new_n = st.text_input("Nombre", value=str(datos['Nombre']))
                c1, c2, c3 = st.columns(3)
                new_pv = c1.number_input("Precio Venta", value=int(datos['Precio']))
                new_pc = c2.number_input("Precio Costo", value=int(datos['Costo']))
                new_st = c3.number_input("Stock", value=int(datos['Stock']))
                
                ca, cb, cc = st.columns(3)
                # Listas para los selectbox
                list_g = ["Clavos y Anclajes", "Electrico", "Fiting", "Herrajes", "Herramientas", "Hogar", "Jardinería", "Pintura", "Químicos", "Seguridad", "Tornillería"]
                list_m = ["ARIDO", "BRONCE", "COBRE", "MADERA", "METAL", "OTRO", "PLASTICO", "PVC", "QUIMICO", "SILICONA"]
                
                new_g = ca.selectbox("Grupo", list_g, index=list_g.index(datos['Grupo']) if datos['Grupo'] in list_g else 0)
                new_m = cb.selectbox("Material", list_m, index=list_m.index(datos['Material']) if datos['Material'] in list_m else 0)
                new_gr = cc.selectbox("Granel", ["No", "Si"], index=0 if datos['Granel'] == "No" else 1)
                
                new_cb = st.text_input("Código Barra", value=str(datos['Codigo Barra']))
                
                 if st.form_submit_button("Actualizar"):
                    # 1. Aseguramos que las columnas de texto acepten cualquier texto
                    columnas_texto = ['Nombre', 'Codigo Barra', 'Grupo', 'Material', 'Granel']
                    for col in columnas_texto:
                        df[col] = df[col].astype(object)
                    
                    # 2. Realizamos la actualización
                    df.loc[idx, ['Nombre', 'Precio', 'Costo', 'Stock', 'Codigo Barra', 'Grupo', 'Material', 'Granel']] = [
                        str(new_n), 
                        float(new_pv), 
                        float(new_pc), 
                        int(new_st), 
                        str(new_cb), 
                        str(new_g), 
                        str(new_m), 
                        str(new_gr)
                    ]
                    
                    # 3. Subimos al Excel
                    conn.update(worksheet="Inventario", data=df)
                    st.success("✅ Producto actualizado correctamente.")
                    st.rerun()

    # --- TAB 3: ELIMINAR ---
    with tab3:
        if not df.empty:
            prod_del = st.selectbox("Producto a eliminar:", df['Nombre'].tolist(), key="del_sel")
            if st.button("Confirmar Eliminación", type="primary"):
                df_final = df[df['Nombre'] != prod_del]
                conn.update(worksheet="Inventario", data=df_final)
                st.success("✅ Eliminado.")
                st.rerun()

    # Resumen
    st.divider()
    st.dataframe(df, use_container_width=True, hide_index=True)
