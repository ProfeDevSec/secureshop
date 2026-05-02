# SecureShop — Aplicación Web Vulnerable (Educativa)

> **Curso de Desarrollo Seguro **

Portal comercial ficticio con vulnerabilidades **deliberadas** para práctica de
identificación, explotación y remediación. **Solo para entornos de laboratorio.**

---

## Estructura del proyecto

```
secureshop/
├── run.py                          # Punto de entrada
├── requirements.txt
├── instance/
│   └── secureshop.db               # BD SQLite (se genera automáticamente)
├── docs/
│   └── VULNERABILIDADES.md         # ← Guía completa de vulnerabilidades
└── app/
    ├── __init__.py                  # App factory
    ├── controllers/
    │   ├── auth_controller.py       # Login/logout  
    │   ├── catalog_controller.py    # Catálogo/búsqueda 
    │   ├── orders_controller.py     # Pedidos       
    │   ├── reports_controller.py    # Reportes      
    │   └── admin_controller.py      # Administración 
    ├── models/
    │   └── database.py              # SQLite + seed
    ├── services/
    │   └── audit_service.py         # Registro de eventos
    └── templates/                   # Jinja2 templates
```

---

## Instalación y ejecución

```bash
# 1. Clonar / descomprimir el proyecto
cd secureshop

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar (la BD se crea automáticamente en el primer inicio)
python run.py
```

La aplicación estará disponible en: **http://localhost:5000**

---

## Credenciales de laboratorio

| Usuario    | Contraseña     | Rol       | Acceso                          |
|------------|----------------|-----------|---------------------------------|
| `admin`    | `Admin2024!`   | admin     | Todo   |
| `jperez`   | `Comercial#99` | vendedor  | Catálogo, pedidos, reportes     |
| `cliente1` | `pass123`      | cliente   | Catálogo y sus propios pedidos  |
| `auditor`  | `Audit0r!`     | auditor   | Reportes y logs                 |

---

## Vulnerabilidades incluidas

| ID            | Categoría               | Ubicación en código |
|---------------|-------------------------|---------------------|
| VULN-SQLI-01  | SQL Injection           |                     |
| VULN-SQLI-02  | SQL Injection (UNION)   |                     |
| VULN-XSS-01   | XSS Reflejado           |                     |
| VULN-XSS-02   | XSS Almacenado          |                     |
| VULN-RCE-01   | Command Injection       |                     |
| VULN-DESER-01 | Insecure Deserialization|                     |
| VULN-IDOR-01  | IDOR                    |                     |
| VULN-INFO     | Info Disclosure         |                     |

---

## Metodología de aprendizaje sugerida

1. **Exploración**: Navegar la aplicación como usuario legítimo, entender los flujos.
2. **Análisis de código**: Revisar los controladores buscando patrones inseguros.
3. **Explotación**: Usar los payloads del documento de vulnerabilidades.
4. **Remediación**: Aplicar los fixes indicados y verificar que el exploit ya no funciona.
5. **Verificación**: Usar herramientas (sqlmap, Burp Suite, OWASP ZAP) para confirmar.

---

*Desarrollado para uso educativo interno · 2026*
