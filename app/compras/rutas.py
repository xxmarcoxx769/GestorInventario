"""Rutas de compras.

Permisos: ver = cualquier rol; crear/recibir/cancelar = ADMIN o ALMACEN.
Flujo: crear (PENDIENTE) → recibir (genera ENTRADAS y sube stock) → RECIBIDA.

El formulario de nueva compra gestiona sus líneas EN EL SERVIDOR (sin JavaScript).
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
    proveedor_id = ""
    lineas = [_fila_vacia()]

    if request.method == "POST" and form.validate_on_submit():
        proveedor_id = request.form.get("proveedor_id", "")
        lineas = _leer_filas(request)

        if request.form.get("quitar") is not None:
            _quitar_fila(lineas, request.form.get("quitar", type=int))
        elif request.form.get("accion") == "add":
            lineas.append(_fila_vacia())
        elif request.form.get("accion") == "guardar":
            try:
                if not proveedor_id:
                    raise ErrorNegocio("Selecciona un proveedor.")
                compra = servicio.crear_compra(current_user.id, int(proveedor_id), _lineas_validas(lineas))
                flash(f"Compra #{compra.id} creada (PENDIENTE) por {compra.total:.2f} €.", "success")
                return redirect(url_for("compras.detalle", compra_id=compra.id))
            except ErrorNegocio as e:
                flash(e.mensaje, "danger")

    return render_template("compras/formulario.html", form=form, productos=productos,
                           proveedores=proveedores, proveedor_id=proveedor_id, lineas=lineas)


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


@compras_bp.route("/<int:compra_id>/recibir", methods=["GET", "POST"])
@rol_requerido(*GESTION)
def recibir(compra_id):
    try:
        compra = servicio.obtener_compra(compra_id)
    except ErrorNegocio as e:
        flash(e.mensaje, "danger")
        return redirect(url_for("compras.lista"))

    if request.method == "POST":
        try:
            servicio.recibir_compra(compra_id, current_user.id)
            flash("Compra recibida: stock actualizado con las entradas.", "success")
        except ErrorNegocio as e:
            flash(e.mensaje, "danger")
        return redirect(url_for("compras.detalle", compra_id=compra_id))

    return render_template(
        "confirmar.html", form=FlaskForm(),
        titulo=f"Recibir compra #{compra.id}",
        mensaje="Al recibir la compra se generarán las entradas de inventario y "
                "aumentará el stock de los productos. ¿Continuar?",
        accion_url=url_for("compras.recibir", compra_id=compra_id),
        volver_url=url_for("compras.detalle", compra_id=compra_id),
        estilo="success", confirmar_texto="Sí, recibir",
    )


@compras_bp.route("/<int:compra_id>/cancelar", methods=["GET", "POST"])
@rol_requerido(*GESTION)
def cancelar(compra_id):
    try:
        compra = servicio.obtener_compra(compra_id)
    except ErrorNegocio as e:
        flash(e.mensaje, "danger")
        return redirect(url_for("compras.lista"))

    if request.method == "POST":
        try:
            servicio.cancelar_compra(compra_id)
            flash("Compra cancelada.", "info")
        except ErrorNegocio as e:
            flash(e.mensaje, "danger")
        return redirect(url_for("compras.detalle", compra_id=compra_id))

    return render_template(
        "confirmar.html", form=FlaskForm(),
        titulo=f"Cancelar compra #{compra.id}",
        mensaje="¿Seguro que quieres cancelar esta compra pendiente?",
        accion_url=url_for("compras.cancelar", compra_id=compra_id),
        volver_url=url_for("compras.detalle", compra_id=compra_id),
        confirmar_texto="Sí, cancelar",
    )


# --------------------------- helpers de líneas ---------------------------

def _fila_vacia() -> dict:
    return {"producto_id": "", "cantidad": "1", "coste_unitario": "0.00"}


def _leer_filas(req) -> list[dict]:
    ids = req.form.getlist("producto_id")
    cantidades = req.form.getlist("cantidad")
    costes = req.form.getlist("coste_unitario")
    filas = [{"producto_id": pid, "cantidad": cant, "coste_unitario": coste}
             for pid, cant, coste in zip(ids, cantidades, costes)]
    return filas or [_fila_vacia()]


def _quitar_fila(filas: list[dict], indice) -> None:
    if indice is not None and 0 <= indice < len(filas):
        filas.pop(indice)
    if not filas:
        filas.append(_fila_vacia())


def _lineas_validas(filas: list[dict]) -> list[dict]:
    lineas = []
    for fila in filas:
        if not fila["producto_id"]:
            continue
        try:
            cantidad = int(fila["cantidad"])
            coste = Decimal(fila["coste_unitario"] or "0")
        except (TypeError, ValueError, InvalidOperation):
            raise ErrorNegocio("Revisa las cantidades y costes introducidos.")
        lineas.append({
            "producto_id": int(fila["producto_id"]),
            "cantidad": cantidad,
            "coste_unitario": coste,
        })
    if not lineas:
        raise ErrorNegocio("Añade al menos una línea con producto, cantidad y coste.")
    return lineas
