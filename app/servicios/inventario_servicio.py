"""Lógica de inventario. Los movimientos son la fuente de verdad del stock.

`registrar_entrada` / `registrar_salida` son bloques de bajo nivel que NO hacen
commit: modifican `stock_actual` y encolan el movimiento para que el llamador
(ventas, compras) cierre la transacción. `ajustar_stock` sí es una operación
completa e independiente.
"""
from ..extensiones import db
from ..modelos import Producto, MovimientoInventario, TipoMovimiento
from .errores import NoEncontrado, ErrorNegocio


def listar_movimientos(producto_id=None, tipo=None, limite=300):
    consulta = db.select(MovimientoInventario).order_by(
        MovimientoInventario.fecha.desc(), MovimientoInventario.id.desc()
    )
    if producto_id:
        consulta = consulta.where(MovimientoInventario.producto_id == producto_id)
    if tipo:
        consulta = consulta.where(MovimientoInventario.tipo == tipo)
    return db.session.scalars(consulta.limit(limite)).all()


def _obtener_producto(producto_id: int) -> Producto:
    producto = db.session.get(Producto, producto_id)
    if producto is None:
        raise NoEncontrado("El producto no existe.")
    return producto


def registrar_entrada(producto: Producto, cantidad: int, usuario_id: int,
                      motivo: str, compra_id: int | None = None) -> MovimientoInventario:
    if cantidad <= 0:
        raise ErrorNegocio("La cantidad de entrada debe ser positiva.")
    producto.stock_actual += cantidad
    mov = MovimientoInventario(
        producto_id=producto.id, tipo=TipoMovimiento.ENTRADA, cantidad=cantidad,
        motivo=motivo, usuario_id=usuario_id, compra_id=compra_id,
    )
    db.session.add(mov)
    return mov


def registrar_salida(producto: Producto, cantidad: int, usuario_id: int,
                     motivo: str, venta_id: int | None = None) -> MovimientoInventario:
    if cantidad <= 0:
        raise ErrorNegocio("La cantidad de salida debe ser positiva.")
    if producto.stock_actual < cantidad:
        raise ErrorNegocio(
            f"Stock insuficiente de «{producto.nombre}»: hay {producto.stock_actual} "
            f"y se requieren {cantidad}."
        )
    producto.stock_actual -= cantidad
    mov = MovimientoInventario(
        producto_id=producto.id, tipo=TipoMovimiento.SALIDA, cantidad=cantidad,
        motivo=motivo, usuario_id=usuario_id, venta_id=venta_id,
    )
    db.session.add(mov)
    return mov


def ajustar_stock(producto_id: int, nuevo_stock: int, usuario_id: int,
                  motivo: str | None = None) -> MovimientoInventario:
    """Ajuste por recuento físico: fija el stock a `nuevo_stock` y registra el delta."""
    producto = _obtener_producto(producto_id)
    if nuevo_stock < 0:
        raise ErrorNegocio("El stock no puede ser negativo.")
    delta = nuevo_stock - producto.stock_actual
    if delta == 0:
        raise ErrorNegocio("El stock indicado coincide con el actual; no hay ajuste que registrar.")
    producto.stock_actual = nuevo_stock
    mov = MovimientoInventario(
        producto_id=producto.id, tipo=TipoMovimiento.AJUSTE, cantidad=delta,
        motivo=(motivo or "").strip() or "Ajuste manual", usuario_id=usuario_id,
    )
    db.session.add(mov)
    db.session.commit()
    return mov
