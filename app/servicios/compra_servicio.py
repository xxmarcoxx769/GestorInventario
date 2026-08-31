"""Lógica de compras. Flujo: crear (PENDIENTE) → recibir (genera ENTRADAS) → RECIBIDA.

Una compra pendiente no altera el stock; solo al recibirla se materializan las
entradas de inventario. También puede cancelarse mientras esté pendiente.
"""
from decimal import Decimal

from ..extensiones import db
from ..modelos import Compra, LineaCompra, Producto, Proveedor, EstadoCompra
from .errores import NoEncontrado, Conflicto, ErrorNegocio
from . import inventario_servicio


def listar_compras():
    return db.session.scalars(
        db.select(Compra).order_by(Compra.fecha.desc(), Compra.id.desc())
    ).all()


def obtener_compra(compra_id: int) -> Compra:
    compra = db.session.get(Compra, compra_id)
    if compra is None:
        raise NoEncontrado("La compra no existe.")
    return compra


def crear_compra(usuario_id: int, proveedor_id: int, lineas: list[dict]) -> Compra:
    """`lineas`: [{'producto_id', 'cantidad', 'coste_unitario'}, ...]. Queda PENDIENTE."""
    if db.session.get(Proveedor, proveedor_id) is None:
        raise NoEncontrado("El proveedor no existe.")
    if not lineas:
        raise ErrorNegocio("La compra debe incluir al menos un producto.")
    try:
        compra = Compra(
            proveedor_id=proveedor_id, usuario_id=usuario_id,
            estado=EstadoCompra.PENDIENTE, total=0,
        )
        db.session.add(compra)
        db.session.flush()

        total = Decimal("0")
        for linea in lineas:
            producto = db.session.get(Producto, linea["producto_id"])
            if producto is None:
                raise NoEncontrado(f"Producto id={linea['producto_id']} no existe.")
            cantidad = linea["cantidad"]
            coste = linea["coste_unitario"]
            if cantidad <= 0:
                raise ErrorNegocio("Las cantidades deben ser positivas.")
            if coste < 0:
                raise ErrorNegocio("El coste no puede ser negativo.")
            db.session.add(LineaCompra(
                compra_id=compra.id, producto_id=producto.id,
                cantidad=cantidad, coste_unitario=coste,
            ))
            total += Decimal(str(coste)) * cantidad

        compra.total = total
        db.session.commit()
        return compra
    except Exception:
        db.session.rollback()
        raise


def recibir_compra(compra_id: int, usuario_id: int) -> Compra:
    """Marca la compra como RECIBIDA y genera las entradas de inventario."""
    compra = obtener_compra(compra_id)
    if compra.estado != EstadoCompra.PENDIENTE:
        raise Conflicto("Solo se pueden recibir compras en estado PENDIENTE.")
    try:
        for linea in compra.lineas:
            inventario_servicio.registrar_entrada(
                linea.producto, linea.cantidad, usuario_id,
                motivo=f"Compra #{compra.id}", compra_id=compra.id,
            )
        compra.estado = EstadoCompra.RECIBIDA
        db.session.commit()
        return compra
    except Exception:
        db.session.rollback()
        raise


def cancelar_compra(compra_id: int) -> Compra:
    compra = obtener_compra(compra_id)
    if compra.estado != EstadoCompra.PENDIENTE:
        raise Conflicto("Solo se pueden cancelar compras en estado PENDIENTE.")
    compra.estado = EstadoCompra.CANCELADA
    db.session.commit()
    return compra
