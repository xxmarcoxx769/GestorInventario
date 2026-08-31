"""Rutas de ventas.

Permisos: ver = cualquier rol; registrar ventas = ADMIN o FINANCIERO.
Cada venta descuenta stock (movimientos de SALIDA) en una única transacción.

El formulario de nueva venta gestiona sus líneas EN EL SERVIDOR (sin JavaScript):
los botones "Añadir/Quitar línea" reenvían el formulario y Python re-renderiza las
filas conservando lo introducido.
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
    form = FlaskForm()  # token CSRF
    productos = producto_servicio.listar_productos()
    cliente = ""
    lineas = [{"producto_id": "", "cantidad": "1"}]

    if request.method == "POST" and form.validate_on_submit():
        cliente = request.form.get("cliente", "")
        lineas = _leer_filas(request)

        if request.form.get("quitar") is not None:
            _quitar_fila(lineas, request.form.get("quitar", type=int))
        elif request.form.get("accion") == "add":
            lineas.append({"producto_id": "", "cantidad": "1"})
        elif request.form.get("accion") == "guardar":
            try:
                venta = servicio.crear_venta(current_user.id, cliente, _lineas_validas(lineas))
                flash(f"Venta #{venta.id} registrada por {venta.total:.2f} €.", "success")
                return redirect(url_for("ventas.detalle", venta_id=venta.id))
            except ErrorNegocio as e:
                flash(e.mensaje, "danger")

    return render_template("ventas/formulario.html", form=form, productos=productos,
                           cliente=cliente, lineas=lineas)


@ventas_bp.route("/<int:venta_id>")
@login_required
def detalle(venta_id):
    try:
        venta = servicio.obtener_venta(venta_id)
    except ErrorNegocio as e:
        flash(e.mensaje, "danger")
        return redirect(url_for("ventas.lista"))
    return render_template("ventas/detalle.html", venta=venta)


# --------------------------- helpers de líneas ---------------------------

def _leer_filas(req) -> list[dict]:
    """Lee las filas tal cual (conservando vacías) para poder re-renderizarlas."""
    ids = req.form.getlist("producto_id")
    cantidades = req.form.getlist("cantidad")
    filas = [{"producto_id": pid, "cantidad": cant}
             for pid, cant in zip(ids, cantidades)]
    return filas or [{"producto_id": "", "cantidad": "1"}]


def _quitar_fila(filas: list[dict], indice) -> None:
    if indice is not None and 0 <= indice < len(filas):
        filas.pop(indice)
    if not filas:
        filas.append({"producto_id": "", "cantidad": "1"})


def _lineas_validas(filas: list[dict]) -> list[dict]:
    lineas = []
    for fila in filas:
        if not fila["producto_id"]:
            continue
        try:
            cantidad = int(fila["cantidad"])
        except (TypeError, ValueError):
            raise ErrorNegocio("Las cantidades deben ser números enteros.")
        lineas.append({"producto_id": int(fila["producto_id"]), "cantidad": cantidad})
    if not lineas:
        raise ErrorNegocio("Añade al menos una línea con producto y cantidad.")
    return lineas
