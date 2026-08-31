"""Rutas de proveedores, suministros y comparativa de precios.

Permisos: ver = cualquier rol autenticado; crear/editar/eliminar = ADMIN o ALMACEN.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm

from ..modelos import RolUsuario
from ..auth.decoradores import rol_requerido
from ..servicios import proveedor_servicio as servicio
from ..servicios import producto_servicio
from ..servicios.errores import ErrorNegocio
from .formularios import ProveedorForm, SuministroForm

proveedores_bp = Blueprint("proveedores", __name__, url_prefix="/proveedores")

GESTION = (RolUsuario.ADMIN, RolUsuario.ALMACEN)


# --------------------------- PROVEEDORES ---------------------------

@proveedores_bp.route("/")
@login_required
def lista():
    buscar = request.args.get("buscar", type=str)
    proveedores = servicio.listar_proveedores(buscar=buscar)
    return render_template(
        "proveedores/lista.html",
        proveedores=proveedores,
        buscar=buscar or "",
        puede_gestionar=current_user.rol in GESTION,
    )


@proveedores_bp.route("/nuevo", methods=["GET", "POST"])
@rol_requerido(*GESTION)
def nuevo():
    form = ProveedorForm()
    if form.validate_on_submit():
        try:
            p = servicio.crear_proveedor(_datos_proveedor(form))
            flash(f"Proveedor «{p.nombre}» creado.", "success")
            return redirect(url_for("proveedores.detalle", proveedor_id=p.id))
        except ErrorNegocio as e:
            flash(e.mensaje, "danger")
    return render_template("proveedores/formulario.html", form=form, modo="crear")


@proveedores_bp.route("/<int:proveedor_id>/editar", methods=["GET", "POST"])
@rol_requerido(*GESTION)
def editar(proveedor_id):
    try:
        proveedor = servicio.obtener_proveedor(proveedor_id)
    except ErrorNegocio as e:
        flash(e.mensaje, "danger")
        return redirect(url_for("proveedores.lista"))

    form = ProveedorForm(obj=proveedor)
    if form.validate_on_submit():
        try:
            servicio.actualizar_proveedor(proveedor_id, _datos_proveedor(form))
            flash("Proveedor actualizado.", "success")
            return redirect(url_for("proveedores.detalle", proveedor_id=proveedor_id))
        except ErrorNegocio as e:
            flash(e.mensaje, "danger")
    return render_template("proveedores/formulario.html", form=form, modo="editar")


@proveedores_bp.route("/<int:proveedor_id>/eliminar", methods=["GET", "POST"])
@rol_requerido(*GESTION)
def eliminar(proveedor_id):
    try:
        proveedor = servicio.obtener_proveedor(proveedor_id)
    except ErrorNegocio as e:
        flash(e.mensaje, "danger")
        return redirect(url_for("proveedores.lista"))

    if request.method == "POST":
        try:
            servicio.eliminar_proveedor(proveedor_id)
            flash("Proveedor eliminado.", "success")
        except ErrorNegocio as e:
            flash(e.mensaje, "danger")
        return redirect(url_for("proveedores.lista"))

    return render_template(
        "confirmar.html", form=FlaskForm(),
        titulo="Eliminar proveedor",
        mensaje=f"¿Seguro que quieres eliminar «{proveedor.nombre}»? Se eliminarán también sus suministros.",
        accion_url=url_for("proveedores.eliminar", proveedor_id=proveedor_id),
        volver_url=url_for("proveedores.lista"), confirmar_texto="Sí, eliminar",
    )


@proveedores_bp.route("/<int:proveedor_id>")
@login_required
def detalle(proveedor_id):
    try:
        proveedor = servicio.obtener_proveedor(proveedor_id)
    except ErrorNegocio as e:
        flash(e.mensaje, "danger")
        return redirect(url_for("proveedores.lista"))
    suministros = servicio.listar_suministros(proveedor_id)
    return render_template(
        "proveedores/detalle.html",
        proveedor=proveedor,
        suministros=suministros,
        puede_gestionar=current_user.rol in GESTION,
    )


def _datos_proveedor(form) -> dict:
    return {
        "nombre": form.nombre.data,
        "cif": form.cif.data,
        "contacto": form.contacto.data,
        "email": form.email.data,
        "telefono": form.telefono.data,
        "condiciones_pago": form.condiciones_pago.data,
        "activo": form.activo.data,
    }


# --------------------------- SUMINISTROS ---------------------------

def _opciones_producto(form):
    productos = producto_servicio.listar_productos()
    form.producto_id.choices = [(p.id, f"{p.referencia} · {p.nombre}") for p in productos]
    return productos


@proveedores_bp.route("/<int:proveedor_id>/suministros/nuevo", methods=["GET", "POST"])
@rol_requerido(*GESTION)
def nuevo_suministro(proveedor_id):
    try:
        proveedor = servicio.obtener_proveedor(proveedor_id)
    except ErrorNegocio as e:
        flash(e.mensaje, "danger")
        return redirect(url_for("proveedores.lista"))

    form = SuministroForm()
    productos = _opciones_producto(form)
    if not productos:
        flash("Crea al menos un producto antes de asignar suministros.", "warning")
        return redirect(url_for("proveedores.detalle", proveedor_id=proveedor_id))

    if form.validate_on_submit():
        try:
            servicio.agregar_suministro(proveedor_id, _datos_suministro(form))
            flash("Suministro añadido.", "success")
            return redirect(url_for("proveedores.detalle", proveedor_id=proveedor_id))
        except ErrorNegocio as e:
            flash(e.mensaje, "danger")
    return render_template(
        "proveedores/suministro_formulario.html", form=form, modo="crear", proveedor=proveedor
    )


@proveedores_bp.route("/suministros/<int:suministro_id>/editar", methods=["GET", "POST"])
@rol_requerido(*GESTION)
def editar_suministro(suministro_id):
    try:
        suministro = servicio.obtener_suministro(suministro_id)
    except ErrorNegocio as e:
        flash(e.mensaje, "danger")
        return redirect(url_for("proveedores.lista"))

    form = SuministroForm(obj=suministro)
    _opciones_producto(form)
    if request.method == "GET":
        form.producto_id.data = suministro.producto_id

    if form.validate_on_submit():
        try:
            servicio.actualizar_suministro(suministro_id, _datos_suministro(form))
            flash("Suministro actualizado.", "success")
            return redirect(url_for("proveedores.detalle", proveedor_id=suministro.proveedor_id))
        except ErrorNegocio as e:
            flash(e.mensaje, "danger")
    return render_template(
        "proveedores/suministro_formulario.html",
        form=form, modo="editar", proveedor=suministro.proveedor, bloquear_producto=True,
    )


@proveedores_bp.route("/suministros/<int:suministro_id>/eliminar", methods=["GET", "POST"])
@rol_requerido(*GESTION)
def eliminar_suministro(suministro_id):
    try:
        suministro = servicio.obtener_suministro(suministro_id)
    except ErrorNegocio as e:
        flash(e.mensaje, "danger")
        return redirect(url_for("proveedores.lista"))

    if request.method == "POST":
        try:
            servicio.eliminar_suministro(suministro_id)
            flash("Suministro eliminado.", "success")
        except ErrorNegocio as e:
            flash(e.mensaje, "danger")
        return redirect(url_for("proveedores.detalle", proveedor_id=suministro.proveedor_id))

    return render_template(
        "confirmar.html", form=FlaskForm(),
        titulo="Quitar suministro",
        mensaje=f"¿Quitar «{suministro.producto.nombre}» de los productos que suministra "
                f"«{suministro.proveedor.nombre}»?",
        accion_url=url_for("proveedores.eliminar_suministro", suministro_id=suministro_id),
        volver_url=url_for("proveedores.detalle", proveedor_id=suministro.proveedor_id),
        confirmar_texto="Sí, quitar",
    )


def _datos_suministro(form) -> dict:
    return {
        "producto_id": form.producto_id.data,
        "precio_proveedor": form.precio_proveedor.data,
        "plazo_entrega_dias": form.plazo_entrega_dias.data,
        "preferente": form.preferente.data,
    }


# --------------------------- COMPARATIVA ---------------------------

@proveedores_bp.route("/comparativa")
@login_required
def comparativa():
    productos = producto_servicio.listar_productos()
    producto_id = request.args.get("producto_id", type=int)
    seleccionado = None
    suministros = []
    if producto_id:
        try:
            seleccionado, suministros = servicio.comparativa_producto(producto_id)
        except ErrorNegocio as e:
            flash(e.mensaje, "danger")
    return render_template(
        "proveedores/comparativa.html",
        productos=productos,
        seleccionado=seleccionado,
        suministros=suministros,
    )
