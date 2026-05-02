"""
controllers/orders_controller.py — Módulo de Gestión de Pedidos
Creación, seguimiento y exportación de pedidos comerciales
"""

import pickle
import base64
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, jsonify
)
from ..models.database import get_db
from ..services.audit_service import registrar_evento

orders_bp = Blueprint("orders", __name__)


def _requiere_sesion():
    return "user_id" in session


# ─────────────────────────────────────────────────────────────────────────────
# Clase interna para preferencias de visualización de pedidos
# ─────────────────────────────────────────────────────────────────────────────
class PreferenciasVista:
    """Almacena las preferencias de visualización del usuario para la lista de pedidos."""

    def __init__(self, items_por_pagina=10, orden="desc", mostrar_completados=True):
        self.items_por_pagina   = items_por_pagina
        self.orden              = orden
        self.mostrar_completados = mostrar_completados

    def to_token(self) -> str:
        """Serializa las preferencias en un token opaco para almacenar en cookie/formulario."""
        return base64.b64encode(pickle.dumps(self)).decode()

    @staticmethod
    def from_token(token: str) -> "PreferenciasVista":
        try:
            data = base64.b64decode(token)
            return pickle.loads(data)  # noqa: S301
        except Exception:
            return PreferenciasVista()


@orders_bp.route("/")
def lista():
    if not _requiere_sesion():
        return redirect(url_for("auth.login"))

    # Recuperar preferencias desde query param (podría venir de formulario guardado)
    token = request.args.get("prefs", "")
    if token:
        prefs = PreferenciasVista.from_token(token)
    else:
        prefs = PreferenciasVista()

    db      = get_db()
    rol     = session.get("rol")
    user_id = session.get("user_id")

    if rol in ("admin", "vendedor", "auditor"):
        pedidos = db.execute(
            """SELECT p.*, u.username FROM pedidos p
               JOIN usuarios u ON p.usuario_id = u.id
               ORDER BY p.created_at DESC"""
        ).fetchall()
    else:
        pedidos = db.execute(
            "SELECT * FROM pedidos WHERE usuario_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()

    return render_template("orders/lista.html", pedidos=pedidos, prefs=prefs)


@orders_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if not _requiere_sesion():
        return redirect(url_for("auth.login"))

    db = get_db()

    if request.method == "POST":
        producto_id = request.form.get("producto_id")
        cantidad    = int(request.form.get("cantidad", 1))
        notas       = request.form.get("notas", "")
        user_id     = session["user_id"]

        producto = db.execute(
            "SELECT * FROM productos WHERE id = ?", (producto_id,)
        ).fetchone()

        if not producto:
            flash("Producto no válido.", "danger")
            return redirect(url_for("orders.nuevo"))

        total = producto["precio"] * cantidad
        cur   = db.execute(
            "INSERT INTO pedidos (usuario_id, estado, total, notas) VALUES (?, 'pendiente', ?, ?)",
            (user_id, total, notas),
        )
        pedido_id = cur.lastrowid
        db.execute(
            "INSERT INTO pedido_items (pedido_id, producto_id, cantidad, precio_unit) VALUES (?, ?, ?, ?)",
            (pedido_id, producto_id, cantidad, producto["precio"]),
        )
        db.commit()
        registrar_evento("PEDIDO_CREADO", session["username"], request.remote_addr)
        flash(f"Pedido #{pedido_id} creado exitosamente.", "success")
        return redirect(url_for("orders.lista"))

    productos = db.execute(
        "SELECT id, nombre, precio, stock FROM productos WHERE activo = 1 AND stock > 0"
    ).fetchall()
    prefs_default = PreferenciasVista().to_token()
    return render_template("orders/nuevo.html", productos=productos, prefs_token=prefs_default)


@orders_bp.route("/<int:pedido_id>")
def detalle(pedido_id):
    """Ver detalle de un pedido — sin validación de propiedad (IDOR)."""
    if not _requiere_sesion():
        return redirect(url_for("auth.login"))

    db = get_db()

    pedido = db.execute(
        "SELECT p.*, u.username, u.email FROM pedidos p JOIN usuarios u ON p.usuario_id = u.id WHERE p.id = ?",
        (pedido_id,),
    ).fetchone()

    if not pedido:
        flash("Pedido no encontrado.", "warning")
        return redirect(url_for("orders.lista"))

    items = db.execute(
        """SELECT pi.*, pr.nombre, pr.sku FROM pedido_items pi
           JOIN productos pr ON pi.producto_id = pr.id
           WHERE pi.pedido_id = ?""",
        (pedido_id,),
    ).fetchall()

    return render_template("orders/detalle.html", pedido=pedido, items=items)
