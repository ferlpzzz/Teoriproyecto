import sqlite3

DB_FILE = "salon.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    crear_tabla_users()
    asegurar_columnas_users()
    crear_tabla_sedes()
    ensure_sedes_iniciales()
    crear_tabla_categorias_inventario()
    crear_tabla_inventario()
    asegurar_columna_precio()
    asegurar_columna_categoria_id()
    crear_tabla_ventas()
    crear_tabla_servicios()
    seed_servicios()
    crear_tabla_citas()
    asegurar_columnas_citas()
    crear_tabla_empleadas()
    seed_empleadas()

def crear_bd_y_tabla():
    init_db()

# -------------------------- USERS / LOGIN --------------------------

def crear_tabla_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'dependiente',
            active INTEGER NOT NULL DEFAULT 1,
            failed_attempts INTEGER NOT NULL DEFAULT 0,
            locked INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def asegurar_columnas_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(users)")
    cols = [c[1] for c in cur.fetchall()]
    try:
        if "role" not in cols:
            cur.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'dependiente'")
        if "active" not in cols:
            cur.execute("ALTER TABLE users ADD COLUMN active INTEGER NOT NULL DEFAULT 1")
        if "failed_attempts" not in cols:
            cur.execute("ALTER TABLE users ADD COLUMN failed_attempts INTEGER NOT NULL DEFAULT 0")
        if "locked" not in cols:
            cur.execute("ALTER TABLE users ADD COLUMN locked INTEGER NOT NULL DEFAULT 0")
        conn.commit()
    except Exception:
        pass
    conn.close()

def usuario_existe(username: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE username=?", (username,))
    ok = cur.fetchone() is not None
    conn.close()
    return ok

def insertar_usuario(username, first_name, last_name, email, password_hash, role="dependiente"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users(username, first_name, last_name, email, password_hash, role, active, failed_attempts, locked)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (username, first_name, last_name, email, password_hash, role, 1, 0, 0))
    conn.commit()
    conn.close()

def obtener_usuario(username: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, username, password_hash, failed_attempts, locked, role, active
        FROM users
        WHERE username=?
    """, (username,))
    row = cur.fetchone()
    conn.close()
    return row

def registrar_fallo(username: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET failed_attempts = failed_attempts + 1 WHERE username=?", (username,))
    conn.commit()
    cur.execute("SELECT failed_attempts FROM users WHERE username=?", (username,))
    fa_row = cur.fetchone()
    if fa_row and int(fa_row[0]) >= 3:
        cur.execute("UPDATE users SET locked=1 WHERE username=?", (username,))
        conn.commit()
    conn.close()
    return int(fa_row[0]) if fa_row else 0

def reset_intentos(username: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET failed_attempts=0, locked=0 WHERE username=?", (username,))
    conn.commit()
    conn.close()

def listar_usuarios():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, username, first_name, last_name, email, role, active, locked
        FROM users
        ORDER BY id ASC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def obtener_usuario_por_id(uid: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, username, first_name, last_name, email, role, active, locked
        FROM users
        WHERE id=?
    """, (int(uid),))
    row = cur.fetchone()
    conn.close()
    return row

def actualizar_usuario(uid: int, first_name: str, last_name: str, email: str, role: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET first_name=?, last_name=?, email=?, role=?
        WHERE id=?
    """, (first_name, last_name, email, role, int(uid)))
    conn.commit()
    conn.close()

def cambiar_password_usuario(uid: int, password_hash: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash=? WHERE id=?", (password_hash, int(uid)))
    conn.commit()
    conn.close()

def toggle_usuario_activo(uid: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT active FROM users WHERE id=?", (int(uid),))
    row = cur.fetchone()
    if not row:
        conn.close()
        return
    nuevo = 0 if int(row[0]) == 1 else 1
    cur.execute("UPDATE users SET active=? WHERE id=?", (nuevo, int(uid)))
    conn.commit()
    conn.close()

def eliminar_usuario(uid: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (int(uid),))
    conn.commit()
    conn.close()

# -------------------------- SEDES --------------------------

def crear_tabla_sedes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sedes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            ubicacion TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def ensure_sedes_iniciales():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sedes")
    n = int(cur.fetchone()[0] or 0)
    if n == 0:
        cur.execute("INSERT INTO sedes(nombre, ubicacion) VALUES (?, ?)", ("Salon de uñas", "Ubicación"))
        cur.execute("INSERT INTO sedes(nombre, ubicacion) VALUES (?, ?)", ("Salon de cabello", "Ubicación"))
    conn.commit()
    conn.close()

def listar_sedes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, ubicacion FROM sedes ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    return rows

def obtener_sede(sede_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, ubicacion FROM sedes WHERE id=?", (int(sede_id),))
    row = cur.fetchone()
    conn.close()
    return row

def insertar_sede(nombre: str, ubicacion: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO sedes(nombre, ubicacion) VALUES (?, ?)", (nombre, ubicacion))
    conn.commit()
    conn.close()

def eliminar_sede(sede_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sedes WHERE id=?", (int(sede_id),))
    conn.commit()
    conn.close()

def sede_es_unas(sede_id: int) -> bool:
    row = obtener_sede(sede_id)
    if not row:
        return False
    nombre = (row[1] or "").lower()
    return "uña" in nombre

# -------------------------- CATEGORIAS INVENTARIO --------------------------

def crear_tabla_categorias_inventario():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categorias_inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sede_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            UNIQUE(sede_id, nombre),
            FOREIGN KEY(sede_id) REFERENCES sedes(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def listar_categorias_inventario(sede_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nombre
        FROM categorias_inventario
        WHERE sede_id=?
        ORDER BY nombre ASC
    """, (int(sede_id),))
    rows = cur.fetchall()
    conn.close()
    return rows

def insertar_categoria_inventario(sede_id: int, nombre: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO categorias_inventario(sede_id, nombre)
        VALUES (?, ?)
    """, (int(sede_id), nombre.strip()))
    conn.commit()
    conn.close()

# -------------------------- INVENTARIO --------------------------

def crear_tabla_inventario():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sede_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            precio REAL NOT NULL DEFAULT 0.0,
            categoria_id INTEGER,
            FOREIGN KEY(sede_id) REFERENCES sedes(id) ON DELETE CASCADE,
            FOREIGN KEY(categoria_id) REFERENCES categorias_inventario(id) ON DELETE SET NULL
        )
    """)
    conn.commit()
    conn.close()

def asegurar_columna_precio():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE inventario ADD COLUMN precio REAL NOT NULL DEFAULT 0.0")
        conn.commit()
    except Exception:
        pass
    conn.close()

def asegurar_columna_categoria_id():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(inventario)")
    cols = [c[1] for c in cur.fetchall()]
    try:
        if "categoria_id" not in cols:
            cur.execute("ALTER TABLE inventario ADD COLUMN categoria_id INTEGER")
            conn.commit()
    except Exception:
        pass
    conn.close()

def listar_inventario(sede_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT i.id, i.nombre, i.stock, i.precio, COALESCE(c.nombre, '') as categoria
        FROM inventario i
        LEFT JOIN categorias_inventario c ON c.id = i.categoria_id
        WHERE i.sede_id=?
        ORDER BY i.nombre ASC
    """, (int(sede_id),))
    rows = cur.fetchall()
    conn.close()
    return rows

def insertar_producto(sede_id, nombre, stock, precio, categoria_id=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO inventario(sede_id, nombre, stock, precio, categoria_id)
        VALUES (?,?,?,?,?)
    """, (int(sede_id), nombre, int(stock), float(precio), int(categoria_id) if categoria_id else None))
    conn.commit()
    conn.close()

def actualizar_producto(pid, nombre, stock, precio, categoria_id=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE inventario
        SET nombre=?, stock=?, precio=?, categoria_id=?
        WHERE id=?
    """, (nombre, int(stock), float(precio), int(categoria_id) if categoria_id else None, int(pid)))
    conn.commit()
    conn.close()

def eliminar_producto(pid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM inventario WHERE id=?", (int(pid),))
    conn.commit()
    conn.close()

def ajustar_stock(sede_id: int, pid: int, delta: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT stock FROM inventario WHERE id=? AND sede_id=?", (int(pid), int(sede_id)))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise ValueError("Producto no encontrado para esta sede.")
    actual = int(row[0] or 0)
    nuevo = actual + int(delta)
    if nuevo < 0:
        conn.close()
        raise ValueError("No puedes dejar el stock en negativo.")
    cur.execute("UPDATE inventario SET stock=? WHERE id=?", (nuevo, int(pid)))
    conn.commit()
    conn.close()

# -------------------------- VENTAS --------------------------

def crear_tabla_ventas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sede_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            total REAL NOT NULL,
            fecha TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            FOREIGN KEY(sede_id) REFERENCES sedes(id) ON DELETE CASCADE,
            FOREIGN KEY(producto_id) REFERENCES inventario(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def registrar_venta(sede_id, producto_id, cantidad, precio_unitario):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT stock FROM inventario WHERE id=? AND sede_id=?", (int(producto_id), int(sede_id)))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise ValueError("Producto no encontrado para esta sede.")
    stock_actual = int(row[0] or 0)
    cantidad = int(cantidad)
    if cantidad <= 0 or cantidad > stock_actual:
        conn.close()
        raise ValueError("Cantidad inválida o stock insuficiente.")
    nuevo_stock = stock_actual - cantidad
    cur.execute("UPDATE inventario SET stock=? WHERE id=?", (nuevo_stock, int(producto_id)))
    total = float(precio_unitario) * cantidad
    cur.execute("""
        INSERT INTO ventas(sede_id, producto_id, cantidad, precio_unitario, total)
        VALUES (?,?,?,?,?)
    """, (int(sede_id), int(producto_id), int(cantidad), float(precio_unitario), float(total)))
    conn.commit()
    conn.close()

# -------------------------- SERVICIOS --------------------------

def crear_tabla_servicios():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sede_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            FOREIGN KEY(sede_id) REFERENCES sedes(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def listar_servicios(sede_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, precio FROM servicios WHERE sede_id=? ORDER BY nombre ASC", (int(sede_id),))
    rows = cur.fetchall()
    conn.close()
    return rows

def _servicios_cabello():
    return [
        ("Lavado de Cabello", 50),
        ("Corte de cabello dama", 50),
        ("corte de caballero", 40),
        ("Combo de lavado/Corte/Planchado", 100),
    ]

def _servicios_unias():
    return [
        ("manicure gelish", 80),
        ("pedicure con gelish", 120),
        ("Planchado de ceja con depilación", 100),
        ("Rizado de pestañas", 100),
        ("Uñas acrílicas corta", 150),
    ]

def seed_servicios():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM sedes ORDER BY id ASC")
    sedes = cur.fetchall()
    for (sid, nombre) in sedes:
        cur.execute("SELECT COUNT(*) FROM servicios WHERE sede_id=?", (int(sid),))
        n = int(cur.fetchone()[0] or 0)
        if n == 0:
            data = _servicios_unias() if "uña" in (nombre or "").lower() else _servicios_cabello()
            for (nom, precio) in data:
                cur.execute("INSERT INTO servicios(sede_id, nombre, precio) VALUES (?,?,?)", (int(sid), nom, float(precio)))
    conn.commit()
    conn.close()

# -------------------------- CITAS --------------------------

def crear_tabla_citas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sede_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            cliente TEXT NOT NULL,
            servicio TEXT NOT NULL,
            inicio TEXT NOT NULL,
            fin TEXT NOT NULL,
            servicio_id INTEGER,
            servicio_nombre TEXT,
            precio REAL DEFAULT 0.0,
            empleada TEXT,
            estado TEXT NOT NULL DEFAULT 'PENDIENTE',
            nit_receptor TEXT,
            nombre_receptor TEXT,
            apellidos_receptor TEXT,
            facturado_en TEXT,
            FOREIGN KEY(sede_id) REFERENCES sedes(id) ON DELETE CASCADE,
            FOREIGN KEY(servicio_id) REFERENCES servicios(id) ON DELETE SET NULL
        )
    """)
    conn.commit()
    conn.close()

def asegurar_columnas_citas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(citas)")
    cols = [c[1] for c in cur.fetchall()]
    try:
        if "servicio_id" not in cols:
            cur.execute("ALTER TABLE citas ADD COLUMN servicio_id INTEGER")
        if "servicio_nombre" not in cols:
            cur.execute("ALTER TABLE citas ADD COLUMN servicio_nombre TEXT")
        if "precio" not in cols:
            cur.execute("ALTER TABLE citas ADD COLUMN precio REAL DEFAULT 0.0")
        if "empleada" not in cols:
            cur.execute("ALTER TABLE citas ADD COLUMN empleada TEXT")
        if "estado" not in cols:
            cur.execute("ALTER TABLE citas ADD COLUMN estado TEXT NOT NULL DEFAULT 'PENDIENTE'")
        if "nit_receptor" not in cols:
            cur.execute("ALTER TABLE citas ADD COLUMN nit_receptor TEXT")
        if "nombre_receptor" not in cols:
            cur.execute("ALTER TABLE citas ADD COLUMN nombre_receptor TEXT")
        if "apellidos_receptor" not in cols:
            cur.execute("ALTER TABLE citas ADD COLUMN apellidos_receptor TEXT")
        if "facturado_en" not in cols:
            cur.execute("ALTER TABLE citas ADD COLUMN facturado_en TEXT")
        conn.commit()
    except Exception:
        pass
    conn.close()

def listar_citas(sede_id: int, fecha: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, cliente,
               COALESCE(servicio_nombre, servicio) as servicio_mostrar,
               inicio, fin, COALESCE(precio, 0.0) as precio_mostrar,
               empleada,
               COALESCE(estado, 'PENDIENTE') as estado
        FROM citas
        WHERE sede_id=? AND fecha=?
        ORDER BY inicio ASC
    """, (int(sede_id), fecha))
    rows = cur.fetchall()
    conn.close()
    return rows

def marcar_cita_atendida(cid: int, nit_receptor: str, nombre_receptor: str, apellidos_receptor: str, facturado_en: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE citas
        SET estado='ATENDIDA',
            nit_receptor=?,
            nombre_receptor=?,
            apellidos_receptor=?,
            facturado_en=?
        WHERE id=?
        """,
        (nit_receptor, nombre_receptor, apellidos_receptor, facturado_en, int(cid))
    )
    conn.commit()
    conn.close()

def insertar_cita(sede_id: int, fecha: str, cliente: str, servicio: str, inicio: str, fin: str,
                  servicio_id: int = None, servicio_nombre: str = None, precio: float = 0.0,
                  empleada: str = None) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO citas(sede_id, fecha, cliente, servicio, inicio, fin, servicio_id, servicio_nombre, precio, empleada)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (int(sede_id), fecha, cliente, servicio, inicio, fin,
          int(servicio_id) if servicio_id else None, servicio_nombre, float(precio), empleada))
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return int(cid)

def actualizar_cita(cid: int, cliente: str, servicio: str, inicio: str, fin: str,
                    servicio_id: int = None, servicio_nombre: str = None, precio: float = None,
                    empleada: str = None):
    conn = get_connection()
    cur = conn.cursor()
    if precio is None:
        cur.execute("""
            UPDATE citas
            SET cliente=?, servicio=?, inicio=?, fin=?, servicio_id=?, servicio_nombre=?, empleada=?
            WHERE id=?
        """, (cliente, servicio, inicio, fin,
              int(servicio_id) if servicio_id else None, servicio_nombre, empleada, int(cid)))
    else:
        cur.execute("""
            UPDATE citas
            SET cliente=?, servicio=?, inicio=?, fin=?, servicio_id=?, servicio_nombre=?, precio=?, empleada=?
            WHERE id=?
        """, (cliente, servicio, inicio, fin,
              int(servicio_id) if servicio_id else None, servicio_nombre, float(precio), empleada, int(cid)))
    conn.commit()
    conn.close()

def eliminar_cita(cid: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM citas WHERE id=?", (int(cid),))
    conn.commit()
    conn.close()

def obtener_cita(cid: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, sede_id, fecha, cliente, servicio, inicio, fin, servicio_id, servicio_nombre, precio, empleada
        FROM citas
        WHERE id=?
    """, (int(cid),))
    row = cur.fetchone()
    conn.close()
    return row


def crear_tabla_empleadas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS empleadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sede_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1,
            UNIQUE(sede_id, nombre),
            FOREIGN KEY(sede_id) REFERENCES sedes(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()


def seed_empleadas():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, nombre FROM sedes ORDER BY id ASC")
    sedes = cur.fetchall()

    for sid, sname in sedes:
        nombre_s = (sname or "").lower()

        if "uña" in nombre_s:
            empleados = ["Angelica", "Yoli"]
        else:
            empleados = ["Mely"]

        for nom in empleados:
            try:
                cur.execute(
                    "INSERT OR IGNORE INTO empleadas(sede_id, nombre, activo) VALUES (?,?,1)",
                    (int(sid), nom.strip())
                )
            except Exception:
                pass

    conn.commit()
    conn.close()


def listar_empleadas(sede_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nombre
        FROM empleadas
        WHERE sede_id=? AND activo=1
        ORDER BY nombre ASC
    """, (int(sede_id),))
    rows = cur.fetchall()
    conn.close()
    return rows
