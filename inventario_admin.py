import streamlit as st
import pandas as pd


def vista_admin_inventario(conn):
    st.header("🛠️ Gestión de Productos")

    # ==========================================
    # 1. CARGA Y LIMPIEZA
    # ==========================================
    df = conn.read(worksheet="Inventario", ttl=0)
    df = df.iloc[:, :10]
    df.columns = ['ID', 'Nombre', 'Precio', 'Costo', 'Stock', 'Codigo Barra', 'Grupo', 'Material', 'Granel', 'Ganancia']

    for col in ['Nombre', 'Codigo Barra', 'Grupo', 'Material', 'Granel']:
        df[col] = df[col].astype(str).replace('nan', '')

    # ==========================================
    # 2. FORMULARIO AÑADIR PRODUCTO
    # ==========================================
    with st.expander("➕ Añadir Nuevo Producto", expanded=True):
        nuevo_id = int(df['ID'].max() + 1) if not df.empty else 1

        # --- PRECIO COSTO fuera del form → actualiza en tiempo real ---
        p_costo_live = st.number_input(
            "Precio Costo *",
            min_value=0,
            key="costo_live",
            help="Ingresa el costo y el precio de venta se calculará automáticamente"
        )
        # p_venta = costo / (1/1.19 - 0.038 - 0.30)
        factor = (1 / 1.19) - 0.038 - 0.30
        precio_sugerido = round(p_costo_live / factor) if p_costo_live > 0 else 0

        if precio_sugerido > 0:
            st.success(f"💡 Precio de venta sugerido con 30% de ganancia: **${precio_sugerido:,.0f}**")

        # --- Resto del formulario ---
        with st.form("form_nuevo_prod", clear_on_submit=True):
            nombre = st.text_input("Nombre del Producto *")

            col_v, col_s = st.columns(2)
            p_venta = col_v.number_input(
                "Precio Venta *",
                min_value=0,
                value=precio_sugerido,
                help="Puedes modificar el precio sugerido"
            )
            stock_ini = col_s.number_input("Stock Inicial *", min_value=0)

            ca, cb, cc = st.columns(3)
            grupo = ca.selectbox("Grupo", ["Clavos y Anclajes", "Electrico", "Fiting", "Herrajes",
                                            "Herramientas", "Hogar", "Jardinería", "Pintura",
                                            "Químicos", "Seguridad", "Tornillería"])
            material = cb.selectbox("Material", ["ARIDO", "BRONCE", "COBRE", "MADERA", "METAL",
                                                  "OTRO", "PLASTICO", "PVC", "QUIMICO", "SILICONA"])
            granel = cc.selectbox("Granel", ["No", "Si"])
            c_barra = st.text_input("Código de Barra (Opcional)")

            if st.form_submit_button("Guardar en Inventario", type="primary"):
                p_costo_final = st.session_state.get("costo_live", 0)
                if nombre and p_venta > 0 and p_costo_final > 0:
                    ganancia_n = (p_venta / 1.19) - (p_venta * 0.038) - p_costo_final
                    nueva_fila = pd.DataFrame([[
                        nuevo_id, nombre.strip(), p_venta, p_costo_final, stock_ini,
                        str(c_barra), grupo, material, granel, ganancia_n
                    ]], columns=df.columns)
                    df_final = pd.concat([df, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Inventario", data=df_final)
                    st.success("✅ Producto añadido correctamente.")
                    st.rerun()
                else:
                    st.error("❌ Nombre, Precio Costo y Precio Venta son obligatorios.")

    # ==========================================
    # 3. FORMULARIO DE EDICIÓN (se activa al pulsar ✏️)
    # ==========================================
    if 'editar_id' in st.session_state and st.session_state.editar_id is not None:
        eid = st.session_state.editar_id
        fila = df[df['ID'] == eid]
        if not fila.empty:
            datos = fila.iloc[0]
            st.divider()
            st.subheader(f"📝 Editando: {datos['Nombre']}")
            with st.form("form_editar_inline"):
                n_n = st.text_input("Nombre", value=str(datos['Nombre']))
                col_v, col_c, col_s = st.columns(3)
                n_pc = col_v.number_input("Precio Costo", value=int(datos['Costo']))
                n_pv = col_c.number_input("Precio Venta", value=int(datos['Precio']))
                n_st = col_s.number_input("Stock", value=int(datos['Stock']))

                ca2, cb2, cc2 = st.columns(3)
                grupos = ["Clavos y Anclajes", "Electrico", "Fiting", "Herrajes",
                          "Herramientas", "Hogar", "Jardinería", "Pintura",
                          "Químicos", "Seguridad", "Tornillería"]
                materiales = ["ARIDO", "BRONCE", "COBRE", "MADERA", "METAL",
                              "OTRO", "PLASTICO", "PVC", "QUIMICO", "SILICONA"]
                g_idx = grupos.index(datos['Grupo']) if datos['Grupo'] in grupos else 0
                m_idx = materiales.index(datos['Material']) if datos['Material'] in materiales else 0
                n_grupo = ca2.selectbox("Grupo", grupos, index=g_idx)
                n_mat = cb2.selectbox("Material", materiales, index=m_idx)
                n_gran = cc2.selectbox("Granel", ["No", "Si"],
                                       index=0 if datos['Granel'] == 'No' else 1)
                n_cb = st.text_input("Código de Barra", value=str(datos['Codigo Barra']))

                col_btn1, col_btn2 = st.columns([1, 4])
                guardar = col_btn1.form_submit_button("💾 Guardar", type="primary")
                cancelar = col_btn2.form_submit_button("✖ Cancelar")

                if guardar:
                    n_gan = (n_pv / 1.19) - (n_pv * 0.038) - n_pc
                    idx_real = df[df['ID'] == eid].index[0]
                    df.at[idx_real, 'Nombre'] = str(n_n)
                    df.at[idx_real, 'Precio'] = float(n_pv)
                    df.at[idx_real, 'Costo'] = float(n_pc)
                    df.at[idx_real, 'Stock'] = int(n_st)
                    df.at[idx_real, 'Grupo'] = n_grupo
                    df.at[idx_real, 'Material'] = n_mat
                    df.at[idx_real, 'Granel'] = n_gran
                    df.at[idx_real, 'Codigo Barra'] = str(n_cb)
                    df.at[idx_real, 'Ganancia'] = float(n_gan)
                    conn.update(worksheet="Inventario", data=df)
                    st.session_state.editar_id = None
                    st.success("✅ Producto actualizado.")
                    st.rerun()

                if cancelar:
                    st.session_state.editar_id = None
                    st.rerun()

    # ==========================================
    # 4. TABLA CON BOTONES POR FILA
    # ==========================================
    st.divider()
    st.subheader("📋 Estado Actual del Inventario")

    if df.empty:
        st.info("No hay productos en el inventario.")
    else:
        cols_header = st.columns([0.5, 2.5, 1, 1, 0.8, 1.5, 1.2, 1.2, 0.8, 1, 0.6, 0.6])
        headers = ["ID", "Nombre", "Precio", "Costo", "Stock",
                   "Cód. Barra", "Grupo", "Material", "Granel", "Ganancia", "✏️", "🗑️"]
        for col, h in zip(cols_header, headers):
            col.markdown(f"**{h}**")

        st.divider()

        if 'confirmar_borrar_id' not in st.session_state:
            st.session_state.confirmar_borrar_id = None

        for _, row in df.iterrows():
            pid = int(row['ID'])
            cols = st.columns([0.5, 2.5, 1, 1, 0.8, 1.5, 1.2, 1.2, 0.8, 1, 0.6, 0.6])

            cols[0].write(pid)
            cols[1].write(row['Nombre'])
            cols[2].write(f"${int(row['Precio']):,}")
            cols[3].write(f"${int(row['Costo']):,}")
            cols[4].write(int(row['Stock']))
            codigo = str(row['Codigo Barra']).split('.')[0] if str(row['Codigo Barra']) not in ['nan', 'None', ''] else '-'
            cols[5].write(codigo)
            cols[6].write(row['Grupo'])
            cols[7].write(row['Material'])
            cols[8].write(row['Granel'])
            cols[9].write(f"${int(row['Ganancia']):,}")

            if cols[10].button("✏️", key=f"edit_{pid}"):
                st.session_state.editar_id = pid
                st.session_state.confirmar_borrar_id = None
                st.rerun()

            if cols[11].button("🗑️", key=f"del_{pid}"):
                st.session_state.confirmar_borrar_id = pid
                st.session_state.editar_id = None

            if st.session_state.confirmar_borrar_id == pid:
                with st.container():
                    st.warning(f"¿Seguro que quieres eliminar **{row['Nombre']}**?")
                    col_si, col_no, _ = st.columns([1, 1, 6])
                    if col_si.button("✅ Sí, eliminar", key=f"confirm_del_{pid}", type="primary"):
                        df_f = df[df['ID'] != pid]
                        conn.update(worksheet="Inventario", data=df_f)
                        st.session_state.confirmar_borrar_id = None
                        st.success("✅ Producto eliminado.")
                        st.rerun()
                    if col_no.button("❌ Cancelar", key=f"cancel_del_{pid}"):
                        st.session_state.confirmar_borrar_id = None
                        st.rerun()
