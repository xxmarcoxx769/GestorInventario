"""Lógica de negocio para productos.

El `stock_actual` no se edita directamente aquí: es un contador cuya fuente de
verdad son los movimientos de inventario. Al crear un producto se admite un stock
inicial opcional, que se materializa como un movimiento de tipo AJUSTE.
"""
from decimal import Decimal

from ..extensiones import db
from ..modelos import (
    Producto,
    Categoria,
    MovimientoInventario,
    TipoMovimiento,
    LineaVenta,
    LineaCompra,
)
from .errores import NoEncontrado, Conflicto


def listar_productos(categoria_id=None, buscar=None, solo_bajo_stock=False):
    consulta = db.select(Producto)
    if categoria_id:
        consulta = consulta.where(Producto.categoria_id == categoria_id)
    if buscar:
        patron = f"%{buscar.strip()}%"
        consulta = consulta.where(
            db.or_(Producto.nombre.ilike(patron), Producto.referencia.ilike(patron))
        )
    if solo_bajo_stock:
        consulta = consulta.where(Producto.stock_actual <= Producto.stock_minimo)
    consulta = consulta.order_by(Producto.nombre)
    return db.session.scalars(consulta).all()


def obtener_producto(producto_id: int) -> Producto:
    producto = db.session.get(Producto, producto_id)
    if producto is None:
        raise NoEncontrado("El producto no existe.")
    return producto


def _validar_referencia_unica(referencia: str, excluir_id: int | None = None):
    consulta = db.select(Producto).where(Producto.referencia == referencia)
    if excluir_id is not None:
        consulta = consulta.where(Producto.id != excluir_id)
    if db.session.scalar(consulta):
        raise Conflicto(f"Ya existe un producto con la referencia «{referencia}».")


def _validar_categoria(categoria_id: int):
    if db.session.get(Categoria, categoria_id) is None:
        raise NoEncontrado("La categoría seleccionada no existe.")


def crear_producto(datos: dict, usuario_id: int) -> Producto:
    referencia = datos["referencia"].strip()
    _validar_referencia_unica(referencia)
    _validar_categoria(datos["categoria_id"])

    producto = Producto(
        referencia=referencia,
        nombre=datos["nombre"].strip(),
        categoria_id=datos["categoria_id"],
        precio_venta=datos["precio_venta"],
        coste_adquisicion=datos["coste_adquisicion"],
        stock_minimo=datos.get("stock_minimo") or 0,
        activo=datos.get("activo", True),
        stock_actual=0,
    )
    db.session.add(producto)
    db.session.flush()  # asignar id antes del movimiento

    stock_inicial = datos.get("stock_inicial") or 0
    if stock_inicial > 0:
        producto.stock_actual = stock_inicial
        db.session.add(
            MovimientoInventario(
                producto_id=producto.id,
                tipo=TipoMovimiento.AJUSTE,
                cantidad=stock_inicial,
                motivo="Stock inicial",
                usuario_id=usuario_id,
            )
        )

    db.session.commit()
    return producto


def actualizar_producto(producto_id: int, datos: dict) -> Producto:
    producto = obtener_producto(producto_id)
    referencia = datos["referencia"].strip()
    _validar_referencia_unica(referencia, excluir_id=producto_id)
    _validar_categoria(datos["categoria_id"])

    producto.referencia = referencia
    producto.nombre = datos["nombre"].strip()
    producto.categoria_id = datos["categoria_id"]
    producto.precio_venta = datos["precio_venta"]
    producto.coste_adquisicion = datos["coste_adquisicion"]
    producto.stock_minimo = datos.get("stock_minimo") or 0
    producto.activo = datos.get("activo", True)
    # stock_actual NO se toca aquí: cambia solo vía movimientos de inventario.

    db.session.commit()
    return producto


def _producto_referenciado(producto_id: int) -> bool:
    for modelo in (LineaVenta, LineaCompra, MovimientoInventario):
        if db.session.scalar(
            db.select(modelo.id).where(modelo.producto_id == producto_id).limit(1)
        ):
            return True
    return False


def eliminar_producto(producto_id: int) -> None:
    producto = obtener_producto(producto_id)
    if _producto_referenciado(producto_id):
        raise Conflicto(
            "No se puede eliminar: el producto tiene ventas, compras o movimientos "
            "asociados. Desactívalo en su lugar."
        )
    db.session.delete(producto)  # elimina en cascada sus suministros (producto_proveedor)
    db.session.commit()
