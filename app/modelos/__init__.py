"""Registro central de modelos y el user_loader de Flask-Login."""
from ..extensiones import db, login_manager

from .usuario import Usuario, RolUsuario
from .catalogo import Categoria, Producto
from .proveedor import Proveedor, ProductoProveedor
from .venta import Venta, LineaVenta
from .compra import Compra, LineaCompra, EstadoCompra
from .movimiento import MovimientoInventario, TipoMovimiento

__all__ = [
    "db",
    "Usuario",
    "RolUsuario",
    "Categoria",
    "Producto",
    "Proveedor",
    "ProductoProveedor",
    "Venta",
    "LineaVenta",
    "Compra",
    "LineaCompra",
    "EstadoCompra",
    "MovimientoInventario",
    "TipoMovimiento",
]


@login_manager.user_loader
def cargar_usuario(user_id: str):
    return db.session.get(Usuario, int(user_id))
