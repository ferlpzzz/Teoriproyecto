import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from datetime import date
import datetime

try:
    from tkcalendar import Calendar
except Exception:
    Calendar = None

import db
import factura_html

BG_PRIMARY = "#fff5f7"
BG_SECONDARY = "#f3d6dc"
BG_CARDS = "#ffffff"
TEXT = "#0b1011"
TEXT_MUTED = "#4b5563"
TEXT_BTN = "white"
BUTTONS = "#01a6b2"
BUTTONS_HOVER = "#028a94"
DANGER = "#d85a7a"


def _apply_ttk_styles(root: tk.Misc):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(".", foreground=TEXT)
    style.configure(
        "Soft.Treeview",
        background=BG_CARDS,
        fieldbackground=BG_CARDS,
        foreground=TEXT,
        rowheight=30,
        borderwidth=0
    )
    style.map(
        "Soft.Treeview",
        background=[("selected", BG_SECONDARY)],
        foreground=[("selected", TEXT)]
    )
    style.configure(
        "Soft.Treeview.Heading",
        font=("Segoe UI", 10, "bold"),
        foreground=TEXT,
        background=BG_SECONDARY,
        relief="flat"
    )
    style.configure("Soft.TCombobox", padding=8)


def _t2m(hhmm: str):
    s = (hhmm or "").strip()
    if len(s) != 5 or s[2] != ":":
        return None
    try:
        return int(s[:2]) * 60 + int(s[3:])
    except Exception:
        return None


def _m2t(minutes: int):
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"


def _inicios():
    vals = []
    t = 9 * 60
    end = 19 * 60
    while t < end:
        vals.append(_m2t(t))
        t += 30
    return vals


def _fines_desde(inicio_hhmm: str):
    m0 = _t2m(inicio_hhmm)
    if m0 is None:
        return []
    vals = []
    t = m0 + 30
    end = 19 * 60
    while t <= end:
        vals.append(_m2t(t))
        t += 30
    return vals


INICIOS = _inicios()


def _overlap(a0, a1, b0, b1):
    return a0 < b1 and b0 < a1


def _listar_servicios_safe(sede_id):
    try:
        return db.listar_servicios(sede_id)
    except Exception:
        return []


def _listar_empleadas_safe(sede_id):
    for intento in (
        lambda: db.listar_empleadas(sede_id),
        lambda: db.listar_empleadas(sede_id, True),
        lambda: db.listar_empleadas(sede_id, solo_activas=True),
        lambda: db.listar_empleadas(sede_id, solo_activas=1),
    ):
        try:
            rows = intento()
            if rows is None:
                continue
            return rows
        except Exception:
            continue
    return []


def _citas_del_dia(sede_id, fecha_iso):
    try:
        return db.listar_citas(sede_id, fecha_iso) or []
    except Exception:
        return []


def _norm_empleadas(rows):
    out = []
    for r in rows or []:
        try:
            if isinstance(r, (list, tuple)):
                if len(r) >= 2:
                    nombre = r[1]
                else:
                    nombre = r[0]
            else:
                nombre = r
            nombre = (nombre or "").strip()
            if nombre:
                out.append(nombre)
        except Exception:
            pass
    return out


def _cita_unpack(row):
    cid = None
    inicio = ""
    fin = ""
    empleada = ""

    if not isinstance(row, (list, tuple)) or len(row) < 1:
        return cid, inicio, fin, empleada

    try:
        cid = int(row[0])
    except Exception:
        cid = None

    if len(row) >= 5:
        inicio = (row[3] or "").strip()
        fin = (row[4] or "").strip()
    elif len(row) >= 4:
        inicio = (row[3] or "").strip()

    if len(row) >= 7:
        empleada = (row[6] or "").strip()
    elif len(row) == 6:
        empleada = (row[5] or "").strip()

    return cid, inicio, fin, empleada


def _empleadas_disponibles_intervalo(sede_id, fecha_iso, inicio, fin, excluir_cid=None):
    inicio = (inicio or "").strip()
    fin = (fin or "").strip()

    if inicio not in INICIOS:
        return []
    if fin not in _fines_desde(inicio):
        return []

    n0 = _t2m(inicio)
    n1 = _t2m(fin)
    if n0 is None or n1 is None or n1 <= n0:
        return []

    emp_rows = _listar_empleadas_safe(sede_id)
    empleadas = _norm_empleadas(emp_rows)
    if not empleadas:
        return []

    citas = _citas_del_dia(sede_id, fecha_iso)
    libres = []

    for emp in empleadas:
        ok = True
        for row in citas:
            cid, cinicio, cfin, cemp = _cita_unpack(row)
            if excluir_cid is not None and cid is not None and int(cid) == int(excluir_cid):
                continue

            if (cemp or "").strip().lower() != (emp or "").strip().lower():
                continue

            c0 = _t2m(cinicio)
            c1 = _t2m(cfin)

            if c0 is None or c1 is None:
                continue

            if _overlap(n0, n1, c0, c1):
                ok = False
                break

        if ok:
            libres.append(emp)

    return libres


class ConfirmDialog(tk.Toplevel):
    def __init__(self, parent, title, message, danger_text="Eliminar"):
        super().__init__(parent)
        self.result = False

        self.title(title)
        self.configure(bg=BG_PRIMARY)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        w, h = 540, 400
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        wrap = tk.Frame(self, bg=BG_PRIMARY)
        wrap.pack(fill="both", expand=True, padx=16, pady=16)

        card = tk.Frame(wrap, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        card.pack(fill="both", expand=True)

        inner = tk.Frame(card, bg=BG_CARDS)
        inner.pack(fill="both", expand=True, padx=18, pady=18)

        top = tk.Frame(inner, bg=BG_CARDS)
        top.pack(fill="x")

        tk.Label(top, text="⚠", bg=BG_CARDS, fg=DANGER, font=("Segoe UI", 22, "bold")).pack(side="left", padx=(0, 12))

        texts = tk.Frame(top, bg=BG_CARDS)
        texts.pack(side="left", fill="both", expand=True)

        tk.Label(texts, text=title, bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(
            texts, text=message, bg=BG_CARDS, fg=TEXT_MUTED,
            font=("Segoe UI", 11), justify="left", wraplength=390
        ).pack(anchor="w", pady=(6, 0))

        actions = tk.Frame(wrap, bg=BG_PRIMARY)
        actions.pack(fill="x", pady=(12, 0))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        tk.Button(
            actions, text="Cancelar", bg=BG_SECONDARY, fg=TEXT, bd=0, cursor="hand2",
            font=("Segoe UI", 12, "bold"), command=self._cancel
        ).grid(row=0, column=0, sticky="ew", ipady=16, padx=(0, 10))

        tk.Button(
            actions, text=danger_text, bg=DANGER, fg=TEXT_BTN, bd=0, cursor="hand2",
            font=("Segoe UI", 12, "bold"), activebackground=DANGER, command=self._ok
        ).grid(row=0, column=1, sticky="ew", ipady=16, padx=(10, 0))

        self.bind("<Escape>", lambda e: self._cancel())
        self.bind("<Return>", lambda e: self._ok())

    def _cancel(self):
        self.result = False
        self.destroy()

    def _ok(self):
        self.result = True
        self.destroy()



class FacturaDatosDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None

        self.title("Facturación")
        self.configure(bg=BG_PRIMARY)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        w, h = 620, 500
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        wrap = tk.Frame(self, bg=BG_PRIMARY)
        wrap.pack(fill="both", expand=True, padx=18, pady=18)

        card = tk.Frame(wrap, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        card.pack(fill="both", expand=True)

        inner = tk.Frame(card, bg=BG_CARDS)
        inner.pack(fill="both", expand=True, padx=18, pady=18)
        inner.grid_columnconfigure(0, weight=1)

        tk.Label(inner, text="Datos para facturación", bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 14))

        self.var_nit = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_apellidos = tk.StringVar()

        tk.Label(inner, text="NIT (9 dígitos)", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w")
        tk.Entry(inner, textvariable=self.var_nit, relief="flat", bg=BG_PRIMARY, fg=TEXT, font=("Segoe UI", 11)).grid(row=2, column=0, sticky="ew", ipady=12, pady=(6, 14))

        tk.Label(inner, text="Nombre", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky="w")
        tk.Entry(inner, textvariable=self.var_nombre, relief="flat", bg=BG_PRIMARY, fg=TEXT, font=("Segoe UI", 11)).grid(row=4, column=0, sticky="ew", ipady=12, pady=(6, 14))

        tk.Label(inner, text="Apellidos", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).grid(row=5, column=0, sticky="w")
        tk.Entry(inner, textvariable=self.var_apellidos, relief="flat", bg=BG_PRIMARY, fg=TEXT, font=("Segoe UI", 11)).grid(row=6, column=0, sticky="ew", ipady=12, pady=(6, 18))

        actions = tk.Frame(wrap, bg=BG_PRIMARY)
        actions.pack(fill="x", pady=(12, 0))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        tk.Button(
            actions, text="Cancelar", bg=BG_SECONDARY, fg=TEXT, bd=0, cursor="hand2",
            font=("Segoe UI", 12, "bold"), command=self._cancel
        ).grid(row=0, column=0, sticky="ew", ipady=14, padx=(0, 10))

        tk.Button(
            actions, text="Continuar", bg=BUTTONS, fg=TEXT_BTN, bd=0, cursor="hand2",
            font=("Segoe UI", 12, "bold"), activebackground=BUTTONS_HOVER, command=self._ok
        ).grid(row=0, column=1, sticky="ew", ipady=14, padx=(10, 0))

        self.bind("<Escape>", lambda e: self._cancel())
        self.bind("<Return>", lambda e: self._ok())

    def _cancel(self):
        self.result = None
        self.destroy()

    def _ok(self):
        nit = self.var_nit.get().strip()
        if not nit.isdigit() or len(nit) != 9:
            messagebox.showerror("NIT inválido", "El NIT debe contener exactamente 9 dígitos numéricos.")
            return

        nombre = self.var_nombre.get().strip()
        apellidos = self.var_apellidos.get().strip()
        if not nombre or not apellidos:
            messagebox.showerror("Datos incompletos", "Completa Nombre y Apellidos.")
            return

        self.result = {"nit": nit, "nombre": nombre, "apellidos": apellidos}
        self.destroy()

class SearchableDropdown(tk.Frame):
    def __init__(self, parent, var, values, on_pick=None):
        super().__init__(parent, bg=BG_CARDS)
        self.var = var
        self.values_all = list(values or [])
        self.on_pick = on_pick
        self.popup = None
        self.listbox = None

        self.entry = tk.Entry(self, textvariable=self.var, relief="flat", bg=BG_PRIMARY, fg=TEXT, font=("Segoe UI", 11))
        self.entry.pack(side="left", fill="x", expand=True, ipady=12)

        self.btn = tk.Button(
            self, text="▼", bg=BG_SECONDARY, fg=TEXT, bd=0, cursor="hand2",
            font=("Segoe UI", 10, "bold"), activebackground=BG_SECONDARY, command=self._toggle
        )
        self.btn.pack(side="left", padx=(8, 0), ipady=8, ipadx=10)

        self.entry.bind("<KeyRelease>", self._on_type)
        self.entry.bind("<Down>", self._open)
        self.entry.bind("<Return>", self._pick_active)
        self.entry.bind("<Escape>", lambda e: self._close())

    def _toggle(self):
        if self.popup:
            self._close()
        else:
            self._open()

    def _open(self, e=None):
        if self.popup:
            self._refresh()
            return

        self.popup = tk.Toplevel(self)
        self.popup.overrideredirect(True)
        self.popup.configure(bg=BG_SECONDARY)

        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height() + 2
        w = self.entry.winfo_width() + self.btn.winfo_width() + 8
        h = 220
        self.popup.geometry(f"{w}x{h}+{x}+{y}")

        border = tk.Frame(self.popup, bg=BG_SECONDARY)
        border.pack(fill="both", expand=True, padx=1, pady=1)

        self.listbox = tk.Listbox(
            border, bd=0, highlightthickness=0, activestyle="none",
            bg=BG_CARDS, fg=TEXT, selectbackground=BG_SECONDARY, selectforeground=TEXT,
            font=("Segoe UI", 10)
        )
        self.listbox.pack(fill="both", expand=True)

        self.listbox.bind("<ButtonRelease-1>", lambda e: self._pick_active())
        self.listbox.bind("<Return>", lambda e: self._pick_active())
        self.listbox.bind("<Escape>", lambda e: self._close())

        self._refresh()
        self.listbox.focus_set()

    def _close(self):
        if self.popup:
            try:
                self.popup.destroy()
            except Exception:
                pass
        self.popup = None
        self.listbox = None

    def _filtered(self):
        t = (self.var.get() or "").strip().lower()
        if not t:
            return self.values_all
        return [v for v in self.values_all if t in (v or "").lower()]

    def _refresh(self):
        if not self.listbox:
            return
        vals = self._filtered()
        self.listbox.delete(0, "end")
        for v in vals:
            self.listbox.insert("end", v)
        if vals:
            self.listbox.selection_set(0)
            self.listbox.activate(0)

    def _on_type(self, e=None):
        self._open()
        self._refresh()

    def _pick_active(self, e=None):
        if not self.listbox:
            return
        sel = self.listbox.curselection()
        if not sel:
            return
        value = self.listbox.get(sel[0])
        self.var.set(value)
        if self.on_pick:
            self.on_pick(value)
        self._close()
        self.entry.icursor("end")
        self.entry.focus_set()


class CitaDialog(tk.Toplevel):
    def __init__(self, parent, sede_id, fecha_iso, user_role="dependiente", cid=None, prefill=None):
        super().__init__(parent)
        self.result = None
        self.sede_id = int(sede_id)
        self.fecha_iso = fecha_iso
        self.user_role = user_role
        self.cid = cid

        try:
            db.crear_tabla_citas()
            db.asegurar_columnas_citas()
            db.crear_tabla_servicios()
            db.seed_servicios()
            db.crear_tabla_empleadas()
            db.seed_empleadas()
        except Exception:
            pass

        self.title("Cita")
        self.configure(bg=BG_PRIMARY)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        w, h = 820, 660
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        wrap = tk.Frame(self, bg=BG_PRIMARY)
        wrap.pack(fill="both", expand=True, padx=18, pady=18)

        head = tk.Frame(wrap, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        head.pack(fill="x", pady=(0, 10))
        tk.Label(
            head,
            text="Editar cita" if cid else "Nueva cita",
            bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 16, "bold")
        ).pack(anchor="w", padx=18, pady=(14, 2))
        tk.Label(
            head,
            text=f"Fecha: {fecha_iso}",
            bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=18, pady=(0, 14))

        body = tk.Frame(wrap, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        body.pack(fill="both", expand=True)
        inner = tk.Frame(body, bg=BG_CARDS)
        inner.pack(fill="both", expand=True, padx=18, pady=18)
        inner.grid_columnconfigure(0, weight=1)
        inner.grid_columnconfigure(1, weight=1)

        servicios = _listar_servicios_safe(self.sede_id)
        nombres_servicios = [s[1] for s in servicios]

        if prefill is None:
            prefill = {}

        ini0 = prefill.get("inicio", INICIOS[0] if INICIOS else "09:00")
        if ini0 not in INICIOS and INICIOS:
            ini0 = INICIOS[0]

        fin_vals0 = _fines_desde(ini0)
        fin0 = prefill.get("fin", fin_vals0[0] if fin_vals0 else "")
        if fin0 not in fin_vals0:
            fin0 = fin_vals0[0] if fin_vals0 else ""

        self.v_cliente = tk.StringVar(value=prefill.get("cliente", ""))
        self.v_servicio = tk.StringVar(value=prefill.get("servicio", ""))
        try:
            self.v_precio = tk.StringVar(value=f"{float(prefill.get('precio', 0.0)):.2f}")
        except Exception:
            self.v_precio = tk.StringVar(value="0.00")
        self.v_inicio = tk.StringVar(value=ini0)
        self.v_fin = tk.StringVar(value=fin0)
        self.v_empleada = tk.StringVar(value=prefill.get("empleada", ""))

        tk.Label(inner, text="Cliente", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        e_cliente = tk.Entry(inner, textvariable=self.v_cliente, relief="flat", bg=BG_PRIMARY, fg=TEXT, font=("Segoe UI", 11))
        e_cliente.grid(row=1, column=0, columnspan=2, sticky="ew", ipady=12, pady=(6, 18))

        tk.Label(inner, text="Servicio", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w")

        self._servicios_all = list(nombres_servicios)

        def _on_pick_servicio(_v=None):
            nombre = (self.v_servicio.get() or "").strip()
            for _s_id, s_nom, s_pre in servicios:
                if (s_nom or "").strip() == nombre:
                    try:
                        self.v_precio.set(f"{float(s_pre):.2f}")
                    except Exception:
                        self.v_precio.set("0.00")
                    break

        self.serv_picker = SearchableDropdown(inner, self.v_servicio, self._servicios_all, on_pick=_on_pick_servicio)
        self.serv_picker.grid(row=3, column=0, sticky="ew", pady=(6, 18), padx=(0, 12))

        tk.Label(inner, text="Precio", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).grid(row=2, column=1, sticky="w")
        e_precio = tk.Entry(inner, textvariable=self.v_precio, relief="flat", bg=BG_PRIMARY, fg=TEXT, font=("Segoe UI", 11))
        e_precio.grid(row=3, column=1, sticky="ew", ipady=12, pady=(6, 18), padx=(12, 0))

        tk.Label(inner, text="Hora inicio", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).grid(row=4, column=0, sticky="w")
        self.cb_inicio = ttk.Combobox(inner, textvariable=self.v_inicio, state="readonly", style="Soft.TCombobox", values=INICIOS)
        self.cb_inicio.grid(row=5, column=0, sticky="ew", pady=(6, 18), padx=(0, 12))

        tk.Label(inner, text="Hora fin", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).grid(row=4, column=1, sticky="w")
        self.cb_fin = ttk.Combobox(inner, textvariable=self.v_fin, state="readonly", style="Soft.TCombobox", values=_fines_desde(self.v_inicio.get()))
        self.cb_fin.grid(row=5, column=1, sticky="ew", pady=(6, 18), padx=(12, 0))

        emp_row = tk.Frame(inner, bg=BG_CARDS)
        emp_row.grid(row=6, column=0, columnspan=2, sticky="ew")
        emp_row.grid_columnconfigure(0, weight=1)

        tk.Label(emp_row, text="Empleada", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.cb_empleada = ttk.Combobox(emp_row, textvariable=self.v_empleada, state="readonly", style="Soft.TCombobox", values=[])
        self.cb_empleada.grid(row=1, column=0, sticky="ew", pady=(6, 0), padx=(0, 12))

        if self.user_role == "administrador":
            tk.Button(
                emp_row, text="+", bg=BUTTONS, fg=TEXT_BTN, bd=0, cursor="hand2",
                font=("Segoe UI", 13, "bold"), activebackground=BUTTONS_HOVER,
                command=self._add_empleada
            ).grid(row=1, column=1, ipady=12, ipadx=20, pady=(6, 0))

        self.lbl_info = tk.Label(inner, text="", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold"))
        self.lbl_info.grid(row=7, column=0, columnspan=2, sticky="w", pady=(18, 0))

        actions = tk.Frame(wrap, bg=BG_PRIMARY)
        actions.pack(fill="x", pady=(12, 0))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        tk.Button(
            actions, text="Cancelar", bg=BG_SECONDARY, fg=TEXT, bd=0, cursor="hand2",
            font=("Segoe UI", 12, "bold"), command=self._cancel
        ).grid(row=0, column=0, sticky="ew", ipady=18, padx=(0, 12))

        tk.Button(
            actions, text="Guardar", bg=BUTTONS, fg=TEXT_BTN, bd=0, cursor="hand2",
            font=("Segoe UI", 12, "bold"), activebackground=BUTTONS_HOVER, command=self._ok
        ).grid(row=0, column=1, sticky="ew", ipady=18, padx=(12, 0))

        def _sync_fin(_=None):
            ini = (self.v_inicio.get() or "").strip()
            vals = _fines_desde(ini)
            self.cb_fin["values"] = vals
            if vals:
                if self.v_fin.get() not in vals:
                    self.v_fin.set(vals[0])
            else:
                self.v_fin.set("")
            self._refresh_empleadas()

        self.cb_inicio.bind("<<ComboboxSelected>>", _sync_fin)
        self.cb_fin.bind("<<ComboboxSelected>>", lambda e: self._refresh_empleadas())

        _on_pick_servicio()
        self._refresh_empleadas()

        self.bind("<Escape>", lambda e: self._cancel())
        self.bind("<Return>", lambda e: self._ok())
        e_cliente.focus_set()

    def _refresh_empleadas(self):
        todas = _norm_empleadas(_listar_empleadas_safe(self.sede_id))
        libres = _empleadas_disponibles_intervalo(
            self.sede_id, self.fecha_iso, self.v_inicio.get(), self.v_fin.get(), excluir_cid=self.cid
        )

        self.cb_empleada["values"] = libres

        if not todas:
            self.v_empleada.set("")
            self.lbl_info.config(text="No hay empleadas registradas para esta sede.")
            return

        if not libres:
            self.v_empleada.set("")
            self.lbl_info.config(text="No hay empleadas disponibles para ese horario.")
            return

        cur = (self.v_empleada.get() or "").strip()
        if cur not in libres:
            self.v_empleada.set(libres[0])
        self.lbl_info.config(text=f"Disponibles: {', '.join(libres)}")

    def _add_empleada(self):
        top = tk.Toplevel(self)
        top.title("Nueva empleada")
        top.configure(bg=BG_PRIMARY)
        top.resizable(False, False)
        top.transient(self)
        top.grab_set()

        w, h = 520, 400
        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()
        top.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        wrap = tk.Frame(top, bg=BG_PRIMARY)
        wrap.pack(fill="both", expand=True, padx=16, pady=16)

        card = tk.Frame(wrap, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        card.pack(fill="both", expand=True)

        inner = tk.Frame(card, bg=BG_CARDS)
        inner.pack(fill="both", expand=True, padx=18, pady=18)

        tk.Label(inner, text="Nueva empleada", bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(inner, text="Nombre", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(14, 6))

        v = tk.StringVar(value="")
        ent = tk.Entry(inner, textvariable=v, relief="flat", bg=BG_PRIMARY, fg=TEXT, font=("Segoe UI", 11))
        ent.pack(fill="x", ipady=12)

        actions = tk.Frame(wrap, bg=BG_PRIMARY)
        actions.pack(fill="x", pady=(12, 0))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        def _cancel():
            top.destroy()

        def _save():
            nombre = (v.get() or "").strip()
            if not nombre:
                messagebox.showwarning("Validación", "Ingresa un nombre.")
                return
            try:
                db.agregar_empleada(self.sede_id, nombre)
                top.destroy()
                self._refresh_empleadas()
                vals = list(self.cb_empleada["values"] or [])
                if nombre in vals:
                    self.v_empleada.set(nombre)
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(
            actions, text="Cancelar", bg=BG_SECONDARY, fg=TEXT, bd=0, cursor="hand2",
            font=("Segoe UI", 12, "bold"), command=_cancel
        ).grid(row=0, column=0, sticky="ew", ipady=18, padx=(0, 12))

        tk.Button(
            actions, text="Guardar", bg=BUTTONS, fg=TEXT_BTN, bd=0, cursor="hand2",
            font=("Segoe UI", 12, "bold"), activebackground=BUTTONS_HOVER, command=_save
        ).grid(row=0, column=1, sticky="ew", ipady=18, padx=(12, 0))

        top.bind("<Escape>", lambda e: _cancel())
        top.bind("<Return>", lambda e: _save())
        ent.focus_set()

    def _cancel(self):
        self.result = None
        self.destroy()

    def _ok(self):
        cliente = (self.v_cliente.get() or "").strip()
        servicio = (self.v_servicio.get() or "").strip()
        inicio = (self.v_inicio.get() or "").strip()
        fin = (self.v_fin.get() or "").strip()
        empleada = (self.v_empleada.get() or "").strip()

        try:
            precio = float((self.v_precio.get() or "0").strip())
        except Exception:
            precio = -1

        if not cliente or not servicio:
            messagebox.showwarning("Validación", "Completa cliente y servicio.")
            return
        if inicio not in INICIOS:
            messagebox.showwarning("Validación", "Selecciona una hora de inicio válida.")
            return
        if fin not in _fines_desde(inicio):
            messagebox.showwarning("Validación", "Selecciona una hora de fin válida.")
            return
        if not empleada:
            messagebox.showwarning("Validación", "Selecciona una empleada.")
            return
        if precio < 0:
            messagebox.showwarning("Validación", "Precio inválido.")
            return

        todas = _norm_empleadas(_listar_empleadas_safe(self.sede_id))
        libres = _empleadas_disponibles_intervalo(self.sede_id, self.fecha_iso, inicio, fin, excluir_cid=self.cid)

        if todas and not libres:
            messagebox.showwarning("Validación", "No hay empleadas disponibles para ese horario.")
            return

        if empleada not in libres:
            messagebox.showwarning("Validación", "La empleada no está disponible en ese horario.")
            return

        self.result = (cliente, servicio, inicio, fin, precio, empleada)
        self.destroy()


class CitasFrame(tk.Frame):
    def __init__(self, master, sede_id: int, user_role="dependiente"):
        super().__init__(master, bg=BG_PRIMARY)
        self.sede_id = int(sede_id)
        self.user_role = user_role
        _apply_ttk_styles(self)

        try:
            db.crear_tabla_citas()
            db.asegurar_columnas_citas()
            db.crear_tabla_servicios()
            db.seed_servicios()
            db.crear_tabla_empleadas()
            db.seed_empleadas()
        except Exception:
            pass

        wrapper = tk.Frame(self, bg=BG_PRIMARY)
        wrapper.pack(fill="both", expand=True, padx=14, pady=14)

        head = tk.Frame(wrapper, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        head.pack(fill="x", pady=(0, 10))

        sede = None
        try:
            sede = db.obtener_sede(self.sede_id)
        except Exception:
            sede = None

        titulo = f"Citas — {sede[1]}" if sede else "Citas"
        tk.Label(head, text=titulo, bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=14, pady=(12, 2))
        tk.Label(head, text="Selecciona un día y gestiona tus citas.", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(0, 12))

        body = tk.Frame(wrapper, bg=BG_PRIMARY)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        left_card = tk.Frame(body, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        left_card.grid(row=0, column=0, sticky="ns", padx=(0, 2))

        right_card = tk.Frame(body, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(2, 0))

        if Calendar is None:
            tk.Label(
                left_card,
                text="Falta tkcalendar\nInstala: pip install tkcalendar",
                bg=BG_CARDS, fg=DANGER,
                font=("Segoe UI", 12, "bold"),
                justify="center"
            ).pack(expand=True, fill="both", padx=14, pady=14)
            self.cal = None
        else:
            hoy = date.today()
            cal_kwargs = dict(
                selectmode="day",
                date_pattern="yyyy-mm-dd",
                showweeknumbers=False,
                font=("Segoe UI", 9),
                headersfont=("Segoe UI", 9, "bold"),
                bordercolor=BG_SECONDARY
            )

            try:
                cal_kwargs.update(
                    background=BG_CARDS,
                    foreground=TEXT,
                    headersbackground=BG_SECONDARY,
                    headersforeground=TEXT,
                    normalbackground=BG_CARDS,
                    normalforeground=TEXT,
                    weekendbackground=BG_PRIMARY,
                    weekendforeground=TEXT,
                    selectbackground=BUTTONS,
                    selectforeground=TEXT_BTN,
                    othermonthbackground=BG_CARDS,
                    othermonthforeground=TEXT_MUTED,
                    othermonthweforeground=TEXT_MUTED
                )
            except Exception:
                pass

            try:
                self.cal = Calendar(left_card, **cal_kwargs)
            except Exception:
                self.cal = Calendar(left_card, selectmode="day", date_pattern="yyyy-mm-dd", showweeknumbers=False)

            self.cal.selection_set(hoy)
            self.cal.pack(padx=12, pady=12, anchor="n")
            tk.Frame(left_card, bg=BG_CARDS).pack(fill="both", expand=True)
            self.cal.bind("<<CalendarSelected>>", lambda e: self._cargar())

        top_r = tk.Frame(right_card, bg=BG_CARDS)
        top_r.pack(fill="x", padx=8, pady=(8, 4))
        self.badge = tk.Label(top_r, text="", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold"))
        self.badge.pack(side="left")

        btns = tk.Frame(right_card, bg=BG_CARDS)
        btns.pack(fill="x", padx=8, pady=(0, 6))

        def mk_btn(texto, cmd, primary=False):
            bg = BUTTONS if primary else BG_SECONDARY
            fg = TEXT_BTN if primary else TEXT
            abg = BUTTONS_HOVER if primary else BG_SECONDARY
            return tk.Button(
                btns, text=texto, bg=bg, fg=fg, bd=0, cursor="hand2",
                font=("Segoe UI", 11, "bold"), activebackground=abg, command=cmd
            )

        self.btn_nueva = mk_btn("+ NUEVA", self._nueva, primary=True)
        self.btn_editar = mk_btn("EDITAR", self._editar)
        self.btn_atender = mk_btn("ATENDER / FACTURAR", self._atender_facturar, primary=True)
        self.btn_cancelar = mk_btn("CANCELAR", self._cancelar, primary=False)
        self.btn_recargar = mk_btn("RECARGAR", self._cargar)

        self.btn_nueva.pack(side="left", padx=(0, 10), ipady=10, ipadx=18)
        self.btn_editar.pack(side="left", padx=(0, 10), ipady=10, ipadx=18)
        self.btn_atender.pack(side="left", padx=(0, 10), ipady=10, ipadx=18)
        self.btn_cancelar.pack(side="left", padx=(0, 10), ipady=10, ipadx=18)
        self.btn_recargar.pack(side="left", ipady=10, ipadx=18)

        self.tree = ttk.Treeview(
            right_card,
            columns=("Cliente", "Servicio", "Precio (Q)", "Hora", "Empleada", "Estado"),
            show="headings",
            style="Soft.Treeview"
        )
        self.tree.heading("Cliente", text="Cliente")
        self.tree.heading("Servicio", text="Servicio")
        self.tree.heading("Precio (Q)", text="Precio (Q)")
        self.tree.heading("Hora", text="Hora")
        self.tree.heading("Empleada", text="Empleada")
        self.tree.heading("Estado", text="Estado")

        self.tree.column("Cliente", width=240, anchor="w")
        self.tree.column("Servicio", width=280, anchor="w")
        self.tree.column("Precio (Q)", width=120, anchor="center")
        self.tree.column("Hora", width=190, anchor="center")
        self.tree.column("Empleada", width=170, anchor="center")
        self.tree.column("Estado", width=120, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        try:
            self.tree.tag_configure("atendida", foreground=TEXT_MUTED)
        except Exception:
            pass
        self.tree.bind("<Double-1>", lambda e: self._editar())
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._sync_actions())

        self.cache = {}
        self._cargar()
        self._sync_actions()

    def _sync_actions(self):
        cid = self._sel_id()
        estado = ""
        if cid and cid in self.cache:
            estado = str(self.cache[cid].get("estado", "")).upper()

        if not cid:
            try:
                self.btn_editar.config(state="disabled")
                self.btn_atender.config(state="disabled")
                self.btn_cancelar.config(state="disabled")
            except Exception:
                pass
            return

        if estado == "ATENDIDA":
            try:
                self.btn_editar.config(state="disabled")
                self.btn_atender.config(state="disabled")
                self.btn_cancelar.config(state="disabled")
            except Exception:
                pass
        else:
            try:
                self.btn_editar.config(state="normal")
                self.btn_atender.config(state="normal")
                self.btn_cancelar.config(state="normal")
            except Exception:
                pass

    def _fecha(self):
        if self.cal:
            return str(self.cal.get_date()).strip()[:10]
        return date.today().isoformat()

    def _cargar(self):
        fecha = self._fecha()

        for i in self.tree.get_children():
            self.tree.delete(i)
        self.cache = {}

        try:
            rows = db.listar_citas(self.sede_id, fecha) or []
        except Exception as e:
            rows = []
            messagebox.showerror("Error", str(e))

        self.badge.config(text=f"Fecha: {fecha}")

        for row in rows:
            try:
                if isinstance(row, (list, tuple)) and len(row) >= 8:
                    cid, cliente, servicio, inicio, fin, precio, empleada, estado = row[:8]
                elif isinstance(row, (list, tuple)) and len(row) == 7:
                    cid, cliente, servicio, inicio, fin, precio, empleada = row
                    estado = 'PENDIENTE'
                elif isinstance(row, (list, tuple)) and len(row) == 6:
                    cid, cliente, servicio, inicio, fin, precio = row
                    empleada = ""
                    estado = 'PENDIENTE'
                elif isinstance(row, (list, tuple)) and len(row) == 5:
                    cid, cliente, servicio, inicio, fin = row
                    precio = 0.0
                    empleada = ""
                    estado = 'PENDIENTE'
                else:
                    continue

                self.cache[int(cid)] = {
                    "cliente": cliente,
                    "servicio": servicio,
                    "inicio": inicio,
                    "fin": fin,
                    "precio": float(precio or 0.0),
                    "empleada": empleada,
                    "estado": (estado or 'PENDIENTE')
                }

                tag = "atendida" if str(estado or '').upper() == 'ATENDIDA' else ""

                self.tree.insert(
                    "", "end", iid=str(cid),
                    values=(cliente, servicio, f"{float(precio or 0.0):.2f}", f"{inicio} - {fin}", (empleada or "—"), (estado or 'PENDIENTE')),
                    tags=(tag,) if tag else ()
                )
            except Exception:
                pass

        self._sync_actions()

    def _sel_id(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def _nueva(self):
        fecha = self._fecha()
        dlg = CitaDialog(self.winfo_toplevel(), self.sede_id, fecha, self.user_role, cid=None, prefill=None)
        self.winfo_toplevel().wait_window(dlg)

        if not dlg.result:
            return
        cliente, servicio, inicio, fin, precio, empleada = dlg.result

        sid = None
        sn = None
        for s_id, s_nombre, _s_precio in _listar_servicios_safe(self.sede_id):
            if (s_nombre or "").strip() == (servicio or "").strip():
                sid = s_id
                sn = s_nombre
                break

        try:
            try:
                db.insertar_cita(
                    self.sede_id, fecha, cliente, servicio, inicio, fin,
                    servicio_id=sid, servicio_nombre=sn, precio=float(precio), empleada=empleada
                )
            except TypeError:
                db.insertar_cita(self.sede_id, fecha, cliente, servicio, inicio, fin, sid, sn, float(precio), empleada)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self._cargar()

    def _editar(self):
        cid = self._sel_id()
        if not cid:
            messagebox.showwarning("Editar", "Selecciona una cita.")
            return

        fecha = self._fecha()
        prefill = self.cache.get(cid)
        if prefill and str(prefill.get('estado','')).upper() == 'ATENDIDA':
            messagebox.showinfo('Cita', 'Esta cita ya fue atendida y no se puede editar.')
            return
        if not prefill:
            self._cargar()
            prefill = self.cache.get(cid, {})

        dlg = CitaDialog(self.winfo_toplevel(), self.sede_id, fecha, self.user_role, cid=cid, prefill=prefill)
        self.winfo_toplevel().wait_window(dlg)

        if not dlg.result:
            return
        cliente, servicio, inicio, fin, precio, empleada = dlg.result

        sid = None
        sn = None
        for s_id, s_nombre, _s_precio in _listar_servicios_safe(self.sede_id):
            if (s_nombre or "").strip() == (servicio or "").strip():
                sid = s_id
                sn = s_nombre
                break

        try:
            try:
                db.actualizar_cita(
                    cid, cliente, servicio, inicio, fin,
                    servicio_id=sid, servicio_nombre=sn, precio=float(precio), empleada=empleada
                )
            except TypeError:
                db.actualizar_cita(cid, cliente, servicio, inicio, fin, sid, sn, float(precio), empleada)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self._cargar()


    def _atender_facturar(self):
        cid = self._sel_id()
        if not cid:
            messagebox.showwarning("Atender", "Selecciona una cita.")
            return

        info = self.cache.get(cid) or {}
        if str(info.get("estado", "")).upper() == "ATENDIDA":
            messagebox.showinfo("Atender", "Esta cita ya fue atendida y facturada.")
            return

        cliente = (info.get("cliente") or "").strip()
        servicio = (info.get("servicio") or "").strip()
        precio = float(info.get("precio") or 0.0)

        dlg = ConfirmDialog(
            self.winfo_toplevel(),
            "Marcar como atendida",
            f"Se generará la factura para la cita de {cliente} por el servicio: {servicio}.\n\n¿Deseas continuar?",
            danger_text="Sí, atender"
        )
        self.winfo_toplevel().wait_window(dlg)
        if not dlg.result:
            return

        fd = FacturaDatosDialog(self.winfo_toplevel())
        self.winfo_toplevel().wait_window(fd)
        if not fd.result:
            return

        nit = fd.result["nit"]
        nombre = fd.result["nombre"]
        apellidos = fd.result["apellidos"]

        items = [{
            "cantidad": 1,
            "descripcion": servicio,
            "precio_unitario": precio,
            "impuestos": 0.0
        }]

        try:
            factura_html.abrir_factura_en_navegador(nit, nombre, apellidos, items, carpeta="facturas_html")
        except Exception as e:
            messagebox.showerror("Factura", str(e))
            return

        try:
            facturado_en = datetime.datetime.now().isoformat(timespec="seconds")
            db.marcar_cita_atendida(cid, nit, nombre, apellidos, facturado_en)
        except Exception as e:
            messagebox.showerror("Cita", str(e))
            return

        self._cargar()

    def _cancelar(self):
        cid = self._sel_id()
        if not cid:
            messagebox.showwarning('Cancelar', 'Selecciona una cita.')
            return
        info = self.cache.get(cid) or {}
        if str(info.get('estado','')).upper() == 'ATENDIDA':
            messagebox.showinfo('Cancelar', 'Esta cita ya fue atendida y no se puede cancelar.')
            return
        nombre = (info.get('cliente') or '').strip() or 'este cliente'
        h = f"{(info.get('inicio') or '').strip()} - {(info.get('fin') or '').strip()}".strip(' -')
        dlg = ConfirmDialog(
            self.winfo_toplevel(),
            'Cancelar cita',
            f"¿Deseas cancelar la cita de {nombre} ({h})?\n\nSe eliminará del calendario.",
            danger_text='Sí, cancelar'
        )
        self.winfo_toplevel().wait_window(dlg)
        if not dlg.result:
            return
        try:
            db.eliminar_cita(cid)
        except Exception as e:
            messagebox.showerror('Error', str(e))
            return
        self._cargar()

    def _eliminar(self):
        cid = self._sel_id()
        if not cid:
            messagebox.showwarning("Eliminar", "Selecciona una cita.")
            return

        nombre = "esta cita"
        info = self.cache.get(cid)
        if info and str(info.get('estado','')).upper() == 'ATENDIDA':
            messagebox.showinfo('Eliminar', 'Esta cita ya fue atendida y no se puede eliminar.')
            return
        if info:
            c = (info.get("cliente") or "").strip()
            h = f"{(info.get('inicio') or '').strip()} - {(info.get('fin') or '').strip()}".strip(" -")
            if c and h:
                nombre = f"la cita de {c} ({h})"
            elif c:
                nombre = f"la cita de {c}"

        dlg = ConfirmDialog(
            self.winfo_toplevel(),
            "Eliminar cita",
            f"¿Estás segura de eliminar {nombre}?\n\nEsta acción no se puede deshacer.",
            danger_text="Sí, eliminar"
        )
        self.winfo_toplevel().wait_window(dlg)
        if not dlg.result:
            return

        try:
            db.eliminar_cita(cid)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self._cargar()
