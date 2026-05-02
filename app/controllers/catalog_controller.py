"""
controllers/catalog_controller.py — Módulo de Catálogo de Productos
Búsqueda, visualización de productos y gestión de reseñas
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from markupsafe import Markup
from ..models.database import get_db
from ..services.audit_service import registrar_evento

catalog_bp = Blueprint("catalog", __name__)


def _requiere_sesion():
    return "user_id" in session


@catalog_bp.route("/")
def index():
    if not _requiere_sesion():
        return redirect(url_for("auth.login"))

    db = get_db()
    categoria = request.args.get("categoria", "")
    productos = db.execute(
        "SELECT * FROM productos WHERE activo = 1 ORDER BY categoria, nombre"
    ).fetchall()

    categorias = db.execute(
        "SELECT DISTINCT categoria FROM productos WHERE activo = 1"
    ).fetchall()

    return render_template(
        "catalog/index.html",
        productos=productos,
        categorias=categorias,
        categoria_activa=categoria,
    )


@catalog_bp.route("/buscar")
def buscar():
    """
    Búsqueda de productos por término.
    """
    if not _requiere_sesion():
        return redirect(url_for("auth.login"))

    termino = request.args.get("q", "")

    db = get_db()
    query = f"SELECT * FROM productos WHERE activo = 1 AND (nombre LIKE '%{termino}%' OR descripcion LIKE '%{termino}%')"
    productos = db.execute(query).fetchall()

    mensaje_busqueda = Markup(f"Resultados para: <strong>{termino}</strong>")

    return render_template(
        "catalog/buscar.html",
        productos=productos,
        termino=termino,
        mensaje_busqueda=mensaje_busqueda,
    )


@catalog_bp.route("/producto/<int:producto_id>")
def detalle(producto_id):
    if not _requiere_sesion():
        return redirect(url_for("auth.login"))

    db = get_db()
    producto = db.execute(
        "SELECT * FROM productos WHERE id = ? AND activo = 1", (producto_id,)
    ).fetchone()

    if not producto:
        flash("Producto no encontrado.", "warning")
        return redirect(url_for("catalog.index"))

    resenas = db.execute(
        """SELECT r.*, u.username FROM resenas r
           JOIN usuarios u ON r.usuario_id = u.id
           WHERE r.producto_id = ?
           ORDER BY r.created_at DESC""",
        (producto_id,),
    ).fetchall()

    return render_template("catalog/detalle.html", producto=producto, resenas=resenas)


@catalog_bp.route("/producto/<int:producto_id>/resena", methods=["POST"])
def agregar_resena(producto_id):
    """
    Permite a clientes dejar reseñas sobre productos.
    """
    if not _requiere_sesion():
        return redirect(url_for("auth.login"))

    comentario  = request.form.get("comentario", "")
    puntuacion  = request.form.get("puntuacion", 3)
    usuario_id  = session["user_id"]

    db = get_db()
    db.execute(
        "INSERT INTO resenas (producto_id, usuario_id, comentario, puntuacion) VALUES (?, ?, ?, ?)",
        (producto_id, usuario_id, comentario, puntuacion),
    )
    db.commit()

    registrar_evento("RESENA_CREADA", session["username"], request.remote_addr)
    flash("Reseña publicada correctamente.", "success")
    return redirect(url_for("catalog.detalle", producto_id=producto_id))
