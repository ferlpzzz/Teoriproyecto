import os
import hashlib
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import db
from sedes_selector import SeleccionSede
db.init_db()


BG_PRIMARY = "#fff5f7"
BG_SECONDARY = "#f3d6dc"
BG_CARDS = "#ffffff"
ACCENT = "#da5d86"
TEXT = "#0b1011"
TEXT_MUTED = "#4b5563"
BUTTONS = "#01a6b2"
BUTTONS_SECONDARY = "#028a94"

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
    except Exception as e:
        print(e)
    return None


def _load_icon(path: str, target_px: int = 22):
    try:
        if os.path.exists(path):
            img = tk.PhotoImage(file=path)
            w, h = img.width(), img.height()
            factor = max(w // target_px, h // target_px, 1)
            if factor > 1:
                img = img.subsample(factor, factor)
            return img
    except Exception:
        pass
    return None


def hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode()).hexdigest()


def aplicar_estilos_ttk(root: tk.Tk):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except:
        pass

    root.configure(bg=BG_PRIMARY)
    style.configure(".", foreground=TEXT)

    style.configure("Main.TFrame", background=BG_PRIMARY)
    style.configure("Card.TFrame", background=BG_CARDS)

    style.configure("Title.TLabel", background=BG_CARDS, foreground=TEXT, font=("Segoe UI", 22, "bold"))
    style.configure("Label.TLabel", background=BG_CARDS, foreground=TEXT, font=("Segoe UI", 11, "bold"))
    style.configure("Hint.TLabel", background=BG_CARDS, foreground=TEXT_MUTED, font=("Segoe UI", 10))

    style.configure("Big.TEntry", fieldbackground="white", bordercolor=BG_SECONDARY, borderwidth=1, relief="flat")
    style.map("Big.TEntry",
              lightcolor=[("focus", ACCENT)],
              bordercolor=[("focus", ACCENT)])

    style.configure("Primary.TButton",
                    background=BUTTONS,
                    foreground="white",
                    font=("Segoe UI", 11, "bold"),
                    padding=10,
                    borderwidth=0)
    style.map("Primary.TButton",
              background=[("active", BUTTONS_SECONDARY)])

    style.configure("Icon.TButton",
                    background=BG_SECONDARY,
                    foreground=TEXT,
                    padding=8,
                    borderwidth=0)
    style.map("Icon.TButton",
              background=[("active", BG_SECONDARY)])


def set_responsive_geometry(win: tk.Tk, w_ratio=0.90, h_ratio=0.90, min_w=1100, min_h=650):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()

    w = max(int(sw * w_ratio), min_w)
    h = max(int(sh * h_ratio), min_h)

    x = (sw - w) // 2
    y = (sh - h) // 2

    win.geometry(f"{w}x{h}+{x}+{y}")
    win.minsize(min_w, min_h)
    win.resizable(True, True)


class AppLogin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login - Sistema de Salon")

        aplicar_estilos_ttk(self)
        set_responsive_geometry(self)

        main = ttk.Frame(self, style="Main.TFrame", padding=24)
        main.pack(fill="both", expand=True)

        card = ttk.Frame(main, style="Card.TFrame")
        card.place(relx=0.5, rely=0.5, anchor="center")

        self.logo_img = _load_logo_scaled(LOGO_PATH, max_w=520, max_h=180)
        if self.logo_img:
            tk.Label(card, image=self.logo_img, bg=BG_CARDS, borderwidth=0, highlightthickness=0) \
                .grid(row=0, column=0, columnspan=2, pady=(20, 12))
        else:
            ttk.Label(card, text="LOGO", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(20, 12))

        ttk.Label(card, text="Inicio de sesion", style="Title.TLabel").grid(row=1, column=0, columnspan=2, pady=(0, 6))
        ttk.Label(card, text="Ingresa tus credenciales para continuar.", style="Hint.TLabel") \
            .grid(row=2, column=0, columnspan=2, pady=(0, 14))

        form = ttk.Frame(card, style="Card.TFrame")
        form.grid(row=3, column=0, columnspan=2, padx=26, pady=(0, 10), sticky="we")

        ttk.Label(form, text="Usuario", style="Label.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.var_user = tk.StringVar()
        self.ent_user = ttk.Entry(form, textvariable=self.var_user, style="Big.TEntry", width=70)
        self.ent_user.grid(row=1, column=0, columnspan=2, sticky="we", pady=(0, 14))

        ttk.Label(form, text="Contrasena", style="Label.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 6))
        self.var_pass = tk.StringVar()

        self._pwd_shown = False
        self.ent_pass = ttk.Entry(form, textvariable=self.var_pass, show="*", style="Big.TEntry", width=44)
        self.ent_pass.grid(row=3, column=0, sticky="we", pady=(0, 10), padx=(0, 8))

        self._img_eye_open = _load_icon(os.path.join(BASE_DIR, "eye.png"), target_px=18)
        self._img_eye_closed = _load_icon(os.path.join(BASE_DIR, "eye_off.png"), target_px=18)

        if self._img_eye_closed:
            self.btn_toggle_pwd = ttk.Button(form, image=self._img_eye_closed, style="Icon.TButton",
                                             command=self._toggle_password)
        else:
            self.btn_toggle_pwd = ttk.Button(form, text="VER", style="Icon.TButton", command=self._toggle_password)
        self.btn_toggle_pwd.grid(row=3, column=1, sticky="e", pady=(0, 10))

        btn = ttk.Button(card, text="Iniciar sesion", style="Primary.TButton", command=self.iniciar_sesion)
        btn.grid(row=4, column=0, columnspan=2, padx=26, pady=(10, 22), sticky="we")

        self.ent_user.bind("<Return>", lambda e: self.iniciar_sesion())
        self.ent_pass.bind("<Return>", lambda e: self.iniciar_sesion())

        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=0)

        self.ent_user.focus_set()

    def _toggle_password(self):
        self._pwd_shown = not self._pwd_shown
        self.ent_pass.configure(show="" if self._pwd_shown else "*")
        if self._pwd_shown:
            if self._img_eye_open:
                self.btn_toggle_pwd.configure(image=self._img_eye_open, text="")
            else:
                self.btn_toggle_pwd.configure(text="OCULTAR")
        else:
            if self._img_eye_closed:
                self.btn_toggle_pwd.configure(image=self._img_eye_closed, text="")
            else:
                self.btn_toggle_pwd.configure(text="VER")

    def _volver_al_login(self):
        self.var_user.set("")
        self.var_pass.set("")
        self._pwd_shown = False
        self.ent_pass.configure(show="*")

        self.deiconify()
        self.lift()
        self.focus_force()
        self.ent_user.focus_set()

    def iniciar_sesion(self):
        username = self.var_user.get().strip()
        passwd = self.var_pass.get()
        if not username or not passwd:
            messagebox.showwarning("Validacion", "Ingresa usuario y contrasena.")
            return

        user = db.obtener_usuario(username)
        if not user:
            messagebox.showerror("Error", "Usuario no encontrado.")
            return

        _id, _u, p_hash, fallos, locked, role, active = user

        if locked:
            messagebox.showerror("Bloqueado", "Usuario bloqueado.\nContacta al administrador.")
            return

        if not active:
            messagebox.showerror("Inactivo", "Usuario desactivado.\nContacta al administrador.")
            return

        if hash_password(passwd) == p_hash:
            db.reset_intentos(username)
            user_info = {"id": _id, "username": _u, "role": role}
            self.withdraw()

            self.sede_win = SeleccionSede(self, user_info=user_info, on_logout=self._volver_al_login)
        else:
            restantes = max(0, 3 - (fallos + 1))
            nuevos_fallos = db.registrar_fallo(username)
            if restantes == 0 or nuevos_fallos >= 3:
                messagebox.showerror("Bloqueado", "Contrasena incorrecta. Usuario BLOQUEADO.")
            else:
                messagebox.showerror("Error", f"Contrasena incorrecta. Intentos restantes: {restantes}")


db.init_db()
app = AppLogin()
app.mainloop()