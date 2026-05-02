"""
services/audit_service.py — Servicio de Auditoría y Logging
Registro de eventos de seguridad y operacionales
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../../instance/secureshop.db")


def registrar_evento(nivel: str, usuario: str, ip: str, mensaje: str = "") -> None:
    """Registra un evento en la tabla system_logs."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO system_logs (nivel, mensaje, usuario, ip) VALUES (?, ?, ?, ?)",
            (nivel, mensaje, usuario, ip),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass  # No interrumpir el flujo principal si el log falla
