import streamlit as st
import pandas as pd

def vista_admin_inventario(conn):
    st.header("🛠️ Gestión de Productos")
    
    # 1. CARGA Y LIMPIEZA (Aseguramos 10 columnas)
    df = conn.read(worksheet="Inventario", ttl=0)
    df = df.iloc[:, :10] # Forzamos lectura de las 10 columnas
    df.columns = ['ID', 'Nombre', 'Precio', 'Costo', 'Stock', 'Codigo Barra', 'Grupo', 'Material', 'Granel', 'Ganancia']
    
    # Limpieza para evitar errores de tipo
    for col in ['Nombre', 'Codigo Barra', 'Grupo', 'Material', 'Granel']:
        df[col] = df[col].astype(str).replace('nan', '')

    tab1, tab2, tab3 = st.tabs(["➕ Añadir Producto", "📝 Modificar", "🗑️ Eliminar"])

    # --- TAB 1: AÑADIR ---
    with tab1:
        st.subheader("🆕 Ingresar Nuevo Producto")
        nuevo_id = int(df['ID'].max() + 1) if not df.empty else 1
        st.info(f"ID Automático: {nuevo_id}")

        with st.form("form_nuevo_prod", clear_on_submit=True):
            nombre = st.text_input("Nombre del Producto *")
            c1, c2, c3 = st.columns(3)
            p_venta = c1.number_input("Precio Venta *", min_value=0)
            p_costo = c2.number_input("Precio Costo *", min_value=0)
            stock_ini = c3.number_input("Stock Inicial *", min_value=0)
            
            ca, cb, cc = st.columns(3)
            grupo = ca.selectbox("Grupo", ["Clavos y Anclajes", "Electrico", "Fiting", "Herrajes", "Herramientas", "Hogar", "Jardinería", "Pintura", "Químicos", "Seguridad", "Tornillería"])
            material = cb.selectbox("Material", ["ARIDO", "BRONCE", "COBRE", "MADERA", "METAL", "OTRO", "PLASTICO", "PVC", "QUIMICO", "SILICONA"])
            granel = cc.selectbox("Granel", ["No", "Si"])
            
            c_barra = st.text_input("Código de Barra (Opcional)")
            
            if st.form_submit_button("Guardar en Inventario"):
                if nombre and p_venta > 0:
                    # CALCULAMOS GANANCIA ANTES DE GUARDAR
                    ganancia_n = (p_venta / 1.19) - (p_venta * 0.038) - p_costo
                    
                    # CREAMOS LA FILA CON LAS 10 COLUMNAS EXACTAS
                    nueva_fila = pd.DataFrame([[
                        nuevo_id, nombre.strip(), p_venta, p_costo, stock_ini, 
                        str(c_barra), grupo, material, granel, ganancia_n
                    ]], columns=df.columns)
                    
                    df_final = pd.concat([df, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Inventario", data=df_final)
                    st.success("✅ Producto añadido con ganancia calculada.")
                    st.rerun()
                else:
                    st.error("❌ Nombre y Precio son obligatorios.")

    # --- TAB 2: MODIFICAR ---
    with tab2:
        if not df.empty:
            prod_edit = st.selectbox("Selecciona producto:", df['Nombre'].tolist(), key="ed_sel")
            idx = df[df['Nombre'] == prod_edit].index
            datos = df.loc[idx].iloc[0] # Usamos .iloc[0] para evitar errores de series
            
            with st.form("form_edit_inv"):
                n_n = st.text_input("Nombre", value=str(datos['Nombre']))
                col_v, col_c, col_s = st.columns(3)
                n_pv = col_v.number_input("Precio Venta", value=int(datos['Precio']))
                n_pc = col_c.number_input("Precio Costo", value=int(datos['Costo']))
                n_st = col_s.number_input("Stock", value=int(datos['Stock']))
                
                # Recalcular ganancia en vivo para el update
                n_gan = (n_pv / 1.19) - (n_pv * 0.038) - n_pc

                if st.form_submit_button("Actualizar"):
                    df.at[idx[0], 'Nombre'] = str(n_n)
                    df.at[idx[0], 'Precio'] = float(n_pv)
                    df.at[idx[0], 'Costo'] = float(n_pc)
                    df.at[idx[0], 'Stock'] = int(n_st)
                    df.at[idx[0], 'Ganancia'] = float(n_gan)
                    
                    conn.update(worksheet="Inventario", data=df)
                    st.success("✅ Actualizado con nueva ganancia.")
                    st.rerun()

    # --- TAB 3: ELIMINAR ---
    with tab3:
        if not df.empty:
            p_del = st.selectbox("Producto a eliminar:", df['Nombre'].tolist(), key="del_sel")
            if st.button("Confirmar Borrado", type="primary"):
                df_f = df[df['Nombre'] != p_del]
                conn.update(worksheet="Inventario", data=df_f)
                st.success("✅ Eliminado.")
                st.rerun()

    st.divider()
    st.dataframe(df, use_container_width=True, hide_index=True)
