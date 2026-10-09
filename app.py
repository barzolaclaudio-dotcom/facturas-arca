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
_PWA_CSS = """
    <head>
        <link rel="manifest" href="/app/static/manifest.json">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="apple-mobile-web-app-title" content="Facturas ARCA">
        <meta name="theme-color" content="#000000">
    </head>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap');

    :root {
        --gold-300: #edcc55; --gold-400: #e8c132; --gold-500: #D4AF37; --gold-600: #b8951c;
        --bg-card: #111113; --bg-tertiary: #18181b;
        --text-tertiary: #a1a1aa;
        --border: rgba(212,175,55,0.15); --border-hover: rgba(212,175,55,0.35);
    }
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', system-ui, sans-serif;
        -webkit-font-smoothing: antialiased;
    }
    .stApp {
        background: radial-gradient(ellipse at top, rgba(212,175,55,0.08), transparent 55%), #000000;
    }
    header[data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] {
        background: #09090b;
        border-right: 1px solid var(--border);
    }
    h1, h2, h3, h4 { font-family: 'Plus Jakarta Sans', sans-serif; color: #fff; }

    .brand {
        display: inline-flex; align-items: baseline; gap: 8px;
        font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800;
        font-size: 1.3rem; color: #fff; margin-bottom: 1.2rem;
    }
    .brand span {
        font-family: 'Playfair Display', serif; font-style: italic; font-weight: 400;
        color: var(--gold-500); font-size: 1.1rem;
    }
    .main-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #fff; font-size: 2.4rem; font-weight: 800;
        line-height: 1.2; margin-bottom: 0.4rem;
    }
    .main-title em {
        font-family: 'Playfair Display', serif; font-style: italic; font-weight: 400;
        background: linear-gradient(135deg, var(--gold-300), var(--gold-500), var(--gold-600));
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .sub-title { color: var(--text-tertiary); font-size: 1.05rem; margin-bottom: 1.8rem; }

    /* Botones: dorado primario / contorno secundario */
    .stButton>button, .stDownloadButton>button {
        border-radius: 16px; font-weight: 600; padding: 0.7rem 1.4rem;
        transition: all .3s cubic-bezier(.4,0,.2,1);
    }
    .stButton>button[kind="primary"], .stDownloadButton>button[kind="primary"] {
        color: #000; border: none;
        background: linear-gradient(135deg, var(--gold-400) 0%, var(--gold-500) 40%, var(--gold-600) 70%, var(--gold-500) 100%);
        box-shadow: 0 0 0 1px rgba(212,175,55,.5), 0 4px 24px rgba(212,175,55,.35), inset 0 1px 0 rgba(255,255,255,.3);
    }
    .stButton>button[kind="primary"]:hover, .stDownloadButton>button[kind="primary"]:hover {
        transform: translateY(-2px) scale(1.02); filter: brightness(1.08); color: #000;
        box-shadow: 0 0 0 2px rgba(212,175,55,.8), 0 8px 40px rgba(212,175,55,.5);
    }
    .stButton>button[kind="secondary"] {
        color: var(--gold-400); background: transparent;
        border: 1px solid rgba(212,175,55,.4);
    }
    .stButton>button[kind="secondary"]:hover {
        background: rgba(212,175,55,.08); border-color: var(--gold-500);
        color: var(--gold-300); transform: translateY(-2px);
    }

    /* Tarjetas y campos */
    [data-testid="stFileUploader"] section, [data-testid="stAlert"] {
        background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px;
    }
    [data-testid="stFileUploader"] section:hover { border-color: var(--border-hover); }
    [data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="base-input"] {
        background: var(--bg-tertiary); border-radius: 8px;
    }
    [data-testid="stImage"] img { border-radius: 16px; border: 1px solid var(--border); }
    hr { border-color: var(--border); }

    /* Ocultar elementos de Streamlit para experiencia App nativa */
    #MainMenu { visibility: hidden; display: none; }
    footer { visibility: hidden; display: none; }
    header[data-testid="stHeader"] { visibility: hidden; display: none; }
    [data-testid="stStatusWidget"] { visibility: hidden; display: none; }
    .viewerBadge_container__r5tak, [data-testid="manage-app-button"] { display: none !important; }
    </style>
    <script>
    // Inyectar manifiesto e ícono dinámicamente en el documento principal
    try {
        let doc = window.parent ? window.parent.document : document;
        let head = doc.head;
        if (!head.querySelector("link[rel='manifest']")) {
            let m = doc.createElement("link");
            m.rel = "manifest";
            m.href = "https://barzolaclaudio-dotcom.github.io/facturas-arca/static/manifest.json";
            head.appendChild(m);
        }
        if (!head.querySelector("link[rel='apple-touch-icon']")) {
            let icon = doc.createElement("link");
            icon.rel = "apple-touch-icon";
            icon.href = "https://barzolaclaudio-dotcom.github.io/facturas-arca/static/icon-512.png";
            head.appendChild(icon);
        }
    } catch(e) {}
    </script>
"""
st.markdown("\n".join(l.strip() for l in _PWA_CSS.splitlines() if l.strip()), unsafe_allow_html=True)

# Encabezado
st.markdown('<div class="brand">CB <span>Asesor Profesional</span></div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">Estampador de Logos para <em>Facturas ARCA / AFIP</em></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Adjunta tus marcas o logos a las facturas electrónicas en formato PDF sin perder la calidad ni el formato original.</div>', unsafe_allow_html=True)

ensure_logos_dir()
saved_logos = list_saved_logos()

# Valores por defecto para posición y formato
pos_x = DEFAULT_ARCA_BBOX["x"]  # 30.0
pos_y = DEFAULT_ARCA_BBOX["y"]  # 50.0
pos_w = DEFAULT_ARCA_BBOX["width"]  # 150.0
pos_h = DEFAULT_ARCA_BBOX["height"]  # 50.0
logo_align = "left"
apply_all_pages = True
transparent_bg = False

# ==========================================
# PASO 1: SELECCIONAR O SUBIR LOGO (Flujo Principal)
# ==========================================
st.markdown("### 🎨 1. Logo para la Factura")

col_logo_select, col_logo_preview = st.columns([3, 2])

with col_logo_select:
    if saved_logos:
        logo_names = list(saved_logos.keys())
        # Preseleccionar 'Logo CB' por defecto si existe
        default_idx = logo_names.index("Logo CB") if "Logo CB" in logo_names else 0
        selected_logo_name = st.selectbox(
            "Elige un logo de tu galería:",
            options=logo_names,
            index=default_idx
        )
    else:
        st.info("💡 No tienes logos guardados. Sube tu logo a continuación.")
        selected_logo_name = None

current_logo_bytes = None
current_logo_path = None

if selected_logo_name and selected_logo_name in saved_logos:
    current_logo_path = saved_logos[selected_logo_name]
    with open(current_logo_path, "rb") as f:
        current_logo_bytes = f.read()

with col_logo_preview:
    if current_logo_path:
        st.image(current_logo_path, caption=f"Logo activo: {selected_logo_name}", use_container_width=True)

# Opciones para subir nuevo logo o administrar galería
with st.expander("➕ Subir nuevo logo o administrar galería", expanded=False):
    col_up1, col_up2 = st.columns([1, 1])
    with col_up1:
        st.markdown("##### Subir nuevo logo")
        new_logo_file = st.file_uploader("Imagen del logo (PNG, JPG, WEBP):", type=["png", "jpg", "jpeg", "webp"], key="main_new_logo")
        logo_custom_name = st.text_input("Nombre para la galería (ej: Mi Marca / Empresa B):", key="main_logo_name")
        if new_logo_file and logo_custom_name.strip():
            if st.button("💾 Guardar Logo en Galería", type="primary", key="btn_save_main_logo"):
                ext = os.path.splitext(new_logo_file.name)[1]
                save_name = f"{logo_custom_name.strip()}{ext}"
                save_logo(save_name, new_logo_file.getvalue())
                st.success(f"¡Logo '{logo_custom_name}' guardado!")
                st.rerun()
    with col_up2:
        if selected_logo_name:
            st.markdown(f"##### Eliminar logo actual")
            st.write(f"¿Deseas quitar '{selected_logo_name}' de la galería?")
            if st.button(f"🗑️ Eliminar '{selected_logo_name}'", type="secondary", key="btn_del_main_logo"):
                if delete_logo(selected_logo_name):
                    st.success(f"Logo eliminado.")
                    st.rerun()

# Ajustes de posición y formato avanzados
with st.expander("⚙️ Ajustes avanzados de posición y formato (Opcional)", expanded=False):
    preset_option = st.radio(
        "Preajuste de ubicación:",
        ["ARCA / AFIP Estándar (Horizontal 30, Vertical 50)", "Personalizado"],
        horizontal=True
    )
    if preset_option == "ARCA / AFIP Estándar (Horizontal 30, Vertical 50)":
        st.caption("📍 Coordenadas oficiales: Horizontal = 30, Vertical = 50.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            pos_x = st.number_input("Horizontal (X):", min_value=0.0, max_value=600.0, value=30.0, step=2.0)
        with c2:
            pos_y = st.number_input("Vertical (Y):", min_value=0.0, max_value=800.0, value=50.0, step=2.0)
        with c3:
            pos_w = st.number_input("Ancho máx:", min_value=10.0, max_value=400.0, value=150.0, step=2.0)
        with c4:
            pos_h = st.number_input("Alto máx:", min_value=10.0, max_value=300.0, value=50.0, step=2.0)

    c_al, c_bg, c_pg = st.columns(3)
    with c_al:
        align_label = st.selectbox("Alineación dentro del recuadro:", ["Izquierda", "Centro", "Derecha"], index=0)
        align_map = {"Izquierda": "left", "Centro": "center", "Derecha": "right"}
        logo_align = align_map[align_label]
    with c_bg:
        transparent_bg = st.checkbox("Fondo blanco transparente", value=False, help="Quita fondo blanco en JPGs")
    with c_pg:
        apply_all_pages = st.checkbox("Aplicar a todas las hojas", value=True, help="Original, Duplicado, Triplicado")

st.divider()

# ==========================================
# PASO 2: CARGA DE FACTURAS
# ==========================================
st.markdown("### 📥 2. Cargar Factura(s) PDF de ARCA / AFIP")
uploaded_pdfs = st.file_uploader(
    "Selecciona o arrastra una o varias Facturas en PDF:",
    type=["pdf"],
    accept_multiple_files=True
)

if not uploaded_pdfs:
    st.info("👆 Sube tus facturas PDF en el recuadro de arriba para comenzar.")
    st.markdown("""
    ### ℹ️ Pasos para estampar tus facturas:
    1. **Elige tu logo** en el Paso 1 de arriba (por defecto ya está seleccionado tu Logo CB).
    2. **Carga tus facturas PDF** de ARCA/AFIP aquí.
    3. Revisa la **vista previa** y descarga tu factura lista con tu marca.
    """)
else:
    if not current_logo_bytes:
        st.warning("⚠️ Selecciona o sube un logo en el Paso 1 para estamparlo en la(s) factura(s).")
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
