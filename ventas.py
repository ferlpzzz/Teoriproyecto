import tkinter as tk
from tkinter import ttk
import db
from factura_html import abrir_factura_en_navegador

BG_PRIMARY = "#fff5f7"
BG_SECONDARY = "#f3d6dc"
BG_CARDS = "#ffffff"
ACCENT = "#da5d86"
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


def _card(parent, padx=12, pady=10):
    c = tk.Frame(parent, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
    inner = tk.Frame(c, bg=BG_CARDS)
    inner.pack(fill="both", expand=True, padx=padx, pady=pady)
    return c, inner


class ConfirmDialog(tk.Toplevel):
    def __init__(self, parent, title_text, body_text, ok_text="Vender", cancel_text="Cancelar"):
        super().__init__(parent)
        self.result = False
        self.configure(bg=BG_PRIMARY)
        self.title(title_text)
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        w, h = 430, 250
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        wrap = tk.Frame(self, bg=BG_PRIMARY)
        wrap.pack(fill="both", expand=True, padx=14, pady=14)

        box = tk.Frame(wrap, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        box.pack(fill="both", expand=True)

        tk.Frame(box, bg=BUTTONS, height=4).pack(fill="x")

        cont = tk.Frame(box, bg=BG_CARDS)
        cont.pack(fill="both", expand=True, padx=14, pady=12)

        tk.Label(cont, text=title_text, bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(cont, text=body_text, bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold"), justify="left").pack(anchor="w", pady=(8, 0))

        btns = tk.Frame(wrap, bg=BG_PRIMARY)
        btns.pack(fill="x", pady=(10, 0))
        btns.grid_columnconfigure(0, weight=1)
        btns.grid_columnconfigure(1, weight=1)

        tk.Button(
            btns, text=cancel_text,
            bg=BG_SECONDARY, fg=TEXT, bd=0, cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            activebackground=BG_SECONDARY,
            command=self._cancel
        ).grid(row=0, column=0, sticky="ew", ipady=10, padx=(0, 8))

        tk.Button(
            btns, text=ok_text,
            bg=BUTTONS, fg=TEXT_BTN, bd=0, cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            activebackground=BUTTONS_HOVER,
            command=self._ok
        ).grid(row=0, column=1, sticky="ew", ipady=10, padx=(8, 0))

        self.bind("<Escape>", lambda e: self._cancel())
        self.bind("<Return>", lambda e: self._ok())
        self.wait_window(self)

    def _ok(self):
        self.result = True
        self.destroy()

    def _cancel(self):
        self.result = False
        self.destroy()


class InfoToast(tk.Toplevel):
    def __init__(self, parent, text, accent=BUTTONS):
        super().__init__(parent)
        self.configure(bg=BG_PRIMARY)
        self.overrideredirect(True)

        box = tk.Frame(self, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        box.pack(fill="both", expand=True)

        tk.Frame(box, bg=accent, height=4).pack(fill="x")
        tk.Label(box, text=text, bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 10, "bold"), justify="left").pack(padx=12, pady=10)

        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()

        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()

        x = px + pw - w - 18
        y = py + ph - h - 18
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.after(1500, self.destroy)


class QtyDialog(tk.Toplevel):
    def __init__(self, parent, producto, maximo, precio_unit, cantidad_inicial=1):
        super().__init__(parent)
        self.result = None
        self.configure(bg=BG_PRIMARY)
        self.title("Cantidad")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        w, h = 420, 306
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        wrap = tk.Frame(self, bg=BG_PRIMARY)
        wrap.pack(fill="both", expand=True, padx=14, pady=14)

        top = tk.Frame(wrap, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        top.pack(fill="x", pady=(0, 10))
        tk.Frame(top, bg=BUTTONS, height=4).pack(fill="x")

        head = tk.Frame(top, bg=BG_CARDS)
        head.pack(fill="x", padx=12, pady=10)
        tk.Label(head, text=producto, bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(head, text=f"Disponible: {int(maximo)}", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6, 0))

        mid = tk.Frame(wrap, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        mid.pack(fill="x", pady=(0, 10))

        row = tk.Frame(mid, bg=BG_CARDS)
        row.pack(fill="x", padx=12, pady=10)
        row.grid_columnconfigure(1, weight=1)

        self.var_qty = tk.IntVar(value=max(1, min(int(cantidad_inicial), int(maximo))))

        btn_minus = tk.Button(row, text="–", bg=BG_SECONDARY, fg=TEXT, bd=0, cursor="hand2", font=("Segoe UI", 16, "bold"), activebackground=BG_SECONDARY)
        btn_minus.grid(row=0, column=0, ipadx=14, ipady=8, padx=(0, 8))

        ent = tk.Entry(row, textvariable=self.var_qty, justify="center", relief="flat", bg=BG_PRIMARY, fg=TEXT, font=("Segoe UI", 16, "bold"))
        ent.grid(row=0, column=1, sticky="ew", ipady=8)

        btn_plus = tk.Button(row, text="+", bg=BG_SECONDARY, fg=TEXT, bd=0, cursor="hand2", font=("Segoe UI", 16, "bold"), activebackground=BG_SECONDARY)
        btn_plus.grid(row=0, column=2, ipadx=14, ipady=8, padx=(8, 0))

        self.lbl_total = tk.Label(mid, text="", bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 12, "bold"))
        self.lbl_total.pack(anchor="w", padx=12, pady=(0, 10))

        actions = tk.Frame(wrap, bg=BG_PRIMARY)
        actions.pack(fill="x")
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        tk.Button(actions, text="Cancelar", bg=BG_SECONDARY, fg=TEXT, bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"), activebackground=BG_SECONDARY, command=self._cancel).grid(row=0, column=0, sticky="ew", ipady=10, padx=(0, 8))
        tk.Button(actions, text="Aceptar", bg=BUTTONS, fg=TEXT_BTN, bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"), activebackground=BUTTONS_HOVER, command=self._ok).grid(row=0, column=1, sticky="ew", ipady=10, padx=(8, 0))

        def clamp():
            try:
                v = int(str(self.var_qty.get()).strip())
            except Exception:
                v = 1
            v = max(1, min(v, int(maximo)))
            self.var_qty.set(v)
            self.lbl_total.config(text=f"Subtotal: Q {float(precio_unit) * v:.2f}")

        def minus():
            self.var_qty.set(max(1, self.var_qty.get() - 1))
            clamp()

        def plus():
            self.var_qty.set(min(int(maximo), self.var_qty.get() + 1))
            clamp()

        btn_minus.config(command=minus)
        btn_plus.config(command=plus)
        ent.bind("<KeyRelease>", lambda e: clamp())
        self.bind("<Escape>", lambda e: self._cancel())
        self.bind("<Return>", lambda e: self._ok())

        clamp()
        ent.focus_set()
        ent.selection_range(0, "end")
        self.wait_window(self)

    def _ok(self):
        try:
            self.result = int(self.var_qty.get())
        except Exception:
            self.result = None
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()



class FacturacionDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        self.configure(bg=BG_PRIMARY)
        self.title("Facturación")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        w, h = 520, 360
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

        wrap = tk.Frame(self, bg=BG_PRIMARY)
        wrap.pack(fill="both", expand=True, padx=14, pady=14)

        box = tk.Frame(wrap, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        box.pack(fill="both", expand=True)

        tk.Frame(box, bg=BUTTONS, height=4).pack(fill="x")

        cont = tk.Frame(box, bg=BG_CARDS)
        cont.pack(fill="both", expand=True, padx=14, pady=12)

        tk.Label(cont, text="Datos para factura", bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(cont, text="Obligatorio para completar la venta.", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6, 12))

        form = tk.Frame(cont, bg=BG_CARDS)
        form.pack(fill="x")
        form.grid_columnconfigure(1, weight=1)

        self.var_nit = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_apellidos = tk.StringVar()


        def add_row(r, label, var):
            tk.Label(form, text=label, bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 10, "bold")).grid(row=r, column=0, sticky="w", pady=6)
            e = tk.Entry(form, textvariable=var, relief="flat", bg=BG_PRIMARY, fg=TEXT, font=("Segoe UI", 11, "bold"))
            e.grid(row=r, column=1, sticky="ew", ipady=8, pady=6)
            return e

        e1 = add_row(0, "NIT:", self.var_nit)
        add_row(1, "Nombre:", self.var_nombre)
        add_row(2, "Apellidos:", self.var_apellidos)

        actions = tk.Frame(wrap, bg=BG_PRIMARY)
        actions.pack(fill="x", pady=(10, 0))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        tk.Button(actions, text="Cancelar", bg=BG_SECONDARY, fg=TEXT, bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"), activebackground=BG_SECONDARY, command=self._cancel).grid(row=0, column=0, sticky="ew", ipady=10, padx=(0, 8))
        tk.Button(actions, text="Siguiente", bg=BUTTONS, fg=TEXT_BTN, bd=0, cursor="hand2", font=("Segoe UI", 11, "bold"), activebackground=BUTTONS_HOVER, command=self._ok).grid(row=0, column=1, sticky="ew", ipady=10, padx=(8, 0))

        self.bind("<Escape>", lambda e: self._cancel())
        self.bind("<Return>", lambda e: self._ok())
        e1.focus_set()
        self.wait_window(self)

    def _ok(self):
        nit = self.var_nit.get().strip()
        if not nit.isdigit() or len(nit) != 9:
            InfoToast(self.winfo_toplevel(), "El NIT debe tener exactamente 9 dígitos numéricos.", accent=ACCENT)
            return

        nombre = self.var_nombre.get().strip()
        apellidos = self.var_apellidos.get().strip()
        if not nit or not nombre or not apellidos:
            InfoToast(self.winfo_toplevel(), "Completa NIT, Nombre y Apellidos.", accent=ACCENT)
            return
        self.result = {"nit": nit, "nombre": nombre, "apellidos": apellidos}
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()

class VentasFrame(tk.Frame):
    def __init__(self, master, sede_id: int, user_role="dependiente"):
        super().__init__(master, bg=BG_PRIMARY)
        self.sede_id = int(sede_id)
        self.user_role = user_role
        _apply_ttk_styles(self)

        self.cart = {}
        self.productos_cache = []

        wrapper = tk.Frame(self, bg=BG_PRIMARY)
        wrapper.pack(fill="both", expand=True, padx=14, pady=14)

        header_card, header = _card(wrapper, padx=14, pady=10)
        header_card.pack(fill="x", pady=(0, 10))

        sede = db.obtener_sede(self.sede_id)
        titulo = f"Ventas — {sede[1]}" if sede else "Ventas"
        tk.Label(header, text=titulo, bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(header, text="Agrega productos al carrito y finaliza la venta.", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(4, 0))

        body = tk.Frame(wrapper, bg=BG_PRIMARY)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        prod_card, prod = _card(body, padx=12, pady=10)
        prod_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        cart_card, cart = _card(body, padx=12, pady=10)
        cart_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(prod, text="Productos", bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w")

        self.var_buscar = tk.StringVar(value="")
        search_box = tk.Frame(prod, bg=BG_PRIMARY, highlightthickness=1, highlightbackground=BG_SECONDARY)
        search_box.pack(fill="x", pady=(8, 8))
        self.ent_buscar = tk.Entry(search_box, textvariable=self.var_buscar, relief="flat", bg=BG_PRIMARY, fg=TEXT, font=("Segoe UI", 11))
        self.ent_buscar.pack(fill="x", padx=10, pady=8)
        self.ent_buscar.bind("<KeyRelease>", lambda e: self._buscar_suave())
        self.ent_buscar.bind("<Return>", lambda e: self._focus_first())

        actions = tk.Frame(prod, bg=BG_CARDS)
        actions.pack(fill="x", pady=(0, 8))
        tk.Button(actions, text="AGREGAR", bg=BUTTONS, fg=TEXT_BTN, bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), activebackground=BUTTONS_HOVER, command=self._agregar_carrito).pack(side="left", padx=(0, 8), ipady=8, ipadx=14)
        tk.Button(actions, text="RECARGAR", bg=BG_SECONDARY, fg=TEXT, bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), activebackground=BG_SECONDARY, command=self._cargar).pack(side="left", ipady=8, ipadx=14)

        self.tree_prod = ttk.Treeview(prod, columns=("Producto", "Categoría", "Stock", "Precio"), show="headings", style="Soft.Treeview")
        self.tree_prod.heading("Producto", text="Producto")
        self.tree_prod.heading("Categoría", text="Categoría")
        self.tree_prod.heading("Stock", text="Stock")
        self.tree_prod.heading("Precio", text="Precio (Q)")
        self.tree_prod.column("Producto", width=360, anchor="w")
        self.tree_prod.column("Categoría", width=170, anchor="center")
        self.tree_prod.column("Stock", width=90, anchor="center")
        self.tree_prod.column("Precio", width=110, anchor="center")
        self.tree_prod.pack(fill="both", expand=True)
        self.tree_prod.bind("<Double-1>", lambda e: self._agregar_carrito())

        cart.grid_rowconfigure(1, weight=1)
        cart.grid_columnconfigure(0, weight=1)

        header_cart = tk.Frame(cart, bg=BG_CARDS)
        header_cart.grid(row=0, column=0, sticky="ew")
        header_cart.grid_columnconfigure(0, weight=1)
        tk.Label(header_cart, text="Carrito", bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")
        self.lbl_total_top = tk.Label(header_cart, text="Q 0.00", bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 14, "bold"))
        self.lbl_total_top.grid(row=0, column=1, sticky="e")

        self.tree_cart = ttk.Treeview(cart, columns=("Producto", "Cant", "Precio", "Subtotal"), show="headings", style="Soft.Treeview", height=10)
        self.tree_cart.heading("Producto", text="Producto")
        self.tree_cart.heading("Cant", text="Cant")
        self.tree_cart.heading("Precio", text="Precio")
        self.tree_cart.heading("Subtotal", text="Subtotal")
        self.tree_cart.column("Producto", width=210, anchor="w")
        self.tree_cart.column("Cant", width=60, anchor="center")
        self.tree_cart.column("Precio", width=85, anchor="center")
        self.tree_cart.column("Subtotal", width=95, anchor="center")
        self.tree_cart.grid(row=1, column=0, sticky="nsew", pady=(8, 8))
        self.tree_cart.bind("<Double-1>", lambda e: self._editar_cantidad())

        cart_actions = tk.Frame(cart, bg=BG_CARDS)
        cart_actions.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        cart_actions.grid_columnconfigure(0, weight=1, uniform="a")
        cart_actions.grid_columnconfigure(1, weight=1, uniform="a")
        cart_actions.grid_columnconfigure(2, weight=1, uniform="a")

        tk.Button(cart_actions, text="EDITAR", bg=BG_SECONDARY, fg=TEXT, bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), activebackground=BG_SECONDARY, command=self._editar_cantidad).grid(row=0, column=0, sticky="ew", ipady=8, padx=(0, 8))
        tk.Button(cart_actions, text="QUITAR", bg=BG_SECONDARY, fg=TEXT, bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), activebackground=BG_SECONDARY, command=self._quitar_item).grid(row=0, column=1, sticky="ew", ipady=8, padx=(0, 8))
        tk.Button(cart_actions, text="VACIAR", bg=BG_SECONDARY, fg=TEXT, bd=0, cursor="hand2", font=("Segoe UI", 10, "bold"), activebackground=BG_SECONDARY, command=self._vaciar).grid(row=0, column=2, sticky="ew", ipady=8)

        totals = tk.Frame(cart, bg=BG_PRIMARY, highlightthickness=1, highlightbackground=BG_SECONDARY)
        totals.grid(row=3, column=0, sticky="ew", pady=(4, 8))
        self.lbl_items = tk.Label(totals, text="Items: 0", bg=BG_PRIMARY, fg=TEXT, font=("Segoe UI", 10, "bold"))
        self.lbl_items.pack(anchor="w", padx=10, pady=(8, 0))
        self.lbl_total = tk.Label(totals, text="Total: Q 0.00", bg=BG_PRIMARY, fg=TEXT, font=("Segoe UI", 14, "bold"))
        self.lbl_total.pack(anchor="w", padx=10, pady=(4, 8))

        tk.Button(cart, text="VENDER", bg=BUTTONS, fg=TEXT_BTN, bd=0, cursor="hand2", font=("Segoe UI", 12, "bold"), activebackground=BUTTONS_HOVER, command=self._checkout).grid(row=4, column=0, sticky="ew", ipady=12)

        self._cargar()
        self._refresh_cart_view()

    def _set_products_rows(self, productos):
        for i in self.tree_prod.get_children():
            self.tree_prod.delete(i)
        for pid, nombre, stock, precio, categoria in productos:
            self.tree_prod.insert("", "end", iid=str(pid), values=(nombre, categoria or "", int(stock), f"{float(precio):.2f}"))

    def _cargar(self):
        self.productos_cache = db.listar_inventario(self.sede_id)
        self._set_products_rows(self.productos_cache)
        self._buscar_suave()

    def _buscar_suave(self):
        texto = (self.var_buscar.get() or "").strip().lower()
        productos = self.productos_cache or db.listar_inventario(self.sede_id)
        if not texto:
            self._set_products_rows(productos)
            return
        filtrados = [p for p in productos if texto in (p[1] or "").strip().lower()]
        self._set_products_rows(filtrados)

    def _focus_first(self):
        kids = self.tree_prod.get_children()
        if kids:
            self.tree_prod.selection_set(kids[0])
            self.tree_prod.focus(kids[0])
            self.tree_prod.see(kids[0])

    def _refresh_cart_view(self):
        for i in self.tree_cart.get_children():
            self.tree_cart.delete(i)

        total_items = 0
        total = 0.0

        for pid, item in self.cart.items():
            cant = int(item["cant"])
            precio = float(item["precio"])
            subtotal = cant * precio
            total_items += cant
            total += subtotal
            self.tree_cart.insert("", "end", iid=str(pid), values=(item["nombre"], cant, f"{precio:.2f}", f"{subtotal:.2f}"))

        self.lbl_items.config(text=f"Items: {total_items}")
        self.lbl_total.config(text=f"Total: Q {total:.2f}")
        self.lbl_total_top.config(text=f"Q {total:.2f}")

    def _get_stock_real(self, pid):
        for p in self.productos_cache or db.listar_inventario(self.sede_id):
            if int(p[0]) == int(pid):
                return int(p[2])
        return 0

    def _agregar_carrito(self):
        sel = self.tree_prod.selection()
        if not sel:
            InfoToast(self.winfo_toplevel(), "Selecciona un producto para agregar.", accent=ACCENT)
            return

        pid = int(sel[0])
        nombre, categoria, stock_str, precio_str = self.tree_prod.item(sel[0], "values")
        stock = int(stock_str)
        precio = float(precio_str)

        if stock <= 0:
            InfoToast(self.winfo_toplevel(), "Este producto está sin existencias.", accent=DANGER)
            return

        actual = int(self.cart.get(pid, {}).get("cant", 0))
        max_disp = max(stock - actual, 0)
        if max_disp <= 0:
            InfoToast(self.winfo_toplevel(), "Ya tienes el máximo en el carrito.", accent=ACCENT)
            return

        dlg = QtyDialog(self.winfo_toplevel(), nombre, max_disp, precio, 1)
        cant = dlg.result
        if not cant:
            return

        if pid not in self.cart:
            self.cart[pid] = {"nombre": nombre, "precio": precio, "cant": 0}

        self.cart[pid]["cant"] += int(cant)
        self._refresh_cart_view()

    def _editar_cantidad(self):
        sel = self.tree_cart.selection()
        if not sel:
            InfoToast(self.winfo_toplevel(), "Selecciona un producto del carrito.", accent=ACCENT)
            return

        pid = int(sel[0])
        item = self.cart.get(pid)
        if not item:
            return

        stock_real = self._get_stock_real(pid)
        if stock_real <= 0:
            InfoToast(self.winfo_toplevel(), "Recarga productos e intenta de nuevo.", accent=DANGER)
            return

        dlg = QtyDialog(self.winfo_toplevel(), item["nombre"], stock_real, float(item["precio"]), int(item["cant"]))
        cant = dlg.result
        if not cant:
            return

        item["cant"] = int(cant)
        self._refresh_cart_view()

    def _quitar_item(self):
        sel = self.tree_cart.selection()
        if not sel:
            InfoToast(self.winfo_toplevel(), "Selecciona un producto del carrito.", accent=ACCENT)
            return
        pid = int(sel[0])
        if pid in self.cart:
            del self.cart[pid]
            self._refresh_cart_view()

    def _vaciar(self):
        if not self.cart:
            InfoToast(self.winfo_toplevel(), "El carrito ya está vacío.", accent=ACCENT)
            return
        dlg = ConfirmDialog(self.winfo_toplevel(), "Vaciar carrito", "¿Eliminar todos los productos del carrito?", ok_text="Vaciar", cancel_text="Cancelar")
        if not dlg.result:
            return
        self.cart.clear()
        self._refresh_cart_view()
        InfoToast(self.winfo_toplevel(), "Carrito vaciado.", accent=BUTTONS)

    def _checkout(self):
        if not self.cart:
            InfoToast(self.winfo_toplevel(), "Agrega productos antes de vender.", accent=ACCENT)
            return

        inv = db.listar_inventario(self.sede_id)
        stock_map = {int(p[0]): int(p[2]) for p in inv}

        for pid, it in self.cart.items():
            if int(it["cant"]) > stock_map.get(int(pid), 0):
                InfoToast(self.winfo_toplevel(), f"Stock insuficiente: {it['nombre']}", accent=DANGER)
                return

        total = 0.0
        total_items = 0
        for pid, it in self.cart.items():
            total += float(it["precio"]) * int(it["cant"])
            total_items += int(it["cant"])

        dlg = ConfirmDialog(self.winfo_toplevel(), "Confirmar venta", f"Items: {total_items}\nTotal: Q {total:.2f}\n\n¿Deseas continuar?", ok_text="Vender", cancel_text="Cancelar")
        if not dlg.result:
            return

        fact = FacturacionDialog(self.winfo_toplevel())
        if not fact.result:
            InfoToast(self.winfo_toplevel(), "Facturación cancelada. Venta no realizada.", accent=ACCENT)
            return
        datos_fact = fact.result

        items_fact = []
        for pid, it in self.cart.items():
            items_fact.append({"cantidad": int(it["cant"]), "descripcion": it["nombre"], "precio_unitario": float(it["precio"]), "impuestos": 0.0})

        try:
            for pid, it in self.cart.items():
                db.registrar_venta(self.sede_id, int(pid), int(it["cant"]), float(it["precio"]))
            self.cart.clear()
            self._refresh_cart_view()
            self._cargar()
            try:
                abrir_factura_en_navegador(datos_fact["nit"], datos_fact["nombre"], datos_fact["apellidos"], items_fact)
            except Exception:
                pass
            InfoToast(self.winfo_toplevel(), f"Venta realizada. Total: Q {total:.2f}", accent=BUTTONS)
        except Exception:
            InfoToast(self.winfo_toplevel(), "No se pudo registrar la venta.", accent=DANGER)
