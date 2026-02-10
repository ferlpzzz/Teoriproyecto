import tkinter as tk
import tkinter.ttk as ttk
from datetime import date, timedelta
import db

BG_PRIMARY = '#fccfd4'
BG_SECONDARY = '#fccfd4'
BG_CARDS = '#fccfd4'
ACCENT = '#da5d86'
TEXT = '#0b1011'
BUTTONS = '#01a6b2'
BUTTONS_SECONDARY = '#01a6b2'
SUCCESS = '#7CE5A3'
WARNING = '#FFD6A5'
ERROR = '#FFB7B7'


class ReportesWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Reportes")
        self.geometry("1366x768")
        self.configure(bg=BG_PRIMARY)
        self.resizable(False, False)

        btn_salir = tk.Button(self, text="x", bg=BUTTONS, fg=TEXT, bd=0, cursor="hand2", command=self.destroy)
        btn_salir.place(x=1340, y=18, width=28, height=28)

        cont = tk.Frame(self, bg=BG_CARDS)
        cont.pack(expand=True, fill="both", padx=16, pady=16)

        tk.Label(
            cont,
            text="Reportes (Ventas + Citas)",
            bg=BG_CARDS, fg=TEXT,
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(0, 10))

        filtros = tk.Frame(cont, bg=BG_CARDS)
        filtros.pack(fill="x", padx=6, pady=(2, 8))

        tk.Label(filtros, text="Sede:", bg=BG_CARDS).pack(side="left", padx=(0, 6))
        sedes = [("0", "Todas")] + [(str(sid), nombre) for sid, nombre in db.listar_sedes_simple()]
        self.var_sede = tk.StringVar(value="0")
        cb_sede = ttk.Combobox(filtros, state="readonly",
                               values=[f"{sid} - {nom}" for sid, nom in sedes], width=30)
        cb_sede.pack(side="left", padx=(0, 12))
        cb_sede.current(0)

        tk.Button(filtros, text="Diario (hoy)", bg=BUTTONS, bd=0,
                  command=lambda: self._aplicar_rango("diario", cb_sede)).pack(side="left", padx=4)
        tk.Button(filtros, text="Últimos 7 días", bg=BUTTONS, bd=0,
                  command=lambda: self._aplicar_rango("7d", cb_sede)).pack(side="left", padx=4)
        tk.Button(filtros, text="Mensual (actual)", bg=BUTTONS, bd=0,
                  command=lambda: self._aplicar_rango("mensual", cb_sede)).pack(side="left", padx=4)
        tk.Button(filtros, text="Anual (actual)", bg=BUTTONS, bd=0,
                  command=lambda: self._aplicar_rango("anual", cb_sede)).pack(side="left", padx=4)

        self.badge = tk.Label(cont, text="Rango: —",
                              bg=BUTTONS, fg="white", font=("Segoe UI", 10, "bold"))
        self.badge.pack(fill="x", padx=6, pady=(0, 8))

        tabla_frame = tk.Frame(cont, bg=BG_CARDS)
        tabla_frame.pack(expand=True, fill="both", padx=6, pady=6)

        cols = ("Tipo", "Concepto", "Cant/Cliente", "P.Unitario", "Total", "Fecha")
        self.tree = ttk.Treeview(tabla_frame, columns=cols, show="headings", height=18)
        for c, w in zip(cols, (80, 330, 160, 100, 100, 120)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)

        total_frame = tk.Frame(cont, bg=BG_CARDS)
        total_frame.pack(fill="x", padx=6, pady=(6, 0))

        self.lbl_tv = tk.Label(total_frame, text="Total ventas: Q 0.00", bg=BG_CARDS, font=("Segoe UI", 10, "bold"))
        self.lbl_tc = tk.Label(total_frame, text="Total citas: Q 0.00", bg=BG_CARDS, font=("Segoe UI", 10, "bold"))
        self.lbl_tt = tk.Label(total_frame, text="TOTAL: Q 0.00", bg=BG_CARDS, font=("Segoe UI", 12, "bold"))

        self.lbl_tv.pack(side="left", padx=8)
        self.lbl_tc.pack(side="left", padx=8)
        self.lbl_tt.pack(side="right", padx=8)

        self._calcular_y_mostrar("diario", "0")

    def _aplicar_rango(self, modo, cb_sede):
        try:
            sel = cb_sede.get().split(" - ", 1)[0].strip()
        except Exception:
            sel = "0"
        self._calcular_y_mostrar(modo, sel)

    def _calcular_y_mostrar(self, modo: str, sede_id_str: str):
        hoy = date.today()
        if modo == "diario":
            fmin = hoy.strftime("%Y-%m-%d")
            fmax = hoy.strftime("%Y-%m-%d")
            rango_txt = f"Hoy ({fmin})"
        elif modo == "7d":
            ini = hoy - timedelta(days=6)
            fmin = ini.strftime("%Y-%m-%d")
            fmax = hoy.strftime("%Y-%m-%d")
            rango_txt = f"Últimos 7 días ({fmin} a {fmax})"
        elif modo == "mensual":
            ini = date(hoy.year, hoy.month, 1)
            if hoy.month == 12:
                fin = date(hoy.year + 1, 1, 1) - timedelta(days=1)
            else:
                fin = date(hoy.year, hoy.month + 1, 1) - timedelta(days=1)
            fmin = ini.strftime("%Y-%m-%d")
            fmax = fin.strftime("%Y-%m-%d")
            rango_txt = f"Mes actual ({fmin} a {fmax})"
        else:  # anual
            ini = date(hoy.year, 1, 1)
            fin = date(hoy.year, 12, 31)
            fmin = ini.strftime("%Y-%m-%d")
            fmax = fin.strftime("%Y-%m-%d")
            rango_txt = f"Año actual ({fmin} a {fmax})"

        self.badge.config(text=f"Rango: {rango_txt}")

        sede_id = int(sede_id_str or "0")

        for i in self.tree.get_children():
            self.tree.delete(i)

        ventas = db.listar_ventas_rango(fmin, fmax, sede_id if sede_id != 0 else None)
        total_v = 0.0
        for (vid, sede, prod, cant, punit, total, ffecha) in ventas:
            total_v += float(total or 0.0)
            self.tree.insert("", "end",
                             values=("Venta", prod, str(cant), f"{punit:.2f}", f"{total:.2f}", ffecha))

        citas = db.listar_citas_rango(fmin, fmax, sede_id if sede_id != 0 else None)
        total_c = 0.0
        for (cid, sede, cliente, servicio, precio, inicio, fin, ffecha) in citas:
            total_c += float(precio or 0.0)
            concepto = f"{servicio} ({inicio}-{fin})"
            self.tree.insert("", "end",
                             values=("Cita", concepto, cliente, f"{precio:.2f}", f"{precio:.2f}", ffecha))

        self.lbl_tv.config(text=f"Total ventas: Q {total_v:.2f}")
        self.lbl_tc.config(text=f"Total citas: Q {total_c:.2f}")
        self.lbl_tt.config(text=f"TOTAL: Q {(total_v + total_c):.2f}")