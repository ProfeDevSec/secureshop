"""
controllers/admin_controller.py — Panel de Administración
Gestión de usuarios, productos y configuración del sistema
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models.database import get_db
from ..services.audit_service import registrar_evento

admin_bp = Blueprint("admin", __name__)


def _solo_admin():
    return session.get("rol") == "admin"


@admin_bp.route("/")
def index():
    if not _solo_admin():
        flash("Panel restringido a administradores.", "danger")
        return redirect(url_for("catalog.index"))

    db = get_db()
    stats = {
        "usuarios":  db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0],
        "productos":  db.execute("SELECT COUNT(*) FROM productos WHERE activo=1").fetchone()[0],
        "pedidos":   db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0],
        "resenas":   db.execute("SELECT COUNT(*) FROM resenas").fetchone()[0],
    }
    return render_template("admin/index.html", stats=stats)


@admin_bp.route("/usuarios")
def usuarios():
    if not _solo_admin():
        flash("Acceso denegado.", "danger")
        return redirect(url_for("catalog.index"))

    db      = get_db()
    usuarios = db.execute("SELECT * FROM usuarios ORDER BY id").fetchall()
    return render_template("admin/usuarios.html", usuarios=usuarios)


@admin_bp.route("/usuarios/<int:uid>/toggle", methods=["POST"])
def toggle_usuario(uid):
    if not _solo_admin():
        flash("Acceso denegado.", "danger")
        return redirect(url_for("catalog.index"))

    db      = get_db()
    usuario = db.execute("SELECT * FROM usuarios WHERE id = ?", (uid,)).fetchone()
    if usuario:
        nuevo_estado = 0 if usuario["activo"] else 1
        db.execute("UPDATE usuarios SET activo = ? WHERE id = ?", (nuevo_estado, uid))
        db.commit()
        registrar_evento("USUARIO_TOGGLE", session["username"], request.remote_addr)
        flash(f"Usuario {usuario['username']} actualizado.", "success")

    return redirect(url_for("admin.usuarios"))
