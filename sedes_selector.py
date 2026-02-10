import tkinter as tk
from tkinter import messagebox
import db
from inventario import InventarioWindow

BG_PRIMARY = "#fff5f7"
BG_SECONDARY = "#f3d6dc"
BG_CARDS = "#ffffff"
ACCENT = "#da5d86"
TEXT = "#0b1011"
TEXT_MUTED = "#4b5563"
BUTTONS = "#01a6b2"
BUTTONS_SECONDARY = "#028a94"


def bind_click_recursive(widget, callback):
    widget.bind("<Button-1>", callback)
    for child in widget.winfo_children():
        bind_click_recursive(child, callback)


def _hover_bg(widget, normal_bg, hover_bg):
    def _enter(_):
        try:
            widget.config(bg=hover_bg)
        except Exception:
            pass

    def _leave(_):
        try:
            widget.config(bg=normal_bg)
        except Exception:
            pass

    widget.bind("<Enter>", _enter)
    widget.bind("<Leave>", _leave)


class NiceDialog(tk.Toplevel):
    def __init__(self, parent, title=""):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.configure(bg=BG_PRIMARY)
        self.resizable(False, False)
        self.transient(parent)
        self.result = None

        self.protocol("WM_DELETE_WINDOW", self._cancel)

        self.card = tk.Frame(
            self, bg=BG_CARDS,
            highlightthickness=1,
            highlightbackground=BG_SECONDARY
        )
        self.card.pack(padx=22, pady=22, fill="both", expand=True)

        self.header = tk.Frame(self.card, bg=BG_CARDS)
        self.header.pack(fill="x", padx=26, pady=(22, 10))

        tk.Label(
            self.header, text=title,
            bg=BG_CARDS, fg=TEXT,
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w")

        self.body = tk.Frame(self.card, bg=BG_CARDS)
        self.body.pack(fill="both", expand=True, padx=26, pady=10)

        self.footer = tk.Frame(self.card, bg=BG_CARDS)
        self.footer.pack(fill="x", padx=26, pady=(16, 26))

        self.grab_set()
        self._center()

    def _center(self):
        self.update_idletasks()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()
        px = self.parent.winfo_rootx()
        py = self.parent.winfo_rooty()

        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1 or h <= 1:
            w = self.winfo_reqwidth()
            h = self.winfo_reqheight()

        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _cancel(self):
        self.result = None
        self.destroy()


class ConfirmLogoutDialog(NiceDialog):
    """
    Confirmación premium de cerrar sesión.
    result=True si confirma; None si cancela.
    """
    def __init__(self, parent, username="Usuario"):
        super().__init__(parent, "Cerrar sesión")

        self.geometry("610x330")
        self.minsize(610, 330)
        self.update_idletasks()
        self._center()

        alert = tk.Frame(self.body, bg=BG_PRIMARY, highlightthickness=1, highlightbackground=BG_SECONDARY)
        alert.pack(fill="x", pady=(6, 12))

        icon_wrap = tk.Frame(alert, bg=BG_PRIMARY)
        icon_wrap.pack(side="left", padx=16, pady=14)

        c = tk.Canvas(icon_wrap, width=44, height=44, bg=BG_PRIMARY, highlightthickness=0)
        c.pack()
        c.create_oval(4, 4, 40, 40, fill=ACCENT, outline=ACCENT)
        c.create_text(22, 22, text="!", fill="white", font=("Segoe UI", 18, "bold"))

        text_wrap = tk.Frame(alert, bg=BG_PRIMARY)
        text_wrap.pack(side="left", fill="both", expand=True, padx=(0, 16), pady=14)

        tk.Label(
            text_wrap,
            text=f"¿Deseas cerrar sesión, {username}?",
            bg=BG_PRIMARY, fg=TEXT,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w")

        tk.Label(
            text_wrap,
            text="Vas a salir del sistema y volverás a la pantalla de inicio.",
            bg=BG_PRIMARY, fg=TEXT_MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(6, 0))

        # ---- BOTONES MÁS VISIBLES (AQUÍ ESTÁ EL CAMBIO) ----
        # Hacemos un "contenedor" para que queden alineados y grandes
        btn_row = tk.Frame(self.footer, bg=BG_CARDS)
        btn_row.pack(fill="x")

        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)

        btn_cancel = tk.Button(
            btn_row, text="Cancelar",
            bg=BG_SECONDARY, fg=TEXT, bd=0,
            cursor="hand2",
            font=("Segoe UI", 12, "bold"),
            command=self._cancel
        )
        btn_cancel.grid(row=0, column=0, sticky="we", padx=(0, 10), ipady=14)
        _hover_bg(btn_cancel, BG_SECONDARY, "#eac7cf")

        btn_ok = tk.Button(
            btn_row, text="Cerrar sesión",
            bg=ACCENT, fg="white", bd=0,
            activebackground="#c84f76",
            cursor="hand2",
            font=("Segoe UI", 12, "bold"),
            command=self._ok
        )
        btn_ok.grid(row=0, column=1, sticky="we", padx=(10, 0), ipady=14)
        _hover_bg(btn_ok, ACCENT, "#c84f76")

        # Teclas rápidas
        self.bind("<Escape>", lambda e: self._cancel())
        self.bind("<Return>", lambda e: self._ok())

    def _ok(self):
        self.result = True
        self.destroy()


class NuevaSedeDialog(NiceDialog):
    def __init__(self, parent):
        super().__init__(parent, "Crear nueva sede")

        self.geometry("650x450")
        self.minsize(650, 450)
        self.update_idletasks()
        self._center()

        tk.Label(
            self.body,
            text="Agrega los datos de la nueva sede. Luego podrás entrar al inventario de esa sede.",
            bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 18))

        form = tk.Frame(self.body, bg=BG_CARDS)
        form.pack(fill="x")

        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        tk.Label(
            form, text="Nombre de la sede",
            bg=BG_CARDS, fg=TEXT_MUTED,
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=0, sticky="w")

        self.e_nombre = tk.Entry(
            form, font=("Segoe UI", 12), bd=0,
            highlightthickness=1, highlightbackground=BG_SECONDARY,
            highlightcolor=BUTTONS
        )
        self.e_nombre.grid(row=1, column=0, sticky="ew", ipady=10, pady=(6, 16), padx=(0, 12))

        tk.Label(
            form, text="Ubicación",
            bg=BG_CARDS, fg=TEXT_MUTED,
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=1, sticky="w")

        self.e_ubic = tk.Entry(
            form, font=("Segoe UI", 12), bd=0,
            highlightthickness=1, highlightbackground=BG_SECONDARY,
            highlightcolor=BUTTONS
        )
        self.e_ubic.grid(row=1, column=1, sticky="ew", ipady=10, pady=(6, 16), padx=(12, 0))

        preview = tk.Frame(
            self.body, bg=BG_PRIMARY,
            highlightthickness=1, highlightbackground=BG_SECONDARY
        )
        preview.pack(fill="x", pady=(10, 0))

        tk.Label(
            preview, text="Vista previa",
            bg=BG_PRIMARY, fg=TEXT_MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=14, pady=(12, 4))

        self.p_title = tk.Label(
            preview, text="Nombre de sede",
            bg=BG_PRIMARY, fg=TEXT,
            font=("Segoe UI", 16, "bold")
        )
        self.p_title.pack(anchor="w", padx=14)

        self.p_sub = tk.Label(
            preview, text="Ubicación",
            bg=BG_PRIMARY, fg=TEXT_MUTED,
            font=("Segoe UI", 11, "bold")
        )
        self.p_sub.pack(anchor="w", padx=14, pady=(0, 14))

        self.e_nombre.bind("<KeyRelease>", self._update_preview)
        self.e_ubic.bind("<KeyRelease>", self._update_preview)

        btn_cancel = tk.Button(
            self.footer, text="Cancelar",
            bg=BG_SECONDARY, fg=TEXT, bd=0,
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            command=self._cancel
        )
        btn_cancel.pack(side="left", ipadx=20, ipady=10)
        _hover_bg(btn_cancel, BG_SECONDARY, "#eac7cf")

        btn_ok = tk.Button(
            self.footer, text="Crear sede",
            bg=BUTTONS, fg="white", bd=0,
            activebackground=BUTTONS_SECONDARY,
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            command=self._ok
        )
        btn_ok.pack(side="right", ipadx=20, ipady=10)
        _hover_bg(btn_ok, BUTTONS, BUTTONS_SECONDARY)

        self.e_nombre.focus_force()

    def _update_preview(self, _=None):
        self.p_title.config(text=self.e_nombre.get().strip() or "Nombre de sede")
        self.p_sub.config(text=self.e_ubic.get().strip() or "Ubicación")

    def _ok(self):
        nombre = self.e_nombre.get().strip()
        ubic = self.e_ubic.get().strip() or "Ubicación"
        if not nombre:
            messagebox.showwarning("Falta nombre", "Escribe el nombre de la sede.", parent=self)
            return
        self.result = {"nombre": nombre, "ubicacion": ubic}
        self.destroy()


class EliminarSedeDialog(NiceDialog):
    def __init__(self, parent):
        super().__init__(parent, "Eliminar sede")

        self.geometry("650x320")
        self.minsize(650, 320)
        self.update_idletasks()
        self._center()

        tk.Label(
            self.body,
            text="Escribe el nombre EXACTO de la sede a eliminar",
            bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 12))

        self.e_nombre = tk.Entry(
            self.body, font=("Segoe UI", 12), bd=0,
            highlightthickness=1, highlightbackground=BG_SECONDARY,
            highlightcolor=ACCENT
        )
        self.e_nombre.pack(fill="x", ipady=10)

        tk.Label(
            self.body,
            text="Si hay varias sedes con ese nombre, luego podrás elegir cuál eliminar.",
            bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(14, 0))

        btn_cancel = tk.Button(
            self.footer, text="Cancelar",
            bg=BG_SECONDARY, fg=TEXT, bd=0,
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            command=self._cancel
        )
        btn_cancel.pack(side="left", ipadx=20, ipady=10)
        _hover_bg(btn_cancel, BG_SECONDARY, "#eac7cf")

        btn_ok = tk.Button(
            self.footer, text="Buscar sede",
            bg=ACCENT, fg="white", bd=0,
            activebackground="#c84f76",
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            command=self._ok
        )
        btn_ok.pack(side="right", ipadx=20, ipady=10)
        _hover_bg(btn_ok, ACCENT, "#c84f76")

        self.e_nombre.focus_force()

    def _ok(self):
        nombre = self.e_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Falta nombre", "Escribe el nombre de la sede.", parent=self)
            return
        self.result = {"nombre": nombre}
        self.destroy()


class ElegirSedeDialog(NiceDialog):
    def __init__(self, parent, opciones):
        super().__init__(parent, "Elige cuál sede eliminar")

        self.geometry("700x380")
        self.minsize(700, 380)
        self.update_idletasks()
        self._center()

        tk.Label(
            self.body,
            text="Hay más de una sede con ese nombre. Selecciona una:",
            bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        self.listbox = tk.Listbox(
            self.body, font=("Segoe UI", 11), bd=0,
            highlightthickness=1, highlightbackground=BG_SECONDARY,
            activestyle="none", height=min(10, len(opciones))
        )
        self.listbox.pack(fill="both", expand=True, pady=(10, 10))

        self.opciones = opciones
        for sid, nombre, ubic in opciones:
            self.listbox.insert("end", f"{nombre}  —  {ubic}   (ID: {sid})")

        btn_cancel = tk.Button(
            self.footer, text="Cancelar",
            bg=BG_SECONDARY, fg=TEXT, bd=0,
            cursor="hand2", font=("Segoe UI", 11, "bold"),
            command=self._cancel
        )
        btn_cancel.pack(side="left", ipadx=20, ipady=10)
        _hover_bg(btn_cancel, BG_SECONDARY, "#eac7cf")

        btn_ok = tk.Button(
            self.footer, text="Eliminar esta",
            bg=ACCENT, fg="white", bd=0,
            activebackground="#c84f76",
            cursor="hand2", font=("Segoe UI", 11, "bold"),
            command=self._ok
        )
        btn_ok.pack(side="right", ipadx=20, ipady=10)
        _hover_bg(btn_ok, ACCENT, "#c84f76")

        if opciones:
            self.listbox.selection_set(0)

    def _ok(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Selecciona una", "Selecciona una sede de la lista.", parent=self)
            return
        idx = sel[0]
        sid, nombre, ubic = self.opciones[idx]
        self.result = {"id": sid, "nombre": nombre, "ubicacion": ubic}
        self.destroy()


class SeleccionSede(tk.Toplevel):
    CARD_W = 360
    CARD_H = 190
    CARD_PADX = 18
    CARD_PADY = 18
    MAX_COLS = 2

    def __init__(self, master=None, user_info=None, on_logout=None):
        super().__init__(master)
        self.title("Selección de sede")
        self.configure(bg=BG_PRIMARY)
        self.resizable(True, True)

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w = int(sw * 0.85)
        h = int(sh * 0.85)
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(900, 600)

        self.user_info = user_info or {}
        self.user_role = self.user_info.get("role", "dependiente")
        self.username = self.user_info.get("username", "Usuario")
        self.on_logout = on_logout

        self.protocol("WM_DELETE_WINDOW", self._cerrar_sesion)

        db.crear_tabla_sedes()
        db.ensure_sedes_iniciales()

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = tk.Frame(self, bg=BG_PRIMARY)
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(16, 0))
        header.grid_columnconfigure(1, weight=1)

        # ✅ HEADER como estaba (simple)
        tk.Button(
            header, text="Cerrar sesión",
            bg=ACCENT, fg="white", bd=0,
            activebackground="#c84f76",
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            command=self._cerrar_sesion
        ).grid(row=0, column=0, ipadx=12, ipady=8, sticky="w")

        role_text = "Administrador" if self.user_role == "administrador" else "Dependiente"
        tk.Label(
            header,
            text=f"Bienvenido: {self.username}  |  {role_text}",
            bg=BG_PRIMARY, fg=TEXT_MUTED,
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=1, sticky="e")

        tk.Label(
            self, text="Selección de sede",
            bg=BG_PRIMARY, fg=TEXT,
            font=("Segoe UI", 32, "bold")
        ).grid(row=1, column=0, pady=(12, 8))

        panel = tk.Frame(self, bg=BG_PRIMARY)
        panel.grid(row=2, column=0, sticky="nsew", padx=28, pady=22)
        panel.grid_rowconfigure(0, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        outer_card = tk.Frame(panel, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        outer_card.grid(row=0, column=0, sticky="nsew")
        outer_card.grid_rowconfigure(0, weight=1)
        outer_card.grid_rowconfigure(1, weight=0)
        outer_card.grid_columnconfigure(0, weight=1)

        content = tk.Frame(outer_card, bg=BG_CARDS)
        content.grid(row=0, column=0, sticky="nsew", padx=24, pady=(24, 10))
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(content, bg=BG_CARDS, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.scroll = tk.Scrollbar(content, orient="vertical", command=self.canvas.yview)
        self.scroll.grid(row=0, column=1, sticky="ns")

        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.scrollable = tk.Frame(self.canvas, bg=BG_CARDS)
        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable, anchor="nw")

        self.scrollable.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

        bottom = tk.Frame(outer_card, bg=BG_CARDS)
        bottom.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 18))
        bottom.grid_columnconfigure(1, weight=1)

        if self.user_role == "administrador":
            tk.Button(
                bottom, text="Eliminar sede",
                bg=BG_SECONDARY, fg=TEXT, bd=0,
                cursor="hand2",
                font=("Segoe UI", 11, "bold"),
                command=self._eliminar
            ).grid(row=0, column=0, sticky="w", ipadx=14, ipady=10)

            tk.Button(
                bottom, text="Nueva sede",
                bg=BUTTONS, fg="white", bd=0,
                activebackground=BUTTONS_SECONDARY,
                cursor="hand2",
                font=("Segoe UI", 11, "bold"),
                command=self._nueva
            ).grid(row=0, column=2, sticky="e", ipadx=14, ipady=10)

        self._render()

    def _on_frame_configure(self, _):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mousewheel(self):
        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self):
        self.unbind_all("<MouseWheel>")

    def _render(self):
        for w in self.scrollable.winfo_children():
            w.destroy()

        sedes = db.listar_sedes()

        for i in range(self.MAX_COLS):
            self.scrollable.grid_columnconfigure(i, weight=1)

        row = col = 0
        for sid, nombre, ubicacion in sedes:
            wrap = tk.Frame(self.scrollable, bg=BG_CARDS)
            wrap.grid(row=row, column=col, padx=self.CARD_PADX, pady=self.CARD_PADY, sticky="nsew")

            card = tk.Frame(
                wrap, bg=BG_PRIMARY,
                width=self.CARD_W, height=self.CARD_H,
                highlightthickness=1, highlightbackground=BG_SECONDARY,
                cursor="hand2"
            )
            card.pack()
            card.pack_propagate(False)

            inner = tk.Frame(card, bg=BG_PRIMARY)
            inner.pack(expand=True)

            tk.Label(
                inner, text=nombre,
                bg=BG_PRIMARY, fg=TEXT,
                font=("Segoe UI", 20, "bold")
            ).pack(pady=(6, 6))

            tk.Label(
                inner, text=ubicacion,
                bg=BG_PRIMARY, fg=TEXT_MUTED,
                font=("Segoe UI", 11, "bold")
            ).pack()

            def _open(event, i=sid):
                self._abrir_inventario(i)

            bind_click_recursive(card, _open)

            col += 1
            if col >= self.MAX_COLS:
                col = 0
                row += 1

        self.canvas.yview_moveto(0)

    def _abrir_inventario(self, sede_id):
        self.withdraw()
        InventarioWindow(self, sede_id, user_role=self.user_role, on_back=self._volver)

    def _volver(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _nueva(self):
        dlg = NuevaSedeDialog(self)
        self.wait_window(dlg)
        if not dlg.result:
            return

        nombre = dlg.result["nombre"]
        ubicacion = dlg.result["ubicacion"]

        db.insertar_sede(nombre, ubicacion)
        self._render()

    def _eliminar(self):
        dlg = EliminarSedeDialog(self)
        self.wait_window(dlg)
        if not dlg.result:
            return

        nombre_buscado = dlg.result["nombre"].strip().lower()

        sedes = db.listar_sedes()
        matches = [
            (sid, nombre, ubic) for (sid, nombre, ubic) in sedes
            if nombre.strip().lower() == nombre_buscado
        ]

        if not matches:
            messagebox.showinfo("No encontrada", "No existe una sede con ese nombre.", parent=self)
            return

        if len(matches) > 1:
            pick = ElegirSedeDialog(self, matches)
            self.wait_window(pick)
            if not pick.result:
                return
            sede_id = pick.result["id"]
            sede_nombre = pick.result["nombre"]
        else:
            sede_id = matches[0][0]
            sede_nombre = matches[0][1]

        if not messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar la sede '{sede_nombre}' y su inventario?",
            parent=self
        ):
            return

        db.eliminar_sede(sede_id)
        self._render()

    def _cerrar_sesion(self):
        dlg = ConfirmLogoutDialog(self, username=self.username)
        self.wait_window(dlg)
        if not dlg.result:
            return

        self.destroy()
        if callable(self.on_logout):
            self.on_logout()
