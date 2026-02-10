import os
import random
import sys
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _mes_abreviado_es(m: int) -> str:
    meses = [
        "ene", "feb", "mar", "abr", "may", "jun",
        "jul", "ago", "sep", "oct", "nov", "dic"
    ]
    if 1 <= int(m) <= 12:
        return meses[int(m) - 1]
    return "ene"


def _fmt_dt_es(dt: datetime) -> str:
    dd = f"{dt.day:02d}"
    mon = _mes_abreviado_es(dt.month)
    yyyy = f"{dt.year:04d}"
    hh = f"{dt.hour:02d}"
    mm = f"{dt.minute:02d}"
    ss = f"{dt.second:02d}"
    return f"{dd}-{mon}-{yyyy} {hh}:{mm}:{ss}"


def _random_autorizacion_like_uuid() -> str:
    hexs = "0123456789ABCDEF"
    def r(n):
        return "".join(random.choice(hexs) for _ in range(n))
    return f"{r(8)}-{r(4)}-{r(4)}-{r(4)}-{r(12)}"


def generar_factura_pdf(
    *,
    nit_receptor: str,
    nombre_receptor: str,
    items: list,
    output_dir: str | None = None,
    template_png_path: str | None = None,
    serie: str = "0BD04EC9",
    dte: str = "142691778",
    moneda: str = "GTQ",
    autorizacion: str | None = None,
    dt: datetime | None = None,
):
    nit_receptor = (nit_receptor or "").strip()
    nombre_receptor = (nombre_receptor or "").strip()
    if not nit_receptor or not nombre_receptor:
        raise ValueError("Falta NIT o nombre del receptor")

    if not items:
        raise ValueError("No hay items para facturar")

    if dt is None:
        dt = datetime.now()

    if not autorizacion:
        autorizacion = _random_autorizacion_like_uuid()

    if not output_dir:
        output_dir = os.path.join(BASE_DIR, "facturas")
    os.makedirs(output_dir, exist_ok=True)

    if not template_png_path:
        template_png_path = os.path.join(BASE_DIR, "factura_template.png")

    ts = dt.strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(output_dir, f"factura_{ts}.pdf")

    c = canvas.Canvas(out_path, pagesize=letter)
    W, H = letter

    if os.path.exists(template_png_path):
        img = ImageReader(template_png_path)
        c.drawImage(img, 0, 0, width=W, height=H, mask='auto')

    def white_box(x, y, w, h):
        c.setFillColorRGB(1, 1, 1)
        c.setStrokeColorRGB(1, 1, 1)
        c.rect(x, y, w, h, fill=1, stroke=0)

    def text(x, y, s, size=9, bold=False):
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(x, y, s)

    def text_right(x, y, s, size=9, bold=False):
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawRightString(x, y, s)

    fecha_str = _fmt_dt_es(dt)

    white_box(395, 705, 190, 22)
    text(400, 712, autorizacion, size=9, bold=True)

    white_box(60, 647, 260, 14)
    text(60, 649.5, f"NIT Receptor: {nit_receptor}", size=9)

    white_box(60, 631, 360, 14)
    text(60, 633.5, f"Nombre Receptor: {nombre_receptor}", size=9)

    white_box(350, 648, 240, 48)
    text(350, 680, f"Fecha y hora de emision: {fecha_str}", size=9)
    text(350, 664, f"Fecha y hora de certificacion: {fecha_str}", size=9)
    text(520, 648, f"Moneda: {moneda}", size=9)

    start_y = 563
    row_h = 18
    max_rows = 10

    total_general = 0.0

    for idx, it in enumerate(items[:max_rows], start=1):
        cant = int(it.get("cantidad", 1))
        desc = (it.get("descripcion", "") or "").strip()
        precio = float(it.get("precio_unitario", 0.0))
        subtotal = cant * precio
        total_general += subtotal

        y = start_y - (idx - 1) * row_h

        white_box(62, y, 485, row_h - 2)

        text_right(86, y + 5, str(idx), size=9)
        text(95, y + 5, "Servicio", size=9)
        text_right(176, y + 5, str(cant), size=9)
        text(185, y + 5, desc[:50], size=9)
        text_right(338, y + 5, f"{precio:.2f}", size=9)
        text_right(420, y + 5, "0.00", size=9)
        text_right(505, y + 5, "0.00", size=9)
        text_right(575, y + 5, f"{subtotal:.2f}", size=9)

    white_box(296, 520, 300, 18)
    text_right(420, 524.5, "0.00", size=9)
    text_right(505, 524.5, "0.00", size=9)
    text_right(575, 524.5, f"{total_general:.2f}", size=9)

    c.showPage()
    c.save()
    return out_path


def abrir_archivo(path: str):
    try:
        if os.name == "nt":
            os.startfile(path)
        elif sys.platform == "darwin":
            os.system(f"open \"{path}\"")
        else:
            os.system(f"xdg-open \"{path}\"")
    except Exception:
        pass
