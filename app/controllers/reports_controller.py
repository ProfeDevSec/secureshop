"""
controllers/reports_controller.py — Módulo de Reportes y Exportación
Generación de reportes operacionales y herramientas de diagnóstico
"""

import os
import subprocess
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, send_file
)
from ..models.database import get_db
from ..services.audit_service import registrar_evento

reports_bp = Blueprint("reports", __name__)


def _requiere_rol(*roles):
    if "user_id" not in session:
        return False
    return session.get("rol") in roles


@reports_bp.route("/")
def index():
    if not _requiere_rol("admin", "vendedor", "auditor"):
        flash("Acceso no autorizado.", "danger")
        return redirect(url_for("catalog.index"))
    return render_template("reports/index.html")


@reports_bp.route("/ventas")
def ventas():
    if not _requiere_rol("admin", "vendedor", "auditor"):
        flash("Acceso no autorizado.", "danger")
        return redirect(url_for("catalog.index"))

    db       = get_db()
    resumen  = db.execute(
        """SELECT u.username, COUNT(p.id) as total_pedidos,
                  SUM(p.total) as total_ventas
           FROM pedidos p JOIN usuarios u ON p.usuario_id = u.id
           GROUP BY u.username ORDER BY total_ventas DESC"""
    ).fetchall()

    detalle  = db.execute(
        """SELECT p.id, u.username, p.estado, p.total, p.created_at
           FROM pedidos p JOIN usuarios u ON p.usuario_id = u.id
           ORDER BY p.created_at DESC LIMIT 50"""
    ).fetchall()

    return render_template("reports/ventas.html", resumen=resumen, detalle=detalle)


@reports_bp.route("/diagnostico", methods=["GET", "POST"])
def diagnostico():
    """
    Herramienta de diagnóstico de conectividad de red.
    Permite verificar que los servidores externos estén alcanzables.
    """
    if not _requiere_rol("admin"):
        flash("Solo administradores pueden usar herramientas de diagnóstico.", "danger")
        return redirect(url_for("catalog.index"))

    resultado = None

    if request.method == "POST":
        host = request.form.get("host", "").strip()

        comando = f"ping -c 2 {host}"
        try:
            resultado = subprocess.check_output(
                comando,
                shell=True,           # shell=True es el vector
                stderr=subprocess.STDOUT,
                timeout=10,
            ).decode("utf-8", errors="replace")
        except subprocess.TimeoutExpired:
            resultado = "Tiempo de espera agotado."
        except subprocess.CalledProcessError as e:
            resultado = e.output.decode("utf-8", errors="replace")

        registrar_evento("DIAGNOSTICO_EJECUTADO", session["username"], request.remote_addr)

    return render_template("reports/diagnostico.html", resultado=resultado)


@reports_bp.route("/exportar")
def exportar():
    """Exporta logs del sistema en formato solicitado."""
    if not _requiere_rol("admin", "auditor"):
        flash("Acceso no autorizado.", "danger")
        return redirect(url_for("catalog.index"))

    db   = get_db()
    logs = db.execute(
        "SELECT * FROM system_logs ORDER BY created_at DESC LIMIT 200"
    ).fetchall()

    return render_template("reports/exportar.html", logs=logs)
