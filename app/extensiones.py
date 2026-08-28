"""Instancias de extensiones compartidas por la aplicación."""
import sqlite3

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Inicia sesión para acceder a esta página."
login_manager.login_message_category = "warning"


@event.listens_for(Engine, "connect")
def _activar_foreign_keys(dbapi_connection, connection_record):
    """SQLite desactiva las claves foráneas por defecto: las activamos por conexión."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
