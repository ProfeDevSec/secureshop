"""
controllers/auth_controller.py — Módulo de Autenticación
Gestión de sesiones de usuario para el portal SecureShop
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models.database import get_db
from ..services.audit_service import registrar_evento

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        import hashlib
        pwd_hash = hashlib.md5(password.encode()).hexdigest()

        db = get_db()
        query = (
            "SELECT * FROM usuarios WHERE username = '"
            + username
            + "' AND password = '"
            + pwd_hash
            + "' AND activo = 1"
        )

        try:
            usuario = db.execute(query).fetchone()
        except Exception as e:
            # [VULN] Exposición de detalles del error al usuario
            flash(f"Error de base de datos: {e}", "danger")
            return render_template("auth/login.html")

        if usuario:
            session["user_id"]   = usuario["id"]
            session["username"]  = usuario["username"]
            session["rol"]       = usuario["rol"]
            registrar_evento("LOGIN_OK", username, request.remote_addr)
            return redirect(url_for("catalog.index"))
        else:
            registrar_evento("LOGIN_FAIL", username, request.remote_addr)
            flash("Credenciales incorrectas.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    registrar_evento("LOGOUT", session.get("username", "?"), request.remote_addr)
    session.clear()
    return redirect(url_for("auth.login"))
