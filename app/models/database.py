"""
models/database.py - Capa de acceso a datos
Gestión de conexión SQLite y bootstrap inicial
"""

import sqlite3
import os
import hashlib
from flask import g, current_app

DB_PATH = os.path.join(os.path.dirname(__file__), "../../instance/secureshop.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            DB_PATH,
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ── Usuarios ──────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            email       TEXT    NOT NULL,
            rol         TEXT    NOT NULL DEFAULT 'cliente',
            activo      INTEGER NOT NULL DEFAULT 1,
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Productos ─────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sku         TEXT    NOT NULL UNIQUE,
            nombre      TEXT    NOT NULL,
            descripcion TEXT,
            precio      REAL    NOT NULL,
            stock       INTEGER NOT NULL DEFAULT 0,
            categoria   TEXT,
            activo      INTEGER NOT NULL DEFAULT 1
        )
    """)

    # ── Pedidos ───────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id  INTEGER NOT NULL,
            estado      TEXT    NOT NULL DEFAULT 'pendiente',
            total       REAL    NOT NULL DEFAULT 0,
            notas       TEXT,
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    # ── Detalle de pedidos ────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pedido_items (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id   INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad    INTEGER NOT NULL,
            precio_unit REAL    NOT NULL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    # ── Reseñas ───────────────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resenas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            usuario_id  INTEGER NOT NULL,
            comentario  TEXT,
            puntuacion  INTEGER,
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producto_id) REFERENCES productos(id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    # ── Logs de sistema ───────────────────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS system_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nivel       TEXT,
            mensaje     TEXT,
            usuario     TEXT,
            ip          TEXT,
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Seed: Usuarios ────────────────────────────────────────────────────────
    usuarios = [
        ("admin",    _hash_password("Admin2024!"),     "admin@secureshop.cl",    "admin"),
        ("jperez",   _hash_password("Comercial#99"),   "j.perez@secureshop.cl",  "vendedor"),
        ("mlopez",   _hash_password("Lopez2023"),      "m.lopez@secureshop.cl",  "vendedor"),
        ("cliente1", _hash_password("pass123"),        "cliente1@ejemplo.cl",    "cliente"),
        ("cliente2", _hash_password("miClave456"),     "cliente2@ejemplo.cl",    "cliente"),
        ("auditor",  _hash_password("Audit0r!"),       "auditor@secureshop.cl",  "auditor"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO usuarios (username, password, email, rol) VALUES (?,?,?,?)",
        usuarios,
    )

    # ── Seed: Productos ───────────────────────────────────────────────────────
    productos = [
        ("SKU-001", "Laptop ProBook 15",        "Laptop empresarial 15\" Intel i7",    899990, 25, "Computación"),
        ("SKU-002", "Monitor UltraWide 34\"",   "Monitor curvo 3440x1440 144Hz",       449990, 12, "Periféricos"),
        ("SKU-003", "Teclado Mecánico TKL",     "Switch Cherry MX Red, retroiluminado",  79990, 50, "Periféricos"),
        ("SKU-004", "Mouse Ergonómico Pro",     "Diseño ergonómico, 6 botones DPI ajust",  34990, 80, "Periféricos"),
        ("SKU-005", "Hub USB-C 7 en 1",         "HDMI 4K, USB 3.0, SD, PD 100W",       29990, 60, "Accesorios"),
        ("SKU-006", "SSD NVMe 1TB",             "PCIe Gen4, 7000MB/s lectura",         119990, 35, "Almacenamiento"),
        ("SKU-007", "Auriculares ANC Pro",      "Cancelación activa de ruido, BT 5.2",  89990, 20, "Audio"),
        ("SKU-008", "Webcam 4K Stream",         "Autoenfoque, micrófono dual stereo",   69990, 15, "Video"),
        ("SKU-009", "Silla Ergonómica Mesh",    "Soporte lumbar ajustable, 8h uso",    299990, 8,  "Mobiliario"),
        ("SKU-010", "Dock Station Thunderbolt", "2x TB4, 2.5G Ethernet, 96W PD",      199990, 10, "Accesorios"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO productos (sku, nombre, descripcion, precio, stock, categoria) VALUES (?,?,?,?,?,?)",
        productos,
    )

    # ── Seed: Pedidos y detalles ──────────────────────────────────────────────
    cur.execute(
        "INSERT OR IGNORE INTO pedidos (id, usuario_id, estado, total, notas) VALUES (1, 4, 'completado', 979980, 'Entrega en oficina')"
    )
    cur.execute(
        "INSERT OR IGNORE INTO pedido_items (pedido_id, producto_id, cantidad, precio_unit) VALUES (1, 1, 1, 899990)"
    )
    cur.execute(
        "INSERT OR IGNORE INTO pedido_items (pedido_id, producto_id, cantidad, precio_unit) VALUES (1, 4, 1, 79990)"
    )
    cur.execute(
        "INSERT OR IGNORE INTO pedidos (id, usuario_id, estado, total, notas) VALUES (2, 5, 'pendiente', 449990, NULL)"
    )
    cur.execute(
        "INSERT OR IGNORE INTO pedido_items (pedido_id, producto_id, cantidad, precio_unit) VALUES (2, 2, 1, 449990)"
    )

    # ── Seed: Reseñas ─────────────────────────────────────────────────────────
    cur.execute(
        "INSERT OR IGNORE INTO resenas (id, producto_id, usuario_id, comentario, puntuacion) VALUES (1, 1, 4, 'Excelente laptop, muy rápida para el trabajo.', 5)"
    )
    cur.execute(
        "INSERT OR IGNORE INTO resenas (id, producto_id, usuario_id, comentario, puntuacion) VALUES (2, 2, 5, 'El monitor es espectacular, los colores son increíbles.', 5)"
    )

    conn.commit()
    conn.close()
