"""Movimientos de inventario: la fuente de verdad del stock."""
from datetime import datetime, timezone

from ..extensiones import db


class TipoMovimiento:
    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"
    AJUSTE = "AJUSTE"
    TODOS = (ENTRADA, SALIDA, AJUSTE)


class MovimientoInventario(db.Model):
    __tablename__ = "movimientos_inventario"

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)  # positiva; el signo lo da `tipo`
    motivo = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    # Trazabilidad opcional al documento que originó el movimiento
    venta_id = db.Column(db.Integer, db.ForeignKey("ventas.id"))
    compra_id = db.Column(db.Integer, db.ForeignKey("compras.id"))

    producto = db.relationship("Producto", back_populates="movimientos")
    usuario = db.relationship("Usuario")
    venta = db.relationship("Venta")
    compra = db.relationship("Compra")

    def __repr__(self) -> str:
        return f"<Movimiento {self.tipo} {self.cantidad} p{self.producto_id}>"
