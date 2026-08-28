"""Usuarios y roles del sistema."""
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from ..extensiones import db


class RolUsuario:
    """Roles disponibles (enumerado por conveniencia, almacenado como texto)."""

    ADMIN = "ADMIN"
    ALMACEN = "ALMACEN"
    FINANCIERO = "FINANCIERO"
    TODOS = (ADMIN, ALMACEN, FINANCIERO)


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default=RolUsuario.ALMACEN)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self) -> bool:  # requerido por Flask-Login
        return self.activo

    def __repr__(self) -> str:
        return f"<Usuario {self.email} ({self.rol})>"
