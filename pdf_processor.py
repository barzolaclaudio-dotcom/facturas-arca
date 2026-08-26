import pymupdf as fitz  # PyMuPDF
import io
import os
import zipfile
from PIL import Image

# Coordenadas ajustadas a petición del usuario: X = 30.0, Y = 50.0
DEFAULT_ARCA_BBOX = {
    "x": 30.0,
    "y": 50.0,
    "width": 150.0,
    "height": 50.0
}

LOGOS_DIR = os.path.join(os.path.dirname(__file__), "logos")

def ensure_logos_dir():
    """Garantiza que la carpeta de logos existe."""
    if not os.path.exists(LOGOS_DIR):
        os.makedirs(LOGOS_DIR, exist_ok=True)
    return LOGOS_DIR

def list_saved_logos() -> dict[str, str]:
    """
    Retorna un diccionario de {nombre_logo: ruta_archivo}.
    Busca imágenes tanto en la raíz del proyecto como en la carpeta logos/
    y organiza automáticamente las imágenes hacia logos/.
    """
    ensure_logos_dir()
    valid_exts = (".png", ".jpg", ".jpeg", ".webp", ".bmp")
    root_dir = os.path.dirname(__file__)

    for fname in os.listdir(root_dir):
        if fname.lower().endswith(valid_exts):
            src_path = os.path.join(root_dir, fname)
            dst_path = os.path.join(LOGOS_DIR, fname)
            try:
                os.replace(src_path, dst_path)
            except Exception:
                pass

    logos = {}
    for fname in sorted(os.listdir(LOGOS_DIR)):
        if fname.lower().endswith(valid_exts):
            name_without_ext = os.path.splitext(fname)[0]
            logos[name_without_ext] = os.path.join(LOGOS_DIR, fname)
    return logos

def save_logo(file_name: str, file_bytes: bytes) -> str:
    """Guarda un logo subido en la carpeta local de logos."""
    ensure_logos_dir()
    clean_name = "".join(c for c in file_name if c.isalnum() or c in (" ", "_", "-", ".")).strip()
    target_path = os.path.join(LOGOS_DIR, clean_name)
    with open(target_path, "wb") as f:
        f.write(file_bytes)
    return target_path

def delete_logo(logo_name: str) -> bool:
    """Elimina un logo guardado."""
    logos = list_saved_logos()
    if logo_name in logos:
        path = logos[logo_name]
        if os.path.exists(path):
            os.remove(path)
            return True
    return False

def make_white_background_transparent(logo_bytes: bytes, tolerance: int = 240) -> bytes:
    """
    Convierte fondos blancos/casi blancos de imágenes JPG o PNG a transparentes
    para evitar recuadros blancos feos sobre la factura.
    """
    try:
        img = Image.open(io.BytesIO(logo_bytes)).convert("RGBA")
        datas = img.getdata()

        new_data = []
        for item in datas:
            if item[0] >= tolerance and item[1] >= tolerance and item[2] >= tolerance:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)

        img.putdata(new_data)
        out_buffer = io.BytesIO()
        img.save(out_buffer, format="PNG")
        return out_buffer.getvalue()
    except Exception:
        return logo_bytes

def calculate_exact_rect(
    logo_bytes: bytes,
    x: float,
    y: float,
    max_w: float,
    max_h: float,
    align: str = "left"
) -> fitz.Rect:
    """
    Calcula el rectángulo fitz.Rect exacto manteniendo rigurosamente la relación
    de aspecto (ancho/alto) original de la imagen del logo para evitar cualquier deformación.
    """
    try:
        img = Image.open(io.BytesIO(logo_bytes))
        img_w, img_h = img.size
        aspect = img_w / img_h
    except Exception:
        aspect = max_w / max_h

    # Calcular dimensiones sin deformación
    box_aspect = max_w / max_h
    if aspect > box_aspect:
        w = max_w
        h = max_w / aspect
    else:
        h = max_h
        w = max_h * aspect

    # Alineación horizontal dentro del recuadro
    if align == "center":
        x_final = x + (max_w - w) / 2.0
    elif align == "right":
        x_final = x + (max_w - w)
    else:  # left
        x_final = x

    # Centrado vertical en el área reservada
    y_final = y + (max_h - h) / 2.0

    return fitz.Rect(x_final, y_final, x_final + w, y_final + h)

def get_pdf_page_count(pdf_bytes: bytes) -> int:
    """Retorna el número de páginas de un PDF."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        count = len(doc)
        doc.close()
        return count
    except Exception:
        return 1

def add_logo_to_pdf(
    pdf_bytes: bytes,
    logo_bytes: bytes,
    x: float = 30.0,
    y: float = 50.0,
    width: float = 150.0,
    height: float = 50.0,
    apply_to_all_pages: bool = True,
    transparent_bg: bool = False,
    align: str = "left"
) -> bytes:
    """
    Superpone el logo en las coordenadas especificadas manteniendo rigurosamente
    la proporción original de la imagen (sin deformar).
    """
    if transparent_bg:
        logo_bytes = make_white_background_transparent(logo_bytes)

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    rect = calculate_exact_rect(logo_bytes, x, y, width, height, align=align)

    pages_to_process = range(len(doc)) if apply_to_all_pages else [0]

    for page_idx in pages_to_process:
        if page_idx < len(doc):
            page = doc[page_idx]
            page.insert_image(rect, stream=logo_bytes, keep_proportion=True, overlay=True)

    output_stream = io.BytesIO()
    doc.save(output_stream)
    doc.close()
    return output_stream.getvalue()

def render_pdf_page_preview(
    pdf_bytes: bytes,
    logo_bytes: bytes = None,
    x: float = 30.0,
    y: float = 50.0,
    width: float = 150.0,
    height: float = 50.0,
    page_num: int = 0,
    apply_to_all_pages: bool = True,
    transparent_bg: bool = False,
    align: str = "left",
    dpi: int = 150
) -> Image.Image:
    """
    Renderiza la página seleccionada de la factura con el logo sin deformar para vista previa.
    """
    if logo_bytes:
        modified_pdf_bytes = add_logo_to_pdf(
            pdf_bytes,
            logo_bytes,
            x=x,
            y=y,
            width=width,
            height=height,
            apply_to_all_pages=apply_to_all_pages,
            transparent_bg=transparent_bg,
            align=align
        )
        doc = fitz.open(stream=modified_pdf_bytes, filetype="pdf")
    else:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    safe_page_num = max(0, min(page_num, len(doc) - 1))
    page = doc[safe_page_num]
    pix = page.get_pixmap(dpi=dpi)
    doc.close()

    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return img

def process_batch_pdfs(
    pdf_files: list[tuple[str, bytes]],
    logo_bytes: bytes,
    x: float = 30.0,
    y: float = 50.0,
    width: float = 150.0,
    height: float = 50.0,
    apply_to_all_pages: bool = True,
    transparent_bg: bool = False,
    align: str = "left"
) -> bytes:
    """
    Procesa múltiples facturas PDF y las empaqueta en un archivo ZIP listo para descargar.
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for original_name, pdf_bytes in pdf_files:
            processed_pdf = add_logo_to_pdf(
                pdf_bytes,
                logo_bytes,
                x=x,
                y=y,
                width=width,
                height=height,
                apply_to_all_pages=apply_to_all_pages,
                transparent_bg=transparent_bg,
                align=align
            )
            name_base, ext = os.path.splitext(original_name)
            out_filename = f"{name_base}_con_logo{ext}"
            zip_file.writestr(out_filename, processed_pdf)
    
    return zip_buffer.getvalue()
