import tkinter as tk
from tkinter import ttk, messagebox
import db
from side_bar import SideBar
from ventas import VentasFrame
from citas import CitasFrame
from usuarios import UsuariosFrame

BG_PRIMARY = "#fff5f7"
BG_SECONDARY = "#f3d6dc"
BG_CARDS = "#ffffff"
ACCENT = "#da5d86"
TEXT = "#0b1011"
TEXT_MUTED = "#4b5563"
BUTTONS = "#01a6b2"
BUTTONS_SECONDARY = "#028a94"
WARNING = "#f3d6dc"


def _apply_ttk_styles(root: tk.Misc):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except:
        pass

    style.configure(".", foreground=TEXT)

    style.configure(
        "Soft.Treeview",
        background=BG_CARDS,
        fieldbackground=BG_CARDS,
        foreground=TEXT,
        rowheight=32,
        borderwidth=0
    )
    style.map(
        "Soft.Treeview",
        background=[("selected", BG_SECONDARY)],
        foreground=[("selected", TEXT)]
    )

    style.configure(
        "Soft.Treeview.Heading",
        font=("Segoe UI", 11, "bold"),
        foreground=TEXT,
        background=BG_SECONDARY,
        relief="flat"
    )

    style.configure("Soft.TCombobox", padding=6)
    style.map(
        "Soft.TCombobox",
        fieldbackground=[("readonly", "white")],
        background=[("readonly", "white")]
    )


class CategoriaDialog(tk.Toplevel):
    """
    Ventana bonita para crear una nueva categoría.
    Retorna self.result con el nombre (str) o None.
    """
    def __init__(self, master, title="Nueva categoría"):
        super().__init__(master)
        self.result = None

        self.title(title)
        self.configure(bg=BG_PRIMARY)
        self.resizable(False, False)

        _apply_ttk_styles(self)

        # Card contenedor
        card = tk.Frame(self, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        card.pack(padx=22, pady=20, fill="both", expand=True)

        header = tk.Frame(card, bg=BG_CARDS)
        header.pack(fill="x", padx=20, pady=(18, 10))

        tk.Label(
            header, text="Crear nueva categoría",
            bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 16, "bold")
        ).pack(anchor="w")

        tk.Label(
            header, text="Organiza tu inventario para trabajar más rápido.",
            bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(4, 0))

        body = tk.Frame(card, bg=BG_CARDS)
        body.pack(fill="x", padx=20, pady=(8, 0))
        body.grid_columnconfigure(0, weight=1)

        tk.Label(
            body, text="Nombre de la categoría",
            bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.var_nombre = tk.StringVar(value="")
        self.ent = tk.Entry(body, textvariable=self.var_nombre, relief="flat", font=("Segoe UI", 11))
        self.ent.grid(row=1, column=0, sticky="we", ipady=6)

        # ✅ Tip orientado a salón de belleza (no médico)
        tip = tk.Frame(card, bg=BG_SECONDARY)
        tip.pack(fill="x", padx=20, pady=(14, 0))

        tk.Label(
            tip, text="Tip:",
            bg=BG_SECONDARY, fg=TEXT, font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(10, 6), pady=10)

        tk.Label(
            tip,
            text="Ejemplos: “Shampoo”, “Tintes”, “Uñas”, “Pestañas”, “Cejas”, “Tratamientos”, “Cabello”.",
            bg=BG_SECONDARY, fg=TEXT, font=("Segoe UI", 10)
        ).pack(side="left", padx=(0, 10), pady=10)

        footer = tk.Frame(card, bg=BG_CARDS)
        footer.pack(fill="x", padx=20, pady=18)

        tk.Button(
            footer, text="Cancelar",
            bg=WARNING, fg=TEXT, bd=0,
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            command=self.destroy
        ).pack(side="right", padx=(10, 0), ipadx=14, ipady=8)

        tk.Button(
            footer, text="Crear",
            bg=BUTTONS, fg="white", bd=0,
            activebackground=BUTTONS_SECONDARY,
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            command=self._crear
        ).pack(side="right", ipadx=16, ipady=8)

        # Enter = crear | Esc = cancelar
        self.bind("<Return>", lambda e: self._crear())
        self.bind("<Escape>", lambda e: self.destroy())

        # Centrar ventana
        self.update_idletasks()
        w = max(self.winfo_reqwidth(), 560)
        h = max(self.winfo_reqheight(), 280)
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (w // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.grab_set()
        self.ent.focus_set()

    def _crear(self):
        nombre = (self.var_nombre.get() or "").strip()
        if not nombre:
            messagebox.showwarning("Validación", "Escribe un nombre para la categoría.")
            return
        if len(nombre) > 40:
            messagebox.showwarning("Validación", "El nombre es demasiado largo (máx. 40).")
            return
        self.result = nombre
        self.destroy()


class ProductoDialog(tk.Toplevel):
    def __init__(self, master, sede_id, title="Producto", initial=None):
        super().__init__(master)
        self.sede_id = int(sede_id)
        self.result = None
        self.title(title)
        self.configure(bg=BG_PRIMARY)
        self.resizable(False, False)

        _apply_ttk_styles(self)

        self.var_nombre = tk.StringVar(value=initial["nombre"] if initial else "")
        self.var_stock = tk.StringVar(value=str(initial["stock"]) if initial else "0")
        self.var_precio = tk.StringVar(value=str(initial["precio"]) if initial else "0.0")
        self.var_cat = tk.StringVar(value=initial.get("categoria", "") if initial else "")

        card = tk.Frame(self, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        card.pack(padx=26, pady=22, expand=True, fill="both")

        frm = tk.Frame(card, bg=BG_CARDS)
        frm.pack(padx=26, pady=24, expand=True, fill="x")
        frm.grid_columnconfigure(1, weight=1)

        tk.Label(frm, text="Nombre:", bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 11, "bold")) \
            .grid(row=0, column=0, sticky="e", padx=10, pady=10)
        tk.Entry(frm, textvariable=self.var_nombre) \
            .grid(row=0, column=1, sticky="we", padx=10, pady=10)

        tk.Label(frm, text="Existencias:", bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 11, "bold")) \
            .grid(row=1, column=0, sticky="e", padx=10, pady=10)
        tk.Entry(frm, textvariable=self.var_stock) \
            .grid(row=1, column=1, sticky="we", padx=10, pady=10)

        tk.Label(frm, text="Precio (Q):", bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 11, "bold")) \
            .grid(row=2, column=0, sticky="e", padx=10, pady=10)
        tk.Entry(frm, textvariable=self.var_precio) \
            .grid(row=2, column=1, sticky="we", padx=10, pady=10)

        tk.Label(frm, text="Categoría:", bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 11, "bold")) \
            .grid(row=3, column=0, sticky="e", padx=10, pady=10)

        cat_row = tk.Frame(frm, bg=BG_CARDS)
        cat_row.grid(row=3, column=1, sticky="we", padx=10, pady=10)
        cat_row.grid_columnconfigure(0, weight=1)

        self.cb = ttk.Combobox(cat_row, textvariable=self.var_cat, state="readonly", style="Soft.TCombobox")
        self.cb.grid(row=0, column=0, sticky="we")

        tk.Button(
            cat_row,
            text="+ Nueva",
            bg=BUTTONS, fg="white", bd=0,
            activebackground=BUTTONS_SECONDARY,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            command=self._crear_categoria
        ).grid(row=0, column=1, padx=(10, 0), ipadx=10, ipady=6)

        botones = tk.Frame(frm, bg=BG_CARDS)
        botones.grid(row=4, column=0, columnspan=2, pady=(18, 0))

        tk.Button(
            botones, text="Guardar",
            bg=BUTTONS, fg="white", bd=0,
            activebackground=BUTTONS_SECONDARY,
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            command=self._guardar
        ).pack(side="left", padx=10, ipadx=18, ipady=10)

        tk.Button(
            botones, text="Cancelar",
            bg=WARNING, fg=TEXT, bd=0,
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            command=self.destroy
        ).pack(side="left", padx=10, ipadx=18, ipady=10)

        self._cats = []
        self._cargar_categorias()

        self.update_idletasks()
        w = max(self.winfo_reqwidth(), 650)
        h = max(self.winfo_reqheight(), 320)
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (w // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.grab_set()

    def _cargar_categorias(self):
        try:
            self._cats = db.listar_categorias_inventario(self.sede_id)
        except Exception:
            self._cats = []

        self.cb["values"] = [n for (_id, n) in self._cats]
        if self.cb["values"]:
            if not (self.var_cat.get() or "").strip():
                self.var_cat.set(self.cb["values"][0])
            else:
                actual = (self.var_cat.get() or "").strip().lower()
                for v in self.cb["values"]:
                    if (v or "").strip().lower() == actual:
                        self.var_cat.set(v)
                        break

    def _crear_categoria(self):
        dlg = CategoriaDialog(self, "Nueva categoría")
        self.wait_window(dlg)

        nombre = dlg.result
        if not nombre:
            return

        existentes = [(n or "").strip().lower() for (_id, n) in self._cats]
        if nombre.lower() in existentes:
            messagebox.showinfo("Categoría", "Esa categoría ya existe.")
            for (_id, n) in self._cats:
                if (n or "").strip().lower() == nombre.lower():
                    self.var_cat.set(n)
                    break
            return

        try:
            db.insertar_categoria_inventario(self.sede_id, nombre)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la categoría.\n\n{e}")
            return

        self._cargar_categorias()
        self.var_cat.set(nombre)

    def _categoria_id(self):
        nombre = (self.var_cat.get() or "").strip().lower()
        for cid, nom in self._cats:
            if (nom or "").strip().lower() == nombre:
                return int(cid)
        return None

    def _guardar(self):
        try:
            nombre = self.var_nombre.get().strip()
            stock = int(self.var_stock.get())
            precio = float(self.var_precio.get())
            if not nombre or stock < 0 or precio < 0:
                raise ValueError
        except Exception:
            messagebox.showwarning("Validación", "Datos inválidos.")
            return

        self.result = (nombre, stock, precio, self._categoria_id())
        self.destroy()


class AjustarExistenciasDialog(tk.Toplevel):
    def __init__(self, master, titulo, producto, stock_actual, maximo=None):
        super().__init__(master)
        self.result = None

        self.title(titulo)
        self.configure(bg=BG_PRIMARY)
        self.resizable(False, False)

        card = tk.Frame(self, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        card.pack(padx=78, pady=58, fill="both", expand=True)

        head = tk.Frame(card, bg=BG_CARDS)
        head.pack(fill="x", padx=44, pady=(36, 18))

        tk.Label(head, text=titulo, bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(head, text=producto, bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8, 0))
        tk.Label(head, text=f"Stock actual: {int(stock_actual)}", bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 0))

        body = tk.Frame(card, bg=BG_CARDS)
        body.pack(fill="x", padx=44, pady=(0, 26))
        body.grid_columnconfigure(0, weight=1)

        tk.Label(body, text="Cantidad", bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.var_cant = tk.StringVar(value="1")
        ent = tk.Entry(body, textvariable=self.var_cant, relief="flat", font=("Segoe UI", 14, "bold"))
        ent.grid(row=1, column=0, sticky="we", ipady=12)

        if maximo is not None:
            tk.Label(body, text=f"Máximo permitido: {int(maximo)}", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(10, 0))

        foot = tk.Frame(card, bg=BG_CARDS)
        foot.pack(fill="x", padx=44, pady=(0, 44))
        foot.grid_columnconfigure(0, weight=1)
        foot.grid_columnconfigure(1, weight=1)

        tk.Button(
            foot,
            text="Cancelar",
            bg=BG_SECONDARY,
            fg=TEXT,
            bd=0,
            cursor="hand2",
            font=("Segoe UI", 12, "bold"),
            command=self.destroy
        ).grid(row=0, column=0, sticky="we", padx=(0, 12), ipady=12)

        tk.Button(
            foot,
            text="Guardar",
            bg=BUTTONS,
            fg="white",
            bd=0,
            activebackground=BUTTONS_SECONDARY,
            cursor="hand2",
            font=("Segoe UI", 12, "bold"),
            command=self._ok
        ).grid(row=0, column=1, sticky="we", padx=(12, 0), ipady=12)

        self.bind("<Return>", lambda e: self._ok())
        self.bind("<Escape>", lambda e: self.destroy())

        self.update_idletasks()
        w = max(self.winfo_reqwidth(), 640)
        h = max(self.winfo_reqheight(), 360)
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (w // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.grab_set()
        ent.focus_set()
        ent.selection_range(0, "end")

    def _ok(self):
        try:
            cant = int((self.var_cant.get() or "").strip())
        except Exception:
            cant = 0

        if cant <= 0:
            messagebox.showwarning("Validación", "Ingresa una cantidad válida.")
            return

        self.result = cant
        self.destroy()


class InventarioView(tk.Frame):
    def __init__(self, master, sede_id, user_role):
        super().__init__(master, bg=BG_PRIMARY)
        self.sede_id = int(sede_id)
        self.user_role = user_role

        panel = tk.Frame(self, bg=BG_PRIMARY)
        panel.pack(expand=True, fill="both", padx=20, pady=20)

        card = tk.Frame(panel, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        card.pack(expand=True, fill="both")

        inner = tk.Frame(card, bg=BG_CARDS)
        inner.pack(expand=True, fill="both", padx=18, pady=16)

        inner.grid_columnconfigure(0, weight=1)
        inner.grid_rowconfigure(2, weight=1)

        sede = db.obtener_sede(self.sede_id)
        titulo = f"Inventario — {sede[1]}" if sede else "Inventario"

        tk.Label(inner, text=titulo, bg=BG_CARDS, fg=TEXT,
                 font=("Segoe UI", 20, "bold")).grid(row=0, column=0, pady=(4, 10), sticky="w")

        # =========================
        # ✅ BARRA FILTROS (RESPONSIVE + LIMPIAR)
        # =========================
        filtros = tk.Frame(inner, bg=BG_SECONDARY)
        filtros.grid(row=1, column=0, sticky="we", pady=(0, 10))

        filtros.grid_columnconfigure(1, weight=2)
        filtros.grid_columnconfigure(6, weight=2)
        filtros.grid_columnconfigure(99, weight=1)

        self.var_buscar = tk.StringVar(value="")
        self.var_ord_por = tk.StringVar(value="Nombre")
        self.var_orden = tk.StringVar(value="Ascendente")
        self.var_cat_filtro = tk.StringVar(value="Todas")
        self.var_stock_bajo = tk.BooleanVar(value=False)
        self.var_precio_min = tk.StringVar(value="")
        self.var_precio_max = tk.StringVar(value="")

        pad_y = 8

        tk.Label(filtros, text="Buscar:", bg=BG_SECONDARY, fg=TEXT, font=("Segoe UI", 10, "bold")) \
            .grid(row=0, column=0, padx=(10, 6), pady=pad_y, sticky="w")

        ent_buscar = tk.Entry(filtros, textvariable=self.var_buscar, relief="flat")
        ent_buscar.grid(row=0, column=1, padx=(0, 12), pady=pad_y, sticky="we", ipady=2)

        tk.Label(filtros, text="Orden:", bg=BG_SECONDARY, fg=TEXT, font=("Segoe UI", 10, "bold")) \
            .grid(row=0, column=2, padx=(0, 6), pady=pad_y, sticky="w")

        cb_ord = ttk.Combobox(
            filtros, textvariable=self.var_ord_por, state="readonly", style="Soft.TCombobox",
            values=["Nombre", "Categoría", "Existencias", "Precio"],
            width=12
        )
        cb_ord.grid(row=0, column=3, padx=(0, 8), pady=pad_y, sticky="w")

        cb_dir = ttk.Combobox(
            filtros, textvariable=self.var_orden, state="readonly", style="Soft.TCombobox",
            values=["Ascendente", "Descendente"],
            width=12
        )
        cb_dir.grid(row=0, column=4, padx=(0, 12), pady=pad_y, sticky="w")

        tk.Label(filtros, text="Categoría:", bg=BG_SECONDARY, fg=TEXT, font=("Segoe UI", 10, "bold")) \
            .grid(row=0, column=5, padx=(0, 6), pady=pad_y, sticky="w")

        self.cb_cat_filtro = ttk.Combobox(
            filtros, textvariable=self.var_cat_filtro, state="readonly", style="Soft.TCombobox",
            width=16
        )
        self.cb_cat_filtro.grid(row=0, column=6, padx=(0, 12), pady=pad_y, sticky="we")

        chk = tk.Checkbutton(
            filtros, text="Stock bajo (<5)", variable=self.var_stock_bajo,
            bg=BG_SECONDARY, fg=TEXT, activebackground=BG_SECONDARY,
            font=("Segoe UI", 10, "bold"), cursor="hand2"
        )
        chk.grid(row=0, column=7, padx=(0, 12), pady=pad_y, sticky="w")

        tk.Button(
            filtros, text="LIMPIAR",
            bg=BUTTONS, fg="white", bd=0,
            activebackground=BUTTONS_SECONDARY,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            command=self._limpiar_filtros
        ).grid(row=0, column=8, padx=(0, 10), pady=pad_y, ipadx=10, ipady=5, sticky="e")

        tk.Label(filtros, text="Precio:", bg=BG_SECONDARY, fg=TEXT, font=("Segoe UI", 10, "bold")) \
            .grid(row=1, column=0, padx=(10, 6), pady=(0, 10), sticky="w")

        ent_pmin = tk.Entry(filtros, textvariable=self.var_precio_min, relief="flat", width=10)
        ent_pmin.grid(row=1, column=1, padx=(0, 6), pady=(0, 10), sticky="w", ipady=2)

        tk.Label(filtros, text="a", bg=BG_SECONDARY, fg=TEXT, font=("Segoe UI", 10, "bold")) \
            .grid(row=1, column=2, padx=(0, 6), pady=(0, 10), sticky="w")

        ent_pmax = tk.Entry(filtros, textvariable=self.var_precio_max, relief="flat", width=10)
        ent_pmax.grid(row=1, column=3, padx=(0, 10), pady=(0, 10), sticky="w", ipady=2)

        # =========================
        # ✅ TABLA (CENTRADA)
        # =========================
        self.tree = ttk.Treeview(
            inner,
            columns=("Producto", "Categoría", "Existencias", "Precio"),
            show="headings",
            style="Soft.Treeview"
        )

        self.tree.heading("Producto", text="Producto", anchor="center")
        self.tree.heading("Categoría", text="Categoría", anchor="center")
        self.tree.heading("Existencias", text="Existencias", anchor="center")
        self.tree.heading("Precio", text="Precio (Q)", anchor="center")

        self.tree.column("Producto", anchor="center")
        self.tree.column("Categoría", anchor="center")
        self.tree.column("Existencias", anchor="center", width=140)
        self.tree.column("Precio", anchor="center", width=140)

        self.tree.grid(row=2, column=0, sticky="nsew")

        barra = tk.Frame(inner, bg=BG_CARDS)
        barra.grid(row=3, column=0, pady=10)

        tk.Button(barra, text="AGREGAR", bg=BUTTONS, fg="white",
                  font=("Segoe UI", 11, "bold"), command=self._agregar) \
            .pack(side="left", padx=6, ipadx=16, ipady=10)

        tk.Button(barra, text="MODIFICAR", bg=BUTTONS, fg="white",
                  font=("Segoe UI", 11, "bold"), command=self._modificar) \
            .pack(side="left", padx=6, ipadx=16, ipady=10)

        tk.Button(barra, text="AÑADIR EXISTENCIAS", bg=BUTTONS, fg="white",
                  font=("Segoe UI", 11, "bold"), command=self._sumar_existencias) \
            .pack(side="left", padx=6, ipadx=16, ipady=10)

        tk.Button(barra, text="RETIRAR EXISTENCIAS", bg=BUTTONS, fg="white",
                  font=("Segoe UI", 11, "bold"), command=self._restar_existencias) \
            .pack(side="left", padx=6, ipadx=16, ipady=10)

        tk.Button(barra, text="ELIMINAR", bg=WARNING, fg=TEXT,
                  font=("Segoe UI", 11, "bold"), command=self._eliminar) \
            .pack(side="left", padx=6, ipadx=16, ipady=10)

        db.crear_tabla_inventario()
        db.crear_tabla_categorias_inventario()
        db.asegurar_columna_categoria_id()

        self._cargar_categorias_filtro()

        ent_buscar.bind("<KeyRelease>", lambda e: self._cargar())
        ent_pmin.bind("<KeyRelease>", lambda e: self._cargar())
        ent_pmax.bind("<KeyRelease>", lambda e: self._cargar())
        self.var_ord_por.trace_add("write", lambda *args: self._cargar())
        self.var_orden.trace_add("write", lambda *args: self._cargar())
        self.var_cat_filtro.trace_add("write", lambda *args: self._cargar())
        self.var_stock_bajo.trace_add("write", lambda *args: self._cargar())

        self._cargar()

    def _cargar_categorias_filtro(self):
        try:
            cats = db.listar_categorias_inventario(self.sede_id)
            nombres = ["Todas"] + [n for (_id, n) in cats]
        except Exception:
            nombres = ["Todas"]

        self.cb_cat_filtro["values"] = nombres
        if not (self.var_cat_filtro.get() or "").strip():
            self.var_cat_filtro.set("Todas")
        elif self.var_cat_filtro.get() not in nombres:
            self.var_cat_filtro.set("Todas")

    def _limpiar_filtros(self):
        self.var_buscar.set("")
        self.var_ord_por.set("Nombre")
        self.var_orden.set("Ascendente")
        self.var_cat_filtro.set("Todas")
        self.var_stock_bajo.set(False)
        self.var_precio_min.set("")
        self.var_precio_max.set("")
        self._cargar()

    def _cargar(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        data = list(db.listar_inventario(self.sede_id))
        txt = (self.var_buscar.get() or "").strip().lower()
        cat = (self.var_cat_filtro.get() or "Todas").strip().lower()
        solo_bajo = bool(self.var_stock_bajo.get())

        pmin_txt = (self.var_precio_min.get() or "").strip()
        pmax_txt = (self.var_precio_max.get() or "").strip()
        pmin = None
        pmax = None
        try:
            if pmin_txt != "":
                pmin = float(pmin_txt)
        except Exception:
            pmin = None
        try:
            if pmax_txt != "":
                pmax = float(pmax_txt)
        except Exception:
            pmax = None

        filtrado = []
        for pid, nombre, stock, precio, categoria in data:
            nombre_s = (nombre or "")
            categoria_s = (categoria or "")

            if txt and txt not in nombre_s.lower():
                continue

            if cat != "todas" and categoria_s.strip().lower() != cat:
                continue

            try:
                stock_i = int(stock)
            except Exception:
                stock_i = 0

            if solo_bajo and stock_i >= 5:
                continue

            try:
                precio_f = float(precio)
            except Exception:
                precio_f = 0.0

            if pmin is not None and precio_f < pmin:
                continue
            if pmax is not None and precio_f > pmax:
                continue

            filtrado.append((pid, nombre_s, stock_i, precio_f, categoria_s))

        key = (self.var_ord_por.get() or "Nombre").strip().lower()
        reverse = ((self.var_orden.get() or "Ascendente").strip().lower() == "descendente")

        def sort_key(row):
            pid, nombre_s, stock_i, precio_f, categoria_s = row
            if key == "existencias":
                return stock_i
            if key == "precio":
                return precio_f
            if key in ("categoría", "categoria"):
                return categoria_s.lower()
            return nombre_s.lower()

        filtrado.sort(key=sort_key, reverse=reverse)

        for pid, nombre_s, stock_i, precio_f, categoria_s in filtrado:
            self.tree.insert("", "end", iid=str(pid),
                             values=(nombre_s, categoria_s, stock_i, f"{precio_f:.2f}"))

    def _agregar(self):
        dlg = ProductoDialog(self.winfo_toplevel(), self.sede_id, "Agregar producto")
        self.winfo_toplevel().wait_window(dlg)
        if dlg.result:
            db.insertar_producto(self.sede_id, *dlg.result)
            self._cargar_categorias_filtro()
            self._cargar()

    def _modificar(self):
        sel = self.tree.selection()
        if not sel:
            return
        pid = int(sel[0])
        nombre, categoria, stock, precio = self.tree.item(sel[0], "values")
        dlg = ProductoDialog(
            self.winfo_toplevel(),
            self.sede_id,
            "Modificar producto",
            initial={"nombre": nombre, "categoria": categoria, "stock": stock, "precio": precio}
        )
        self.winfo_toplevel().wait_window(dlg)
        if dlg.result:
            db.actualizar_producto(pid, *dlg.result)
            self._cargar_categorias_filtro()
            self._cargar()

    def _sumar_existencias(self):
        sel = self.tree.selection()
        if not sel:
            return
        pid = int(sel[0])
        nombre, categoria, stock, precio = self.tree.item(sel[0], "values")
        dlg = AjustarExistenciasDialog(self.winfo_toplevel(), "Añadir existencias", nombre, int(stock))
        self.winfo_toplevel().wait_window(dlg)
        if not dlg.result:
            return
        try:
            db.ajustar_stock(self.sede_id, pid, int(dlg.result))
            self._cargar()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _restar_existencias(self):
        sel = self.tree.selection()
        if not sel:
            return
        pid = int(sel[0])
        nombre, categoria, stock, precio = self.tree.item(sel[0], "values")
        stock_actual = 0
        try:
            stock_actual = int(stock)
        except Exception:
            stock_actual = 0
        dlg = AjustarExistenciasDialog(self.winfo_toplevel(), "Retirar existencias", nombre, stock_actual, maximo=stock_actual)
        self.winfo_toplevel().wait_window(dlg)
        if not dlg.result:
            return
        try:
            db.ajustar_stock(self.sede_id, pid, -int(dlg.result))
            self._cargar()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _eliminar(self):
        sel = self.tree.selection()
        if not sel:
            return
        if messagebox.askyesno("Eliminar", "¿Eliminar producto?"):
            db.eliminar_producto(int(sel[0]))
            self._cargar()


class InventarioWindow(tk.Toplevel):
    def __init__(self, master, sede_id, user_role="dependiente", on_back=None):
        super().__init__(master)
        self.sede_id = int(sede_id)
        self.user_role = user_role
        self.on_back = on_back

        self.title("Sistema — Lorets Xela")
        self.configure(bg=BG_PRIMARY)

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w = int(sw * 0.92)
        h = int(sh * 0.92)
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(1100, 650)
        self.resizable(True, True)

        _apply_ttk_styles(self)

        self.protocol("WM_DELETE_WINDOW", self._salir)

        self.sidebar = SideBar(
            self,
            user_role=user_role,
            on_exit=self._salir,
            on_open_inventario=self._show_inventario,
            on_open_ventas=self._show_ventas,
            on_open_calendario=self._show_citas,
            on_open_usuarios=self._show_usuarios if user_role == "administrador" else None
        )
        self.sidebar.pack(side="left", fill="y")

        self.container = tk.Frame(self, bg=BG_PRIMARY)
        self.container.pack(side="left", expand=True, fill="both")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.view_inventario = InventarioView(self.container, self.sede_id, user_role)
        self.view_ventas = VentasFrame(self.container, self.sede_id, user_role)
        self.view_citas = CitasFrame(self.container, self.sede_id, user_role)
        self.view_usuarios = UsuariosFrame(self.container, user_role, self.sede_id) if user_role == "administrador" else None

        self.view_inventario.grid(row=0, column=0, sticky="nsew")
        self.view_ventas.grid(row=0, column=0, sticky="nsew")
        self.view_citas.grid(row=0, column=0, sticky="nsew")
        if self.view_usuarios:
            self.view_usuarios.grid(row=0, column=0, sticky="nsew")

        self._show_inventario()

    def _salir(self):
        try:
            self.destroy()
        finally:
            if callable(self.on_back):
                self.on_back()

    def _show_inventario(self):
        try:
            self.view_inventario.tkraise()
            if hasattr(self.view_inventario, "_cargar"):
                self.view_inventario._cargar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Inventario.\n\n{e}")

    def _show_ventas(self):
        try:
            self.view_ventas.tkraise()
            if hasattr(self.view_ventas, "_cargar"):
                self.view_ventas._cargar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Ventas.\n\n{e}")

    def _show_citas(self):
        try:
            self.view_citas.tkraise()
            if hasattr(self.view_citas, "_cargar"):
                self.view_citas._cargar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Citas.\n\n{e}")

    def _show_usuarios(self):
        try:
            if self.view_usuarios:
                self.view_usuarios.tkraise()
                if hasattr(self.view_usuarios, "_cargar_usuarios"):
                    self.view_usuarios._cargar_usuarios()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Usuarios.\n\n{e}")
