"""Proveedores y la relación N:M producto-proveedor (suministros)."""
from ..extensiones import db


class Proveedor(db.Model):
    __tablename__ = "proveedores"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    cif = db.Column(db.String(20), unique=True, nullable=False, index=True)
    contacto = db.Column(db.String(120))
    email = db.Column(db.String(120))
    telefono = db.Column(db.String(30))
    condiciones_pago = db.Column(db.String(120))
    activo = db.Column(db.Boolean, nullable=False, default=True)

    productos = db.relationship(
        "ProductoProveedor", back_populates="proveedor", cascade="all, delete-orphan"
    )
    compras = db.relationship("Compra", back_populates="proveedor")

    def __repr__(self) -> str:
        return f"<Proveedor {self.nombre} ({self.cif})>"


class ProductoProveedor(db.Model):
    """Tabla puente M:N: qué proveedor suministra qué producto y a qué precio."""

    __tablename__ = "producto_proveedor"
    __table_args__ = (
        db.UniqueConstraint("producto_id", "proveedor_id", name="uq_producto_proveedor"),
    )

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"), nullable=False)
    precio_proveedor = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    plazo_entrega_dias = db.Column(db.Integer)
    preferente = db.Column(db.Boolean, nullable=False, default=False)

    producto = db.relationship("Producto", back_populates="proveedores")
    proveedor = db.relationship("Proveedor", back_populates="productos")

    def __repr__(self) -> str:
        return f"<ProductoProveedor p{self.producto_id}-prov{self.proveedor_id}>"
