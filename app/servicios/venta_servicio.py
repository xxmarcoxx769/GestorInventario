"""Lógica de ventas. Cada línea congela precio y coste; cada venta genera SALIDAS."""
from decimal import Decimal

from ..extensiones import db
from ..modelos import Venta, LineaVenta, Producto
from .errores import NoEncontrado, ErrorNegocio
from . import inventario_servicio


def listar_ventas():
    return db.session.scalars(
        db.select(Venta).order_by(Venta.fecha.desc(), Venta.id.desc())
    ).all()


def obtener_venta(venta_id: int) -> Venta:
    venta = db.session.get(Venta, venta_id)
    if venta is None:
        raise NoEncontrado("La venta no existe.")
    return venta


def crear_venta(usuario_id: int, cliente: str | None, lineas: list[dict]) -> Venta:
    """`lineas`: [{'producto_id': int, 'cantidad': int}, ...]. Todo en una transacción."""
    if not lineas:
        raise ErrorNegocio("La venta debe incluir al menos un producto.")
    try:
        venta = Venta(usuario_id=usuario_id, cliente=(cliente or "").strip() or None, total=0)
        db.session.add(venta)
        db.session.flush()  # asignar venta.id para los movimientos

        total = Decimal("0")
        for linea in lineas:
            producto = db.session.get(Producto, linea["producto_id"])
            if producto is None:
                raise NoEncontrado(f"Producto id={linea['producto_id']} no existe.")
            cantidad = linea["cantidad"]
            if cantidad <= 0:
                raise ErrorNegocio("Las cantidades deben ser positivas.")

            db.session.add(LineaVenta(
                venta_id=venta.id, producto_id=producto.id, cantidad=cantidad,
                precio_unitario=producto.precio_venta,       # congelado
                coste_unitario=producto.coste_adquisicion,   # congelado
            ))
            inventario_servicio.registrar_salida(
                producto, cantidad, usuario_id, motivo=f"Venta #{venta.id}", venta_id=venta.id
            )
            total += producto.precio_venta * cantidad

        venta.total = total
        db.session.commit()
        return venta
    except Exception:
        db.session.rollback()
        raise
