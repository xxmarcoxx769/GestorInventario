# Gestor de Inventario

Aplicación web para una empresa de suministros tecnológicos: gestiona productos,
proveedores, ventas, compras e inventario, e incorpora métricas y análisis de negocio.
Proyecto Final de Python (Tokio School) — **Propuesta A**.

## Stack tecnológico

- **Python 3.13** + **Flask** (aplicación web renderizada en servidor con Jinja2)
- **SQLite 3** como base de datos, mediante el ORM **SQLAlchemy**
- **Flask-Login** para autenticación por sesión y control de roles
- **Flask-WTF / WTForms** para formularios y protección CSRF
- **Bootstrap 5** para la interfaz

## Requisitos previos

- Python 3.13 (o 3.11+). Comprueba tu versión con `python --version`.

## Instalación desde cero

En Windows (PowerShell), desde la carpeta del proyecto:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
flask --app run init-db
flask --app run seed
flask --app run run
```

En Linux/macOS sustituye `.venv\Scripts\activate` por `source .venv/bin/activate`.

La aplicación quedará disponible en http://localhost:5000

> `init-db` crea las tablas y `seed` carga datos de ejemplo. La base de datos se
> genera en `instance/gestor.sqlite` (no se versiona).

## Usuarios de ejemplo

Tras ejecutar `seed` (contraseña común: **Demo1234**):

| Email | Rol |
|---|---|
| admin@gestor.com | ADMIN |
| almacen@gestor.com | ALMACEN |
| finanzas@gestor.com | FINANCIERO |

Para crear tu propio administrador de forma interactiva:

```powershell
flask --app run crear-admin
```

## Estructura del proyecto

```
GestorInventario/
├─ run.py                 # punto de entrada
├─ requirements.txt       # dependencias con versiones ancladas
├─ docs/modelo-datos.md   # diagrama ER y diccionario de datos
└─ app/
   ├─ __init__.py         # application factory
   ├─ config.py           # configuración (ruta SQLite, secret key)
   ├─ extensiones.py      # db, login_manager, PRAGMA foreign_keys
   ├─ cli.py              # comandos init-db / crear-admin / seed
   ├─ modelos/            # entidades SQLAlchemy (10 tablas)
   ├─ auth/               # login, logout y decorador de roles
   ├─ main/               # panel de control
   ├─ templates/          # plantillas Jinja2
   └─ static/             # recursos estáticos
```

## Modelo de datos

El esquema (10 tablas) y el diagrama entidad-relación están documentados en
[docs/modelo-datos.md](docs/modelo-datos.md).

## Estado

Andamiaje inicial funcional: autenticación con roles, base de datos, datos de
ejemplo y panel de control. Módulos previstos: productos, proveedores, ventas,
compras, inventario y análisis/métricas.
