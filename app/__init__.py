"""Application factory."""
import os

from flask import Flask

from .config import Config, INSTANCE_DIR
from .extensiones import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Asegurar la carpeta `instance/` donde vive el fichero SQLite
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    # Extensiones
    db.init_app(app)
    login_manager.init_app(app)

    # Modelos (registra las tablas y el user_loader)
    from . import modelos  # noqa: F401

    # Blueprints
    from .auth.rutas import auth_bp
    from .main.rutas import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Comandos de consola
    from .cli import registrar_comandos

    registrar_comandos(app)

    return app
