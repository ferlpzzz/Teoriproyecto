import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
import db

BG_PRIMARY = "#fff5f7"
BG_SECONDARY = "#f3d6dc"
BG_CARDS = "#ffffff"
ACCENT = "#da5d86"
TEXT = "#0b1011"
BUTTONS = "#01a6b2"
BUTTONS_SECONDARY = "#028a94"
WARNING = "#f3d6dc"
ERROR = "#f3d6dc"


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
        relief="flat"
    )

    style.configure(
        "Soft.TEntry",
        fieldbackground="white",
        bordercolor=BG_SECONDARY,
        borderwidth=1,
        relief="flat",
        padding=8,
        font=("Segoe UI", 12)
    )
    style.map(
        "Soft.TEntry",
        lightcolor=[("focus", ACCENT)],
        bordercolor=[("focus", ACCENT)]
    )


def _load_icon_18px(path: str, target_px: int = 18):
    """
    Carga un PNG como PhotoImage y lo reduce con subsample()
    para que quede aprox de target_px de alto/ancho.
    (Tkinter no tiene resize real sin Pillow; subsample reduce por factores enteros)
    """
    try:
        img = tk.PhotoImage(file=path)
        w, h = img.width(), img.height()
        if w <= 0 or h <= 0:
            return img

        # factor entero para acercar el alto a target_px
        # ej: si h=72 -> factor=4 -> 18px aprox
        factor = max(1, round(h / target_px))
        img_small = img.subsample(factor, factor)
        return img_small
    except Exception:
        return None


class CambiarPasswordDialog(tk.Toplevel):
    MIN_LEN = 6

    def __init__(self, parent, username="Usuario"):
        super().__init__(parent)
        self.parent = parent
        self.result = None

        self.title("Cambiar contraseña")
        self.configure(bg=BG_PRIMARY)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        _apply_ttk_styles(self)

        self.var_pass1 = tk.StringVar()
        self.var_pass2 = tk.StringVar()
        self.var_show1 = tk.BooleanVar(value=False)
        self.var_show2 = tk.BooleanVar(value=False)
        self.var_msg = tk.StringVar(value="")

        # --- iconos 18px ---
        # Importante: guardar referencia en self para que no se "borren"
        self.icon_eye = _load_icon_18px("eye.png", 18)
        self.icon_eye_off = _load_icon_18px("eye_off.png", 18)

        card = tk.Frame(self, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        card.pack(padx=22, pady=22, fill="both", expand=True)

        header = tk.Frame(card, bg=BG_CARDS)
        header.pack(fill="x", padx=22, pady=(20, 10))

        icon = tk.Canvas(header, width=44, height=44, bg=BG_CARDS, highlightthickness=0)
        icon.pack(side="left")
        icon.create_oval(4, 4, 40, 40, fill=ACCENT, outline=ACCENT)
        icon.create_text(22, 22, text="🔒", font=("Segoe UI", 16), fill="white")

        title_wrap = tk.Frame(header, bg=BG_CARDS)
        title_wrap.pack(side="left", padx=12)

        tk.Label(
            title_wrap, text="Cambiar contraseña",
            bg=BG_CARDS, fg=TEXT,
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w")

        tk.Label(
            title_wrap, text=f"Usuario: {username}",
            bg=BG_CARDS, fg="#4b5563",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(2, 0))

        body = tk.Frame(card, bg=BG_CARDS)
        body.pack(fill="both", expand=True, padx=22, pady=10)
        body.grid_columnconfigure(0, weight=1)

        tk.Label(
            body,
            text="Escribe la nueva contraseña y confírmala.",
            bg=BG_CARDS, fg="#4b5563",
            font=("Segoe UI", 10)
        ).grid(row=0, column=0, sticky="w", pady=(0, 14))

        # -------- Campo 1
        box1 = tk.Frame(body, bg=BG_CARDS)
        box1.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        box1.grid_columnconfigure(0, weight=1)

        tk.Label(
            box1, text="Nueva contraseña",
            bg=BG_CARDS, fg="#4b5563",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        row1 = tk.Frame(box1, bg=BG_CARDS)
        row1.grid(row=1, column=0, sticky="ew")
        row1.grid_columnconfigure(0, weight=1)

        self.e1 = ttk.Entry(row1, textvariable=self.var_pass1, style="Soft.TEntry", show="*")
        self.e1.grid(row=0, column=0, sticky="ew")

        self.btn_show1 = tk.Button(
            row1,
            bg=BG_SECONDARY, fg=TEXT, bd=0,
            cursor="hand2",
            activebackground="#eac7cf",
            command=self._toggle1
        )
        self.btn_show1.grid(row=0, column=1, padx=(8, 0), ipadx=8, ipady=4)

        # -------- Campo 2
        box2 = tk.Frame(body, bg=BG_CARDS)
        box2.grid(row=2, column=0, sticky="ew", pady=(0, 6))
        box2.grid_columnconfigure(0, weight=1)

        tk.Label(
            box2, text="Confirmar contraseña",
            bg=BG_CARDS, fg="#4b5563",
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(10, 6))

        row2 = tk.Frame(box2, bg=BG_CARDS)
        row2.grid(row=1, column=0, sticky="ew")
        row2.grid_columnconfigure(0, weight=1)

        self.e2 = ttk.Entry(row2, textvariable=self.var_pass2, style="Soft.TEntry", show="*")
        self.e2.grid(row=0, column=0, sticky="ew")

        self.btn_show2 = tk.Button(
            row2,
            bg=BG_SECONDARY, fg=TEXT, bd=0,
            cursor="hand2",
            activebackground="#eac7cf",
            command=self._toggle2
        )
        self.btn_show2.grid(row=0, column=1, padx=(8, 0), ipadx=8, ipady=4)

        self._refresh_eye_buttons()

        self.lbl_msg = tk.Label(
            body, textvariable=self.var_msg,
            bg=BG_CARDS, fg="#b91c1c",
            font=("Segoe UI", 9, "bold")
        )
        self.lbl_msg.grid(row=3, column=0, sticky="w", pady=(10, 0))

        footer = tk.Frame(card, bg=BG_CARDS)
        footer.pack(fill="x", padx=22, pady=(14, 20))
        footer.grid_columnconfigure(0, weight=1)
        footer.grid_columnconfigure(1, weight=1)

        btn_cancel = tk.Button(
            footer, text="Cancelar",
            bg=BG_SECONDARY, fg=TEXT, bd=0,
            cursor="hand2",
            font=("Segoe UI", 12, "bold"),
            activebackground="#eac7cf",
            command=self._cancel
        )
        btn_cancel.grid(row=0, column=0, sticky="we", padx=(0, 10), ipady=12)

        btn_ok = tk.Button(
            footer, text="Guardar contraseña",
            bg=BUTTONS, fg="white", bd=0,
            activebackground=BUTTONS_SECONDARY,
            cursor="hand2",
            font=("Segoe UI", 12, "bold"),
            command=self._ok
        )
        btn_ok.grid(row=0, column=1, sticky="we", padx=(10, 0), ipady=12)

        self.var_pass1.trace_add("write", lambda *_: self._validate(live=True))
        self.var_pass2.trace_add("write", lambda *_: self._validate(live=True))
        self.bind("<Escape>", lambda e: self._cancel())
        self.bind("<Return>", lambda e: self._ok())

        self._center()
        self.e1.focus_force()

    def _center(self):
        self.update_idletasks()
        pw = self.parent.winfo_width()
        ph = self.parent.winfo_height()
        px = self.parent.winfo_rootx()
        py = self.parent.winfo_rooty()

        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _refresh_eye_buttons(self):
        def _apply(btn, show_state: bool):
            if self.icon_eye and self.icon_eye_off:
                btn.config(
                    image=self.icon_eye if show_state else self.icon_eye_off,
                    text="",
                    compound="center",
                    width=24, height=24  # área clicable cómoda aunque el icono sea 18px
                )
            else:
                btn.config(
                    text="👁" if not show_state else "🙈",
                    width=3
                )

        _apply(self.btn_show1, self.var_show1.get())
        _apply(self.btn_show2, self.var_show2.get())

    def _toggle1(self):
        self.var_show1.set(not self.var_show1.get())
        self.e1.configure(show="" if self.var_show1.get() else "*")
        self._refresh_eye_buttons()

    def _toggle2(self):
        self.var_show2.set(not self.var_show2.get())
        self.e2.configure(show="" if self.var_show2.get() else "*")
        self._refresh_eye_buttons()

    def _validate(self, live=False):
        p1 = self.var_pass1.get()
        p2 = self.var_pass2.get()

        if not p1 and not p2:
            self.var_msg.set("")
            return False

        if len(p1) < self.MIN_LEN:
            self.var_msg.set(f"La contraseña debe tener al menos {self.MIN_LEN} caracteres.")
            return False

        if p2 and p1 != p2:
            self.var_msg.set("Las contraseñas no coinciden.")
            return False

        self.var_msg.set("")
        return True

    def _cancel(self):
        self.result = None
        self.destroy()

    def _ok(self):
        p1 = self.var_pass1.get()
        p2 = self.var_pass2.get()

        if not p1 or not p2:
            self.var_msg.set("Completa ambos campos.")
            return

        if not self._validate(live=False):
            return

        self.result = {"password": p1}
        self.destroy()


class UsuariosFrame(tk.Frame):
    def __init__(self, master, user_role="administrador", sede_id=None):
        super().__init__(master, bg=BG_PRIMARY)
        self.user_role = user_role
        self.sede_id = sede_id

        _apply_ttk_styles(self)

        panel = tk.Frame(self, bg=BG_PRIMARY)
        panel.pack(expand=True, fill="both", padx=20, pady=20)

        card = tk.Frame(panel, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        card.pack(expand=True, fill="both")

        inner = tk.Frame(card, bg=BG_CARDS)
        inner.pack(expand=True, fill="both", padx=18, pady=16)

        inner.grid_rowconfigure(1, weight=1)
        inner.grid_columnconfigure(0, weight=1)

        tk.Label(
            inner, text="Gestión de Usuarios",
            bg=BG_CARDS, fg=TEXT,
            font=("Segoe UI", 20, "bold")
        ).grid(row=0, column=0, sticky="ew", pady=(4, 10))

        self.tree = ttk.Treeview(
            inner,
            columns=("ID", "Usuario", "Nombre", "Apellido", "Email", "Rol", "Estado"),
            show="headings",
            style="Soft.Treeview"
        )

        for col in ("ID", "Usuario", "Nombre", "Apellido", "Email", "Rol", "Estado"):
            self.tree.heading(col, text=col)

        self.tree.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        barra = tk.Frame(inner, bg=BG_CARDS)
        barra.grid(row=2, column=0, sticky="ew")

        def _btn(texto, bg, fg, cmd, w=16):
            tk.Button(
                barra, text=texto,
                bg=bg, fg=fg, bd=0,
                activebackground=BUTTONS_SECONDARY if bg == BUTTONS else bg,
                activeforeground=fg,
                cursor="hand2",
                font=("Segoe UI", 11, "bold"),
                width=w,
                command=cmd
            ).pack(side="left", padx=6, ipady=10)

        _btn("Nuevo usuario", BUTTONS, "white", self._nuevo_usuario, w=14)
        _btn("Editar", BUTTONS, "white", self._editar_usuario, w=10)
        _btn("Cambiar contraseña", WARNING, TEXT, self._cambiar_password, w=18)
        _btn("Activar/Desactivar", WARNING, TEXT, self._toggle_activo, w=18)
        _btn("Eliminar", ERROR, TEXT, self._eliminar_usuario, w=10)

        self._cargar_usuarios()

    def _cargar_usuarios(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            usuarios = db.listar_usuarios()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar usuarios:\n{e}")
            return

        for (uid, username, first_name, last_name, email, role, active, locked) in usuarios:
            if locked:
                estado = "Bloqueado"
            elif not active:
                estado = "Inactivo"
            else:
                estado = "Activo"

            role_display = "Admin" if role == "administrador" else "Dependiente"

            self.tree.insert(
                "", "end", iid=str(uid),
                values=(uid, username, first_name, last_name, email, role_display, estado)
            )

    def _nuevo_usuario(self):
        dlg = UsuarioDialog(self, title="Nuevo Usuario")
        self.wait_window(dlg)
        if dlg.result:
            username, first_name, last_name, email, password, role = dlg.result
            try:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                db.insertar_usuario(username, first_name, last_name, email, password_hash, role)
                self._cargar_usuarios()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _editar_usuario(self):
        sel = self.tree.selection()
        if not sel:
            return

        uid = int(sel[0])
        usuario = db.obtener_usuario_por_id(uid)
        if not usuario:
            return

        initial = {
            "username": usuario[1],
            "first_name": usuario[2],
            "last_name": usuario[3],
            "email": usuario[4],
            "role": usuario[5]
        }

        dlg = UsuarioDialog(self, title="Editar Usuario", initial=initial, edit_mode=True)
        self.wait_window(dlg)
        if dlg.result:
            _, first_name, last_name, email, _, role = dlg.result
            db.actualizar_usuario(uid, first_name, last_name, email, role)
            self._cargar_usuarios()

    def _cambiar_password(self):
        sel = self.tree.selection()
        if not sel:
            return

        uid = int(sel[0])
        vals = self.tree.item(sel[0], "values")
        username = vals[1] if len(vals) > 1 else "Usuario"

        dlg = CambiarPasswordDialog(self.winfo_toplevel(), username=username)
        self.winfo_toplevel().wait_window(dlg)

        if not dlg.result:
            return

        new_pass = dlg.result["password"]
        password_hash = hashlib.sha256(new_pass.encode()).hexdigest()

        try:
            db.cambiar_password_usuario(uid, password_hash)
            messagebox.showinfo("Listo", "Contraseña actualizada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar la contraseña:\n{e}")

    def _toggle_activo(self):
        sel = self.tree.selection()
        if not sel:
            return

        uid = int(sel[0])
        db.toggle_usuario_activo(uid)
        self._cargar_usuarios()

    def _eliminar_usuario(self):
        sel = self.tree.selection()
        if not sel:
            return
        if not messagebox.askyesno("Eliminar", "¿Eliminar usuario?"):
            return

        uid = int(sel[0])
        db.eliminar_usuario(uid)
        self._cargar_usuarios()


class UsuarioDialog(tk.Toplevel):
    def __init__(self, master, title="Usuario", initial=None, edit_mode=False):
        super().__init__(master)
        self.result = None
        self.edit_mode = edit_mode
        self.title(title)
        self.configure(bg=BG_PRIMARY)
        self.resizable(False, False)

        _apply_ttk_styles(self)

        card = tk.Frame(self, bg=BG_CARDS, highlightthickness=1, highlightbackground=BG_SECONDARY)
        card.pack(padx=18, pady=18)

        frm = tk.Frame(card, bg=BG_CARDS)
        frm.pack(padx=18, pady=18)

        self.var_username = tk.StringVar(value=initial.get("username", "") if initial else "")
        self.var_first_name = tk.StringVar(value=initial.get("first_name", "") if initial else "")
        self.var_last_name = tk.StringVar(value=initial.get("last_name", "") if initial else "")
        self.var_email = tk.StringVar(value=initial.get("email", "") if initial else "")
        self.var_password = tk.StringVar()
        self.var_role = tk.StringVar(value=initial.get("role", "dependiente") if initial else "dependiente")

        row = 0

        def _lbl(txt):
            tk.Label(
                frm, text=txt, bg=BG_CARDS, fg=TEXT,
                font=("Segoe UI", 11, "bold")
            ).grid(row=row, column=0, sticky="e", padx=8, pady=8)

        def _ent(var, show=None):
            e = ttk.Entry(frm, textvariable=var, style="Soft.TEntry", show=show)
            e.grid(row=row, column=1, padx=8, pady=8, sticky="we")
            return e

        _lbl("Usuario:")
        ent_user = _ent(self.var_username)
        if edit_mode:
            ent_user.configure(state="disabled")
        row += 1

        _lbl("Nombre:")
        _ent(self.var_first_name)
        row += 1

        _lbl("Apellido:")
        _ent(self.var_last_name)
        row += 1

        _lbl("Email:")
        _ent(self.var_email)
        row += 1

        if not edit_mode:
            _lbl("Contraseña:")
            _ent(self.var_password, show="*")
            row += 1

        _lbl("Rol:")
        role_frame = tk.Frame(frm, bg=BG_CARDS)
        role_frame.grid(row=row, column=1, sticky="w")

        tk.Radiobutton(
            role_frame, text="Dependiente",
            variable=self.var_role, value="dependiente",
            bg=BG_CARDS, fg=TEXT, selectcolor=BG_CARDS
        ).pack(side="left", padx=10)

        tk.Radiobutton(
            role_frame, text="Administrador",
            variable=self.var_role, value="administrador",
            bg=BG_CARDS, fg=TEXT, selectcolor=BG_CARDS
        ).pack(side="left", padx=10)

        botones = tk.Frame(frm, bg=BG_CARDS)
        botones.grid(row=row + 1, column=0, columnspan=2, pady=(16, 0))

        tk.Button(
            botones, text="Guardar",
            bg=BUTTONS, fg="white",
            font=("Segoe UI", 11, "bold"),
            command=self._guardar
        ).pack(side="left", padx=6, ipadx=12, ipady=10)

        tk.Button(
            botones, text="Cancelar",
            bg=WARNING, fg=TEXT,
            font=("Segoe UI", 11, "bold"),
            command=self.destroy
        ).pack(side="left", padx=6, ipadx=12, ipady=10)

        self.grab_set()

    def _guardar(self):
        username = self.var_username.get().strip()
        first_name = self.var_first_name.get().strip()
        last_name = self.var_last_name.get().strip()
        email = self.var_email.get().strip()
        password = self.var_password.get()
        role = self.var_role.get()

        if not username or not first_name or not last_name or not email:
            return

        if not self.edit_mode and not password:
            return

        self.result = (username, first_name, last_name, email, password, role)
        self.destroy()
