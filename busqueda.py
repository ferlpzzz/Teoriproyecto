import tkinter as tk
from tkinter import ttk, messagebox
import db

BG_PRIMARY = "#fff5f7"
BG_SECONDARY = "#f3d6dc"
BG_CARDS = "#ffffff"
TEXT = "#0b1011"
BUTTONS = "#01a6b2"
BUTTONS_SECONDARY = "#028a94"


def _apply_ttk_styles(root: tk.Misc):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except:
        pass

    style.configure(".", foreground=TEXT)

    style.configure("Soft.Treeview",
                    background=BG_CARDS,
                    fieldbackground=BG_CARDS,
                    foreground=TEXT,
                    rowheight=32,
                    borderwidth=0)
    style.map("Soft.Treeview",
              background=[("selected", BG_SECONDARY)],
              foreground=[("selected", TEXT)])

    style.configure("Soft.Treeview.Heading",
                    font=("Segoe UI", 11, "bold"),
                    foreground=TEXT,
                    relief="flat")


class BusquedaFrame(tk.Frame):
    def __init__(self, master, sede_id: int, user_role="dependiente"):
        super().__init__(master, bg=BG_PRIMARY)
        self.sede_id = int(sede_id)
        self.user_role = user_role

        _apply_ttk_styles(self)

        panel = tk.Frame(self, bg=BG_PRIMARY)
        panel.pack(side="left", expand=True, fill="both", padx=20, pady=20)

        card = tk.Frame(panel, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        card.pack(expand=True, fill="both")

        inner = tk.Frame(card, bg=BG_CARDS)
        inner.pack(expand=True, fill="both", padx=18, pady=16)

        inner.grid_rowconfigure(2, weight=1)
        inner.grid_columnconfigure(0, weight=1)

        sede = db.obtener_sede(self.sede_id)
        titulo = f"Búsqueda — {sede[1]}" if sede else "Búsqueda"
        tk.Label(
            inner, text=titulo,
            bg=BG_CARDS, fg=TEXT,
            font=("Segoe UI", 20, "bold")
        ).grid(row=0, column=0, sticky="ew", pady=(4, 10))

        barra = tk.Frame(inner, bg=BG_CARDS)
        barra.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        barra.grid_columnconfigure(3, weight=1)

        tk.Label(
            barra, text="Buscar producto:",
            bg=BG_CARDS, fg=TEXT,
            font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=0, sticky="w", padx=(6, 8))

        self.var_texto = tk.StringVar()
        self.ent = tk.Entry(barra, textvariable=self.var_texto, width=40)
        self.ent.grid(row=0, column=1, sticky="w", padx=(0, 10))
        self.ent.bind("<Return>", lambda e: self._buscar())

        tk.Button(
            barra, text="BUSCAR",
            bg=BUTTONS, fg="white",
            activebackground=BUTTONS_SECONDARY, activeforeground="white",
            bd=0, cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            command=self._buscar
        ).grid(row=0, column=2, sticky="w", padx=(0, 10), ipadx=12, ipady=8)

        tk.Button(
            barra, text="LIMPIAR",
            bg=BUTTONS, fg="white",
            activebackground=BUTTONS_SECONDARY, activeforeground="white",
            bd=0, cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            command=self._limpiar
        ).grid(row=0, column=4, sticky="e", padx=6, ipadx=12, ipady=8)

        self.tree = ttk.Treeview(
            inner,
            columns=("Producto", "Categoría", "Existencias", "Precio"),
            show="headings",
            style="Soft.Treeview"
        )
        self.tree.heading("Producto", text="Producto")
        self.tree.heading("Categoría", text="Categoría")
        self.tree.heading("Existencias", text="Existencias")
        self.tree.heading("Precio", text="Precio (Q)")

        self.tree.column("Producto", width=360, anchor="center")
        self.tree.column("Categoría", width=220, anchor="center")
        self.tree.column("Existencias", width=120, anchor="center")
        self.tree.column("Precio", width=120, anchor="center")

        self.tree.grid(row=2, column=0, sticky="nsew", pady=6)

        self._cargar_todo()

    def _set_rows(self, productos):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for pid, nombre, stock, precio, categoria in productos:
            self.tree.insert(
                "", "end", iid=str(pid),
                values=(nombre, categoria or "", int(stock), f"{float(precio):.2f}")
            )

    def _cargar_todo(self):
        try:
            productos = db.listar_inventario(self.sede_id)
        except Exception as e:
            messagebox.showerror("Búsqueda", f"No se pudo cargar inventario:\n{e}")
            return
        self._set_rows(productos)

    def _buscar(self):
        texto = (self.var_texto.get() or "").strip().lower()
        if not texto:
            messagebox.showinfo("Búsqueda", "Escribe algo para buscar (ej: esmalte).")
            return

        try:
            productos = db.listar_inventario(self.sede_id)
        except Exception as e:
            messagebox.showerror("Búsqueda", f"No se pudo cargar inventario:\n{e}")
            return

        filtrados = [p for p in productos if texto in (p[1] or "").strip().lower()]
        self._set_rows(filtrados)

        kids = self.tree.get_children()
        if kids:
            self.tree.selection_set(kids[0])
            self.tree.focus(kids[0])
            self.tree.see(kids[0])

    def _limpiar(self):
        self.var_texto.set("")
        self._cargar_todo()