"""
run.py — Punto de entrada de SecureShop
Aplicación educativa para curso de Desarrollo Seguro — Secure Develop SpA
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
