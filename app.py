import streamlit as st
import os
import io
from pdf_processor import (
    list_saved_logos,
    save_logo,
    delete_logo,
    add_logo_to_pdf,
    render_pdf_page_preview,
    process_batch_pdfs,
    get_pdf_page_count,
    DEFAULT_ARCA_BBOX,
    ensure_logos_dir
)

st.set_page_config(
    page_title="Estampador de Logos - Facturas ARCA",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de meta-etiquetas PWA para instalación móvil en Android, iPhone e iPad
st.markdown("""
    <head>
        <link rel="manifest" href="/app/static/manifest.json">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="apple-mobile-web-app-title" content="Facturas ARCA">
        <meta name="theme-color" content="#1E3A8A">
    </head>
    <style>
    .main-title {
        color: #1E3A8A;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #4B5563;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado
st.markdown('<div class="main-title">📄 Estampador de Logos para Facturas ARCA / AFIP</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Adjunta tus marcas o logos a las facturas electrónicas en formato PDF sin perder la calidad ni el formato original.</div>', unsafe_allow_html=True)

ensure_logos_dir()

# ==========================================
# BARRA LATERAL: GALERÍA DE LOGOS Y POSICIÓN
# ==========================================
st.sidebar.header("🎨 Galería de Logos")

# Obtener logos guardados (incluye auto-descubrimiento en raíz y en logos/)
saved_logos = list_saved_logos()

# Selector de Logo
if saved_logos:
    logo_options = ["-- Seleccionar Logo Guardado --"] + list(saved_logos.keys())
    selected_logo_name = st.sidebar.selectbox("Elige un logo de tu galería:", logo_options)
else:
    st.sidebar.info("💡 No tienes logos guardados. ¡Sube uno abajo!")
    selected_logo_name = "-- Seleccionar Logo Guardado --"

# Cargar bytes del logo seleccionado
current_logo_bytes = None
current_logo_path = None

if selected_logo_name != "-- Seleccionar Logo Guardado --":
    current_logo_path = saved_logos[selected_logo_name]
    with open(current_logo_path, "rb") as f:
        current_logo_bytes = f.read()
    st.sidebar.image(current_logo_path, caption=f"Logo activo: {selected_logo_name}", use_container_width=True)

    # Opción para eliminar logo guardado
    if st.sidebar.button(f"🗑️ Eliminar '{selected_logo_name}'", type="secondary"):
        if delete_logo(selected_logo_name):
            st.sidebar.success(f"Logo '{selected_logo_name}' eliminado.")
            st.rerun()

st.sidebar.divider()
st.sidebar.subheader("➕ Subir Nuevo Logo")
new_logo_file = st.sidebar.file_uploader("Subir imagen de logo (PNG, JPG, WEBP)", type=["png", "jpg", "jpeg", "webp"])
logo_custom_name = st.sidebar.text_input("Nombre para la galería (ej: Mi Marca / Empresa B):")

if new_logo_file and logo_custom_name.strip():
    if st.sidebar.button("💾 Guardar Logo en Galería", type="primary"):
        ext = os.path.splitext(new_logo_file.name)[1]
        save_name = f"{logo_custom_name.strip()}{ext}"
        saved_path = save_logo(save_name, new_logo_file.getvalue())
        st.sidebar.success(f"¡Logo '{logo_custom_name}' guardado en la galería!")
        st.rerun()
elif new_logo_file and not logo_custom_name.strip():
    current_logo_bytes = new_logo_file.getvalue()
    st.sidebar.caption("📌 Usando logo subido temporalmente.")

st.sidebar.divider()
st.sidebar.header("⚙️ Ajustes de Posición y Proporción")

preset_option = st.sidebar.radio(
    "Preajuste de ubicación:",
    ["ARCA / AFIP Estándar (Horizontal 30, Vertical 50)", "Personalizado"]
)

if preset_option == "ARCA / AFIP Estándar (Horizontal 30, Vertical 50)":
    pos_x = DEFAULT_ARCA_BBOX["x"]  # 30.0
    pos_y = DEFAULT_ARCA_BBOX["y"]  # 50.0
    pos_w = DEFAULT_ARCA_BBOX["width"]  # 150.0
    pos_h = DEFAULT_ARCA_BBOX["height"]  # 50.0
    st.sidebar.caption("📍 Coordenadas configuradas: Horizontal = 30, Vertical = 50.")
else:
    pos_x = st.sidebar.number_input("Posición Horizontal (X):", min_value=0.0, max_value=600.0, value=30.0, step=2.0)
    pos_y = st.sidebar.number_input("Posición Vertical (Y):", min_value=0.0, max_value=800.0, value=50.0, step=2.0)
    pos_w = st.sidebar.number_input("Ancho máximo:", min_value=10.0, max_value=400.0, value=150.0, step=2.0)
    pos_h = st.sidebar.number_input("Alto máximo:", min_value=10.0, max_value=300.0, value=50.0, step=2.0)

align_label = st.sidebar.radio("Alineación dentro del recuadro:", ["Izquierda", "Centro", "Derecha"], index=0)
align_map = {"Izquierda": "left", "Centro": "center", "Derecha": "right"}
logo_align = align_map[align_label]

st.sidebar.subheader("Opciones de Formato")
apply_all_pages = st.sidebar.checkbox(
    "Aplicar logo a TODAS las hojas (Original, Duplicado, Triplicado)",
    value=True,
    help="Al estar activo, el logo aparecerá en las 3 páginas de la factura emitida por ARCA."
)

transparent_bg = st.sidebar.checkbox(
    "Hacer transparente el fondo blanco del logo",
    value=False,
    help="Útil si tu logo es una imagen JPG con recuadro blanco y quieres que solo se vea el diseño."
)

# ==========================================
# ÁREA PRINCIPAL: CARGA Y PROCESAMIENTO
# ==========================================

uploaded_pdfs = st.file_uploader(
    "📥 Selecciona o arrastra una o varias Facturas en PDF:",
    type=["pdf"],
    accept_multiple_files=True
)

if not uploaded_pdfs:
    st.info("👆 Sube tus facturas PDF en el recuadro de arriba para comenzar.")
    st.markdown("""
    ### ℹ️ ¿Cómo funciona?
    1. **Sube tu logo** en la barra lateral izquierda (o selecciónalo si ya está guardado).
    2. **Carga tus facturas PDF** de ARCA/AFIP arriba.
    3. Revisa la **vista previa en tiempo real** (los logos cuadrados o rectangulares mantendrán exactamente su forma original en Horizontal 30, Vertical 50).
    4. Descarga tu factura lista en PDF o descarga un archivo **ZIP** si procesaste varias facturas juntas.
    """)
else:
    if not current_logo_bytes:
        st.warning("⚠️ Selecciona o sube un logo en la barra lateral para estamparlo en la(s) factura(s).")
    else:
        num_files = len(uploaded_pdfs)

        if num_files == 1:
            pdf_file = uploaded_pdfs[0]
            st.subheader(f"📄 Factura: `{pdf_file.name}`")

            pdf_bytes = pdf_file.getvalue()
            total_pages = get_pdf_page_count(pdf_bytes)

            col_preview, col_controls = st.columns([3, 2])

            with col_preview:
                st.markdown("#### 👁️ Vista Previa en Tiempo Real")
                
                if total_pages > 1:
                    page_labels = [f"Hoja {i+1} ({'Original' if i==0 else 'Duplicado' if i==1 else 'Triplicado' if i==2 else 'Copia'})" for i in range(total_pages)]
                    selected_page_idx = st.selectbox("Selecciona la hoja a previsualizar:", range(total_pages), format_func=lambda i: page_labels[i])
                else:
                    selected_page_idx = 0

                with st.spinner("Generando vista previa..."):
                    try:
                        preview_img = render_pdf_page_preview(
                            pdf_bytes=pdf_bytes,
                            logo_bytes=current_logo_bytes,
                            x=pos_x,
                            y=pos_y,
                            width=pos_w,
                            height=pos_h,
                            page_num=selected_page_idx,
                            apply_to_all_pages=apply_all_pages,
                            transparent_bg=transparent_bg,
                            align=logo_align
                        )
                        st.image(preview_img, caption=f"Vista previa: Hoja {selected_page_idx + 1} de {total_pages} (Posición: Horizontal {pos_x}, Vertical {pos_y})", use_container_width=True)
                    except Exception as e:
                        st.error(f"Error al generar vista previa: {e}")

            with col_controls:
                st.markdown("#### 📥 Descargar Factura")
                st.write(f"Se estampará el logo en las **{total_pages} hojas** en la posición (Horiz: {pos_x}, Vert: {pos_y}).")

                try:
                    modified_pdf = add_logo_to_pdf(
                        pdf_bytes=pdf_bytes,
                        logo_bytes=current_logo_bytes,
                        x=pos_x,
                        y=pos_y,
                        width=pos_w,
                        height=pos_h,
                        apply_to_all_pages=apply_all_pages,
                        transparent_bg=transparent_bg,
                        align=logo_align
                    )

                    name_base, ext = os.path.splitext(pdf_file.name)
                    output_name = f"{name_base}_con_logo{ext}"

                    st.download_button(
                        label="⬇️ Descargar Factura PDF con Logo",
                        data=modified_pdf,
                        file_name=output_name,
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )

                    st.success(f"✨ ¡Factura de {total_pages} hojas lista para descargar!")
                except Exception as e:
                    st.error(f"Error al procesar el PDF: {e}")

        else:
            # Procesamiento de múltiples archivos (Lote)
            st.subheader(f"📚 Procesamiento en Lote: {num_files} Facturas cargadas")

            col_batch_list, col_batch_action = st.columns([3, 2])

            with col_batch_list:
                st.markdown("#### 📋 Facturas a Procesar")
                file_names = [f.name for f in uploaded_pdfs]
                for name in file_names:
                    st.caption(f"• {name}")

                st.markdown("#### 👁️ Vista Previa del primer comprobante")
                with st.spinner("Generando vista previa..."):
                    first_pdf_bytes = uploaded_pdfs[0].getvalue()
                    total_pages = get_pdf_page_count(first_pdf_bytes)
                    preview_img = render_pdf_page_preview(
                        pdf_bytes=first_pdf_bytes,
                        logo_bytes=current_logo_bytes,
                        x=pos_x,
                        y=pos_y,
                        width=pos_w,
                        height=pos_h,
                        page_num=0,
                        apply_to_all_pages=apply_all_pages,
                        transparent_bg=transparent_bg,
                        align=logo_align
                    )
                    st.image(preview_img, caption=f"Muestra: {uploaded_pdfs[0].name} (Hoja 1 de {total_pages})", use_container_width=True)

            with col_batch_action:
                st.markdown("#### 📦 Descarga Todo en ZIP")
                st.write(f"Se estampará el logo en las {num_files} facturas en posición (Horiz: {pos_x}, Vert: {pos_y}).")

                pdf_batch = [(f.name, f.getvalue()) for f in uploaded_pdfs]

                try:
                    zip_data = process_batch_pdfs(
                        pdf_files=pdf_batch,
                        logo_bytes=current_logo_bytes,
                        x=pos_x,
                        y=pos_y,
                        width=pos_w,
                        height=pos_h,
                        apply_to_all_pages=apply_all_pages,
                        transparent_bg=transparent_bg,
                        align=logo_align
                    )

                    st.download_button(
                        label=f"⬇️ Descargar Paquete ZIP ({num_files} Facturas)",
                        data=zip_data,
                        file_name="facturas_con_logo.zip",
                        mime="application/zip",
                        type="primary",
                        use_container_width=True
                    )

                    st.success(f"✨ ¡Las {num_files} facturas han sido procesadas en todas sus hojas!")
                except Exception as e:
                    st.error(f"Error al procesar lote de PDFs: {e}")
