"""Catálogo: categorías y productos."""
from datetime import datetime, timezone
from decimal import Decimal

from ..extensiones import db


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))

    productos = db.relationship("Producto", back_populates="categoria")

    def __repr__(self) -> str:
        return f"<Categoria {self.nombre}>"


class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    referencia = db.Column(db.String(40), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(150), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)
    precio_venta = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    coste_adquisicion = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    stock_actual = db.Column(db.Integer, nullable=False, default=0)
    stock_minimo = db.Column(db.Integer, nullable=False, default=0)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    creado = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    categoria = db.relationship("Categoria", back_populates="productos")
    proveedores = db.relationship(
        "ProductoProveedor", back_populates="producto", cascade="all, delete-orphan"
    )
    movimientos = db.relationship("MovimientoInventario", back_populates="producto")

    @property
    def margen(self) -> Decimal:
        """Margen de beneficio unitario = precio de venta - coste de adquisición."""
        precio = self.precio_venta or Decimal("0")
        coste = self.coste_adquisicion or Decimal("0")
        return Decimal(precio) - Decimal(coste)

    @property
    def bajo_stock(self) -> bool:
        return self.stock_actual <= self.stock_minimo

    def __repr__(self) -> str:
        return f"<Producto {self.referencia} - {self.nombre}>"
