"""Rutas de ventas.

Permisos: ver = cualquier rol; registrar ventas = ADMIN o FINANCIERO.
Cada venta descuenta stock (movimientos de SALIDA) en una única transacción.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm

from ..modelos import RolUsuario
from ..auth.decoradores import rol_requerido
from ..servicios import venta_servicio as servicio
from ..servicios import producto_servicio
from ..servicios.errores import ErrorNegocio

ventas_bp = Blueprint("ventas", __name__, url_prefix="/ventas")
GESTION = (RolUsuario.ADMIN, RolUsuario.FINANCIERO)


@ventas_bp.route("/")
@login_required
def lista():
    return render_template(
        "ventas/lista.html",
        ventas=servicio.listar_ventas(),
        puede_gestionar=current_user.rol in GESTION,
    )


@ventas_bp.route("/nueva", methods=["GET", "POST"])
@rol_requerido(*GESTION)
def nueva():
    form = FlaskForm()  # solo para el token CSRF
    productos = producto_servicio.listar_productos()

    if request.method == "POST" and form.validate_on_submit():
        try:
            lineas = _parsear_lineas(request)
            venta = servicio.crear_venta(current_user.id, request.form.get("cliente"), lineas)
            flash(f"Venta #{venta.id} registrada por {venta.total:.2f} €.", "success")
            return redirect(url_for("ventas.detalle", venta_id=venta.id))
        except (ErrorNegocio, ValueError) as e:
            mensaje = e.mensaje if isinstance(e, ErrorNegocio) else "Revisa las cantidades introducidas."
            flash(mensaje, "danger")

    return render_template("ventas/formulario.html", form=form, productos=productos)


@ventas_bp.route("/<int:venta_id>")
@login_required
def detalle(venta_id):
    try:
        venta = servicio.obtener_venta(venta_id)
    except ErrorNegocio as e:
        flash(e.mensaje, "danger")
        return redirect(url_for("ventas.lista"))
    return render_template("ventas/detalle.html", venta=venta)


def _parsear_lineas(req) -> list[dict]:
    """Lee las columnas repetidas producto_id[] y cantidad[] del formulario."""
    ids = req.form.getlist("producto_id")
    cantidades = req.form.getlist("cantidad")
    lineas = []
    for pid, cant in zip(ids, cantidades):
        if not pid:
            continue
        lineas.append({"producto_id": int(pid), "cantidad": int(cant or 0)})
    if not lineas:
        raise ErrorNegocio("Añade al menos una línea con producto y cantidad.")
    return lineas
