"""Rutas de compras.

Permisos: ver = cualquier rol; crear/recibir/cancelar = ADMIN o ALMACEN.
Flujo: crear (PENDIENTE) → recibir (genera ENTRADAS y sube stock) → RECIBIDA.
"""
from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm

from ..modelos import RolUsuario
from ..auth.decoradores import rol_requerido
from ..servicios import compra_servicio as servicio
from ..servicios import producto_servicio, proveedor_servicio
from ..servicios.errores import ErrorNegocio

compras_bp = Blueprint("compras", __name__, url_prefix="/compras")
GESTION = (RolUsuario.ADMIN, RolUsuario.ALMACEN)


@compras_bp.route("/")
@login_required
def lista():
    return render_template(
        "compras/lista.html",
        compras=servicio.listar_compras(),
        puede_gestionar=current_user.rol in GESTION,
    )


@compras_bp.route("/nueva", methods=["GET", "POST"])
@rol_requerido(*GESTION)
def nueva():
    form = FlaskForm()
    productos = producto_servicio.listar_productos()
    proveedores = proveedor_servicio.listar_proveedores()

    if request.method == "POST" and form.validate_on_submit():
        try:
            proveedor_id = request.form.get("proveedor_id", type=int)
            if not proveedor_id:
                raise ErrorNegocio("Selecciona un proveedor.")
            lineas = _parsear_lineas(request)
            compra = servicio.crear_compra(current_user.id, proveedor_id, lineas)
            flash(f"Compra #{compra.id} creada (PENDIENTE) por {compra.total:.2f} €.", "success")
            return redirect(url_for("compras.detalle", compra_id=compra.id))
        except (ErrorNegocio, ValueError, InvalidOperation) as e:
            mensaje = e.mensaje if isinstance(e, ErrorNegocio) else "Revisa las cantidades y costes."
            flash(mensaje, "danger")

    return render_template(
        "compras/formulario.html", form=form, productos=productos, proveedores=proveedores
    )


@compras_bp.route("/<int:compra_id>")
@login_required
def detalle(compra_id):
    try:
        compra = servicio.obtener_compra(compra_id)
    except ErrorNegocio as e:
        flash(e.mensaje, "danger")
        return redirect(url_for("compras.lista"))
    return render_template(
        "compras/detalle.html", compra=compra, puede_gestionar=current_user.rol in GESTION
    )


@compras_bp.route("/<int:compra_id>/recibir", methods=["POST"])
@rol_requerido(*GESTION)
def recibir(compra_id):
    try:
        servicio.recibir_compra(compra_id, current_user.id)
        flash("Compra recibida: stock actualizado con las entradas.", "success")
    except ErrorNegocio as e:
        flash(e.mensaje, "danger")
    return redirect(url_for("compras.detalle", compra_id=compra_id))


@compras_bp.route("/<int:compra_id>/cancelar", methods=["POST"])
@rol_requerido(*GESTION)
def cancelar(compra_id):
    try:
        servicio.cancelar_compra(compra_id)
        flash("Compra cancelada.", "info")
    except ErrorNegocio as e:
        flash(e.mensaje, "danger")
    return redirect(url_for("compras.detalle", compra_id=compra_id))


def _parsear_lineas(req) -> list[dict]:
    ids = req.form.getlist("producto_id")
    cantidades = req.form.getlist("cantidad")
    costes = req.form.getlist("coste_unitario")
    lineas = []
    for pid, cant, coste in zip(ids, cantidades, costes):
        if not pid:
            continue
        lineas.append({
            "producto_id": int(pid),
            "cantidad": int(cant or 0),
            "coste_unitario": Decimal(coste or "0"),
        })
    if not lineas:
        raise ErrorNegocio("Añade al menos una línea con producto, cantidad y coste.")
    return lineas
