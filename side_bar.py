import tkinter as tk
import os

BG_PRIMARY = "#fff5f7"
BG_SECONDARY = "#f3d6dc"
BG_CARDS = "#ffffff"
ACCENT = "#da5d86"
TEXT = "#0b1011"
TEXT_MUTED = "#4b5563"
TEXT_BTN = "white"
BUTTONS = "#01a6b2"
BUTTONS_HOVER = "#028a94"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")


def _load_logo_scaled(path: str, max_w: int, max_h: int):
    try:
        if os.path.exists(path):
            img = tk.PhotoImage(file=path)
            w, h = img.width(), img.height()
            factor = max((w + max_w - 1) // max_w, (h + max_h - 1) // max_h, 1)
            if factor > 1:
                img = img.subsample(factor, factor)
            return img
    except Exception:
        pass
    return None


class SideBar(tk.Frame):
    def __init__(
        self,
        master,
        user_role="dependiente",
        on_exit=None,
        on_open_inventario=None,
        on_open_ventas=None,
        on_open_calendario=None,
        on_open_usuarios=None,
        **kwargs
    ):
        super().__init__(master, bg=BG_PRIMARY, width=260)
        self.user_role = user_role
        self.on_exit = on_exit
        self.on_open_inventario = on_open_inventario
        self.on_open_ventas = on_open_ventas
        self.on_open_calendario = on_open_calendario
        self.on_open_usuarios = on_open_usuarios
        self.pack_propagate(False)

        container = tk.Frame(self, bg=BG_PRIMARY)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        top_card = tk.Frame(container, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        top_card.pack(fill="x", pady=(0, 12))

        top = tk.Frame(top_card, bg=BG_CARDS)
        top.pack(fill="x", padx=12, pady=14)

        C_SIZE = 110
        C_RAD = 48
        self._canvas_logo = tk.Canvas(top, width=C_SIZE, height=C_SIZE, bg=BG_CARDS, highlightthickness=0)
        self._canvas_logo.pack()

        cx, cy = C_SIZE // 2, C_SIZE // 2
        self._canvas_logo.create_oval(cx - C_RAD, cy - C_RAD, cx + C_RAD, cy + C_RAD, fill=BG_PRIMARY, outline="")

        self.logo_img = _load_logo_scaled(LOGO_PATH, max_w=int(C_RAD * 1.6), max_h=int(C_RAD * 1.6))
        if self.logo_img:
            self._canvas_logo.create_image(cx, cy, image=self.logo_img)
        else:
            self._canvas_logo.create_text(cx, cy, text="LOGO", fill=TEXT, font=("Segoe UI", 12, "bold"))

        tk.Label(top, text="MENÚ", bg=BG_CARDS, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).pack(pady=(10, 0))

        buttons_card = tk.Frame(container, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        buttons_card.pack(fill="both", expand=True)

        btns = tk.Frame(buttons_card, bg=BG_CARDS)
        btns.pack(fill="both", expand=True, padx=12, pady=12)

        def _mk_btn(texto, cmd, danger=False):
            bg = ACCENT if danger else BUTTONS
            abg = "#c84f76" if danger else BUTTONS_HOVER
            b = tk.Button(
                btns,
                text=texto,
                bg=bg,
                fg=TEXT_BTN,
                activebackground=abg,
                activeforeground=TEXT_BTN,
                bd=0,
                cursor="hand2",
                font=("Segoe UI", 12, "bold"),
                command=cmd
            )
            b.pack(fill="x", pady=8, ipady=10)

            def _on_enter(_):
                b.configure(bg=abg)

            def _on_leave(_):
                b.configure(bg=bg)

            b.bind("<Enter>", _on_enter)
            b.bind("<Leave>", _on_leave)
            return b

        _mk_btn("INVENTARIO", self._abrir_inventario)
        _mk_btn("VENTAS", self._abrir_ventas)
        _mk_btn("CITAS", self._abrir_calendario)

        if self.user_role == "administrador":
            _mk_btn("USUARIOS", self._abrir_usuarios)

        tk.Frame(btns, bg=BG_CARDS).pack(expand=True, fill="both")

        _mk_btn("SALIR", self._cerrar, danger=True)

    def _abrir_inventario(self):
        if callable(self.on_open_inventario):
            self.on_open_inventario()

    def _abrir_ventas(self):
        if callable(self.on_open_ventas):
            self.on_open_ventas()

    def _abrir_calendario(self):
        if callable(self.on_open_calendario):
            self.on_open_calendario()

    def _abrir_usuarios(self):
        if callable(self.on_open_usuarios):
            self.on_open_usuarios()

    def _cerrar(self):
        if callable(self.on_exit):
            self.on_exit()
