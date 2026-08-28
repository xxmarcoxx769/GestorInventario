"""Compras a proveedores y sus líneas de detalle."""
from datetime import datetime, timezone

from ..extensiones import db


class EstadoCompra:
    PENDIENTE = "PENDIENTE"
    RECIBIDA = "RECIBIDA"
    CANCELADA = "CANCELADA"
    TODOS = (PENDIENTE, RECIBIDA, CANCELADA)


class Compra(db.Model):
    __tablename__ = "compras"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default=EstadoCompra.PENDIENTE)
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    proveedor = db.relationship("Proveedor", back_populates="compras")
    usuario = db.relationship("Usuario")
    lineas = db.relationship(
        "LineaCompra", back_populates="compra", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Compra #{self.id} {self.estado}>"


class LineaCompra(db.Model):
    __tablename__ = "lineas_compra"

    id = db.Column(db.Integer, primary_key=True)
    compra_id = db.Column(db.Integer, db.ForeignKey("compras.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    coste_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    compra = db.relationship("Compra", back_populates="lineas")
    producto = db.relationship("Producto")

    @property
    def subtotal(self):
        return self.cantidad * self.coste_unitario
