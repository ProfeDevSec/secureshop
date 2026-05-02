"""
SecureShop - Portal de Gestión Comercial
Aplicación educativa para curso de Desarrollo Seguro
"""

from flask import Flask
from .models.database import init_db


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = "dev-secret-key-2024"  # [VULN-NOTE] Hardcoded, débil

    # Registrar blueprints (módulos de negocio)
    from .controllers.auth_controller import auth_bp
    from .controllers.catalog_controller import catalog_bp
    from .controllers.orders_controller import orders_bp
    from .controllers.reports_controller import reports_bp
    from .controllers.admin_controller import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp, url_prefix="/catalogo")
    app.register_blueprint(orders_bp, url_prefix="/pedidos")
    app.register_blueprint(reports_bp, url_prefix="/reportes")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Inicializar base de datos
    with app.app_context():
        init_db()

    return app
