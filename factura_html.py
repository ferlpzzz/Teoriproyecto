import os
import webbrowser
import datetime
import random
import string

EMISOR_BLOQUE_AZUL = {
    "nombre": "CLAUDIA LORENA , SULECIO TAMAYAC",
    "nit": "12123676",
    "comercial": "LORETS",
    "dir1": "21 AVENIDA Y 4 CALLE 20-45 E EDIFICIO LA ESTACION LOCAL E,",
    "dir2": "zona 3, QUETZALTENANGO, QUETZALTENANGO",
}

SERIE_FIJA = "0BD04EC9"
DTE_FIJO = "142691778"


def _esc(s):
    s = "" if s is None else str(s)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _auth_random(n=36):
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(int(n)))


def abrir_factura_en_navegador(nit_receptor, nombres, apellidos, items, carpeta="facturas_html"):
    os.makedirs(carpeta, exist_ok=True)
    auth = _auth_random(36)
    now = datetime.datetime.now().strftime("%d-%b-%Y %H:%M:%S").lower()

    total_general = 0.0
    total_impuestos = 0.0

    filas = ""
    for i, it in enumerate(items or [], 1):
        cantidad = float(it.get("cantidad", 1))
        descripcion = _esc(it.get("descripcion", ""))
        unit = float(it.get("precio_unitario", 0))
        impuestos = float(it.get("impuestos", 0))
        total_linea = cantidad * unit
        total_general += total_linea
        total_impuestos += impuestos
        filas += (
            f"<tr>"
            f"<td class='c'>{i}</td>"
            f"<td class='c'>Servicio</td>"
            f"<td class='c'>{cantidad:g}</td>"
            f"<td>{descripcion}</td>"
            f"<td class='r'>{unit:,.2f}</td>"
            f"<td class='r'>0.00</td>"
            f"<td class='r'>0.00</td>"
            f"<td class='r'>{impuestos:,.2f}</td>"
            f"<td class='r'>{total_linea:,.2f}</td>"
            f"</tr>"
        )

    html = f"""<!doctype html>
<html lang='es'>
<head>
<meta charset='utf-8'/>
<title>Factura</title>
<style>
:root{{--blue:#0b5ed7;--border:#d1d5db;--light:#f3f4f6;--text:#111827;--muted:#6b7280;}}
body{{font-family:Arial,Helvetica,sans-serif;background:#fff;color:var(--text);}}
.wrap{{width:900px;margin:18px auto;}}
.actions{{display:flex;justify-content:flex-end;margin-bottom:10px;}}
button{{background:var(--blue);border:0;color:#fff;padding:10px 14px;border-radius:10px;font-weight:700;cursor:pointer;}}
.sheet{{border:1px solid var(--border);padding:18px;}}
.title{{text-align:center;color:var(--blue);font-weight:800;letter-spacing:.3px;font-size:18px;margin:2px 0 12px;}}
.topline{{border-top:2px solid var(--border);margin:10px 0 14px;}}
.row{{display:flex;gap:14px;align-items:flex-start;}}
.col{{flex:1;}}
.blueblock{{color:var(--blue);font-weight:700;font-size:12px;line-height:1.35;}}
.rightbox{{text-align:right;font-size:12px;line-height:1.35;}}
.label{{color:var(--blue);font-weight:800;}}
.hr{{border-top:1px solid var(--border);margin:14px 0;}}
.meta{{display:flex;gap:14px;}}
.meta .box{{flex:1;border:1px solid var(--border);padding:10px;font-size:12px;line-height:1.45;}}
table{{width:100%;border-collapse:collapse;font-size:12px;margin-top:12px;}}
th,td{{border:1px solid var(--border);padding:8px;}}
th{{background:var(--light);font-weight:800;}}
.c{{text-align:center;}}
.r{{text-align:right;}}
.totals{{width:320px;margin-left:auto;margin-top:10px;border:1px solid var(--border);}}
.totals div{{display:flex;justify-content:space-between;padding:8px 10px;border-top:1px solid var(--border);font-size:12px;}}
.totals div:first-child{{border-top:0;}}
.note{{margin-top:10px;font-size:11px;color:var(--muted);}}
.foot{{margin-top:12px;display:flex;gap:12px;}}
.cert{{flex:1;border:1px solid var(--border);padding:10px;font-size:12px;}}
.qr{{width:160px;height:160px;border:1px solid var(--border);display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:12px;}}
@media print{{.actions{{display:none;}}.wrap{{width:auto;margin:0;}}.sheet{{border:0;padding:0;}}}}
</style>
</head>
<body>
<div class='wrap'>
  <div class='actions'><button onclick='window.print()'>Imprimir</button></div>
  <div class='sheet'>
    <div class='title'>Factura Pequeño Contribuyente</div>
    <div class='topline'></div>
    <div class='row'>
      <div class='col blueblock'>
        {_esc(EMISOR_BLOQUE_AZUL['nombre'])}<br/>
        Nit Emisor: {_esc(EMISOR_BLOQUE_AZUL['nit'])}<br/>
        {_esc(EMISOR_BLOQUE_AZUL['comercial'])}<br/>
        {_esc(EMISOR_BLOQUE_AZUL['dir1'])}<br/>
        {_esc(EMISOR_BLOQUE_AZUL['dir2'])}
      </div>
      <div class='col rightbox'>
        <div class='label'>NÚMERO DE AUTORIZACIÓN:</div>
        <div style='font-weight:800;margin-top:4px;'>{auth}</div>
        <div style='margin-top:10px;color:var(--blue);font-weight:800;'>Serie: {SERIE_FIJA} &nbsp;&nbsp; Número de DTE: {DTE_FIJO}</div>
      </div>
    </div>
    <div class='hr'></div>
    <div class='meta'>
      <div class='box'><b>NIT Receptor:</b> {_esc(nit_receptor)}<br/><b>Nombre Receptor:</b> {_esc(nombres)} {_esc(apellidos)}</div>
      <div class='box' style='text-align:right;'><b>Fecha y hora de emisión:</b> {now}<br/><b>Fecha y hora de certificación:</b> {now}<br/><b>Moneda:</b> GTQ</div>
    </div>
    <table>
      <thead>
        <tr>
          <th class='c'>#No</th><th class='c'>B/S</th><th class='c'>Cantidad</th><th>Descripción</th>
          <th class='r'>P. Unitario con IVA (Q)</th><th class='r'>Descuentos (Q)</th><th class='r'>Otros Descuentos (Q)</th>
          <th class='r'>Impuestos</th><th class='r'>Total (Q)</th>
        </tr>
      </thead>
      <tbody>
        {filas}
      </tbody>
    </table>
    <div class='totals'>
      <div><b>Descuentos (Q)</b><span>0.00</span></div>
      <div><b>Otros Descuentos (Q)</b><span>0.00</span></div>
      <div><b>Total IVA (Q)</b><span>{total_impuestos:,.2f}</span></div>
      <div><b>Total General (Q)</b><span>{total_general:,.2f}</span></div>
    </div>
    <div class='note'>* No genera derecho a crédito fiscal</div>
    <div class='foot'>
      <div class='cert'><b>Datos del certificador</b><br/>Superintendencia de Administración Tributaria &nbsp; NIT: 16693949</div>
      <div class='qr'> <img src='../qr_sat.png' alt='QR' style='width:100%;height:100%;object-fit:contain;'></div>
    </div>
  </div>
</div>
</body>
</html>"""

    fname = f"factura_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    path = os.path.abspath(os.path.join(carpeta, fname))
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    webbrowser.open("file:///" + path.replace("\\", "/"))
    return path
