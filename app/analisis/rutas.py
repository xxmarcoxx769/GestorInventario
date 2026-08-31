"""Panel de análisis: métricas y gráficas generadas en el servidor con Matplotlib.

Las gráficas se construyen en Python y se inyectan como imágenes base64 en la
plantilla; no se usa JavaScript ni librerías de cliente.
"""
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request
from flask_login import login_required

from ..servicios import analisis_servicio as servicio
from . import graficas

analisis_bp = Blueprint("analisis", __name__, url_prefix="/analisis")


def _rango_fechas():
    """Lee desde/hasta (YYYY-MM-DD) del query; por defecto, últimos 90 días."""
    hoy = datetime.now()
    por_defecto_desde = (hoy - timedelta(days=90)).date()

    def _parse(nombre, defecto):
        valor = request.args.get(nombre)
        if valor:
            try:
                return datetime.strptime(valor, "%Y-%m-%d").date()
            except ValueError:
                pass
        return defecto

    desde_d = _parse("desde", por_defecto_desde)
    hasta_d = _parse("hasta", hoy.date())
    # datetime con hasta inclusivo (fin del día)
    desde = datetime.combine(desde_d, datetime.min.time())
    hasta = datetime.combine(hasta_d, datetime.max.time())
    return desde, hasta, desde_d, hasta_d


@analisis_bp.route("/")
@login_required
def panel():
    desde, hasta, desde_d, hasta_d = _rango_fechas()

    kpis = servicio.kpis(desde, hasta)
    vendidos = servicio.mas_vendidos(desde, hasta)
    rentables = servicio.mas_rentables(desde, hasta)
    poca_rotacion = servicio.menor_rotacion(desde, hasta)
    evolucion = servicio.evolucion_ventas(desde, hasta)
    agotamiento = servicio.dias_hasta_agotar()

    graf_vendidos = graficas.barras_horizontal(
        [n for n, _ in vendidos], [u for _, u in vendidos],
        "Productos más vendidos (unidades)", color=graficas.COLOR_PRIMARIO,
    )
    graf_rentables = graficas.barras_horizontal(
        [n for n, _ in rentables], [b for _, b in rentables],
        "Productos más rentables (beneficio €)", color=graficas.COLOR_EXITO, sufijo=" €",
    )
    graf_rotacion = graficas.barras_horizontal(
        [n for n, _ in poca_rotacion], [u for _, u in poca_rotacion],
        "Productos con menor rotación (unidades)", color=graficas.COLOR_AVISO,
    )
    graf_evolucion = graficas.linea_temporal(
        [d for d, _ in evolucion], [t for _, t in evolucion],
        "Evolución de ventas por día",
    )

    return render_template(
        "analisis/panel.html",
        kpis=kpis,
        agotamiento=agotamiento,
        desde=desde_d.isoformat(),
        hasta=hasta_d.isoformat(),
        graf_vendidos=graf_vendidos,
        graf_rentables=graf_rentables,
        graf_rotacion=graf_rotacion,
        graf_evolucion=graf_evolucion,
    )
