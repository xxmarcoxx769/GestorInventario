"""Ventas y sus líneas de detalle."""
from datetime import datetime, timezone

from ..extensiones import db


class Venta(db.Model):
    __tablename__ = "ventas"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    cliente = db.Column(db.String(150))  # texto opcional, no entidad CRM
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    usuario = db.relationship("Usuario")
    lineas = db.relationship(
        "LineaVenta", back_populates="venta", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Venta #{self.id} total={self.total}>"


class LineaVenta(db.Model):
    __tablename__ = "lineas_venta"

    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey("ventas.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    # Precio y coste congelados en el momento de la venta (analítica histórica correcta)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    coste_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    venta = db.relationship("Venta", back_populates="lineas")
    producto = db.relationship("Producto")

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    @property
    def beneficio(self):
        return self.cantidad * (self.precio_unitario - self.coste_unitario)
