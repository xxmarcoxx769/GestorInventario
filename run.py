"""Punto de entrada de la aplicación.

Uso:
    flask --app run init-db     # crea las tablas
    flask --app run seed        # carga datos de ejemplo
    flask --app run run         # arranca el servidor de desarrollo
    python run.py               # equivalente para arrancar el servidor
"""
from dotenv import load_dotenv

load_dotenv()

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
