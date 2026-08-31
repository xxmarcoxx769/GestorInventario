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
    from .productos.rutas import productos_bp, categorias_bp
    from .proveedores.rutas import proveedores_bp
    from .inventario.rutas import inventario_bp
    from .ventas.rutas import ventas_bp
    from .compras.rutas import compras_bp
    from .analisis.rutas import analisis_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(analisis_bp)

    # Manejadores de error
    from flask import render_template

    @app.errorhandler(403)
    def acceso_denegado(_error):
        return render_template("errores/403.html"), 403

    # Comandos de consola
    from .cli import registrar_comandos

    registrar_comandos(app)

    return app
