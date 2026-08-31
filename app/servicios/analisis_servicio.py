"""Consultas analíticas: métricas y agregaciones para el panel de análisis."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func

from ..extensiones import db
from ..modelos import Producto, LineaVenta, Venta


# Expresión SQL del beneficio de una línea: (precio - coste) * cantidad
_BENEFICIO_LINEA = (LineaVenta.precio_unitario - LineaVenta.coste_unitario) * LineaVenta.cantidad
_INGRESO_LINEA = LineaVenta.precio_unitario * LineaVenta.cantidad
_COSTE_LINEA = LineaVenta.coste_unitario * LineaVenta.cantidad


def _join_ventas(consulta, desde, hasta):
    return (
        consulta.join(LineaVenta, LineaVenta.producto_id == Producto.id)
        .join(Venta, Venta.id == LineaVenta.venta_id)
        .where(Venta.fecha >= desde, Venta.fecha <= hasta)
    )


def kpis(desde: datetime, hasta: datetime) -> dict:
    """Ingresos, coste, beneficio y nº de ventas en el rango."""
    fila = db.session.execute(
        db.select(
            func.coalesce(func.sum(_INGRESO_LINEA), 0),
            func.coalesce(func.sum(_COSTE_LINEA), 0),
            func.coalesce(func.sum(LineaVenta.cantidad), 0),
        )
        .select_from(LineaVenta)
        .join(Venta, Venta.id == LineaVenta.venta_id)
        .where(Venta.fecha >= desde, Venta.fecha <= hasta)
    ).one()
    ingresos, coste, unidades = Decimal(fila[0]), Decimal(fila[1]), int(fila[2])
    num_ventas = db.session.scalar(
        db.select(func.count(Venta.id)).where(Venta.fecha >= desde, Venta.fecha <= hasta)
    )
    return {
        "ingresos": ingresos,
        "coste": coste,
        "beneficio": ingresos - coste,
        "unidades": unidades,
        "num_ventas": num_ventas or 0,
    }


def mas_vendidos(desde, hasta, limite=5):
    """[(nombre, unidades), ...] ordenado por unidades vendidas desc."""
    filas = db.session.execute(
        _join_ventas(
            db.select(Producto.nombre, func.sum(LineaVenta.cantidad).label("u")), desde, hasta
        )
        .group_by(Producto.id)
        .order_by(func.sum(LineaVenta.cantidad).desc())
        .limit(limite)
    ).all()
    return [(nombre, int(u)) for nombre, u in filas]


def mas_rentables(desde, hasta, limite=5):
    """[(nombre, beneficio), ...] ordenado por beneficio total desc."""
    filas = db.session.execute(
        _join_ventas(
            db.select(Producto.nombre, func.sum(_BENEFICIO_LINEA).label("b")), desde, hasta
        )
        .group_by(Producto.id)
        .order_by(func.sum(_BENEFICIO_LINEA).desc())
        .limit(limite)
    ).all()
    return [(nombre, Decimal(b)) for nombre, b in filas]


def menor_rotacion(desde, hasta, limite=5):
    """Productos con menos unidades vendidas en el periodo (incluye los de 0 ventas)."""
    vendidas = dict(
        db.session.execute(
            _join_ventas(
                db.select(Producto.id, func.sum(LineaVenta.cantidad)), desde, hasta
            ).group_by(Producto.id)
        ).all()
    )
    productos = db.session.scalars(db.select(Producto)).all()
    ranking = sorted(
        ((p, int(vendidas.get(p.id, 0))) for p in productos),
        key=lambda par: par[1],
    )
    return [(p.nombre, u) for p, u in ranking[:limite]]


def evolucion_ventas(desde, hasta):
    """[(dia 'YYYY-MM-DD', total), ...] por día dentro del rango."""
    dia = func.date(Venta.fecha)
    filas = db.session.execute(
        db.select(dia.label("dia"), func.coalesce(func.sum(Venta.total), 0))
        .where(Venta.fecha >= desde, Venta.fecha <= hasta)
        .group_by(dia)
        .order_by(dia)
    ).all()
    return [(str(d), Decimal(total)) for d, total in filas]


def dias_hasta_agotar(ventana_dias=30):
    """Estima días hasta agotar stock según el ritmo de ventas de los últimos N días.

    Devuelve filas ordenadas: primero los que se agotarán antes.
    """
    ahora = datetime.now(timezone.utc)
    desde = ahora - timedelta(days=ventana_dias)
    vendidas = dict(
        db.session.execute(
            db.select(LineaVenta.producto_id, func.sum(LineaVenta.cantidad))
            .join(Venta, Venta.id == LineaVenta.venta_id)
            .where(Venta.fecha >= desde)
            .group_by(LineaVenta.producto_id)
        ).all()
    )
    filas = []
    for p in db.session.scalars(db.select(Producto)).all():
        unidades = int(vendidas.get(p.id, 0))
        ritmo = unidades / ventana_dias if unidades else 0.0
        dias = (p.stock_actual / ritmo) if ritmo > 0 else None
        filas.append({
            "producto": p,
            "unidades_periodo": unidades,
            "ritmo_diario": ritmo,
            "dias_restantes": dias,
        })
    # Los que tienen fecha de agotamiento primero (asc); los de ritmo 0 al final.
    filas.sort(key=lambda f: (f["dias_restantes"] is None, f["dias_restantes"] or 0))
    return filas
