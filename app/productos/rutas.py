"""Rutas de productos y categorías.

Permisos: ver = cualquier rol autenticado; crear/editar/eliminar = ADMIN o ALMACEN.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm

from ..modelos import RolUsuario
from ..auth.decoradores import rol_requerido
from ..servicios import producto_servicio as servicio
from ..servicios import categoria_servicio as cat_servicio
from ..servicios.errores import ErrorNegocio
from .formularios import ProductoForm, CategoriaForm

productos_bp = Blueprint("productos", __name__, url_prefix="/productos")
categorias_bp = Blueprint("categorias", __name__, url_prefix="/categorias")

GESTION = (RolUsuario.ADMIN, RolUsuario.ALMACEN)


# --------------------------- PRODUCTOS ---------------------------

@productos_bp.route("/")
@login_required
def lista():
    categoria_id = request.args.get("categoria_id", type=int)
    buscar = request.args.get("buscar", type=str)
    bajo_stock = request.args.get("bajo_stock") == "1"
    productos = servicio.listar_productos(
        categoria_id=categoria_id, buscar=buscar, solo_bajo_stock=bajo_stock
    )
    categorias = cat_servicio.listar_categorias()
    return render_template(
        "productos/lista.html",
        productos=productos,
        categorias=categorias,
        filtro={"categoria_id": categoria_id, "buscar": buscar or "", "bajo_stock": bajo_stock},
        puede_gestionar=current_user.rol in GESTION,
    )


def _opciones_categoria(form):
    categorias = cat_servicio.listar_categorias()
    form.categoria_id.choices = [(c.id, c.nombre) for c in categorias]
    return categorias


@productos_bp.route("/nuevo", methods=["GET", "POST"])
@rol_requerido(*GESTION)
def nuevo():
    form = ProductoForm()
    categorias = _opciones_categoria(form)
    if not categorias:
        flash("Crea al menos una categoría antes de añadir productos.", "warning")
        return redirect(url_for("categorias.lista"))

    if form.validate_on_submit():
        try:
            producto = servicio.crear_producto(
                {
                    "referencia": form.referencia.data,
                    "nombre": form.nombre.data,
                    "categoria_id": form.categoria_id.data,
                    "precio_venta": form.precio_venta.data,
                    "coste_adquisicion": form.coste_adquisicion.data,
                    "stock_minimo": form.stock_minimo.data,
                    "stock_inicial": form.stock_inicial.data,
                    "activo": form.activo.data,
                },
                usuario_id=current_user.id,
            )
            flash(f"Producto «{producto.nombre}» creado.", "success")
            return redirect(url_for("productos.lista"))
        except ErrorNegocio as e:
            flash(e.mensaje, "danger")

    return render_template("productos/formulario.html", form=form, modo="crear")


@productos_bp.route("/<int:producto_id>/editar", methods=["GET", "POST"])
@rol_requerido(*GESTION)
def editar(producto_id):
    try:
        producto = servicio.obtener_producto(producto_id)
    except ErrorNegocio as e:
        flash(e.mensaje, "danger")
        return redirect(url_for("productos.lista"))

    form = ProductoForm(obj=producto)
    _opciones_categoria(form)

    if form.validate_on_submit():
        try:
            servicio.actualizar_producto(
                producto_id,
                {
                    "referencia": form.referencia.data,
                    "nombre": form.nombre.data,
                    "categoria_id": form.categoria_id.data,
                    "precio_venta": form.precio_venta.data,
                    "coste_adquisicion": form.coste_adquisicion.data,
                    "stock_minimo": form.stock_minimo.data,
                    "activo": form.activo.data,
                },
            )
            flash("Producto actualizado.", "success")
            return redirect(url_for("productos.lista"))
        except ErrorNegocio as e:
            flash(e.mensaje, "danger")

    return render_template("productos/formulario.html", form=form, modo="editar", producto=producto)


@productos_bp.route("/<int:producto_id>/eliminar", methods=["GET", "POST"])
@rol_requerido(*GESTION)
def eliminar(producto_id):
    try:
        producto = servicio.obtener_producto(producto_id)
    except ErrorNegocio as e:
        flash(e.mensaje, "danger")
        return redirect(url_for("productos.lista"))

    if request.method == "POST":
        try:
            servicio.eliminar_producto(producto_id)
            flash("Producto eliminado.", "success")
        except ErrorNegocio as e:
            flash(e.mensaje, "danger")
        return redirect(url_for("productos.lista"))

    return render_template(
        "confirmar.html", form=FlaskForm(),
        titulo="Eliminar producto",
        mensaje=f"¿Seguro que quieres eliminar «{producto.nombre}»? Esta acción no se puede deshacer.",
        accion_url=url_for("productos.eliminar", producto_id=producto_id),
        volver_url=url_for("productos.lista"), confirmar_texto="Sí, eliminar",
    )


# --------------------------- CATEGORÍAS ---------------------------

@categorias_bp.route("/")
@login_required
def lista():
    categorias = cat_servicio.listar_categorias()
    return render_template(
        "categorias/lista.html",
        categorias=categorias,
        puede_gestionar=current_user.rol in GESTION,
    )


@categorias_bp.route("/nueva", methods=["GET", "POST"])
@rol_requerido(*GESTION)
def nueva():
    form = CategoriaForm()
    if form.validate_on_submit():
        try:
            cat_servicio.crear_categoria(form.nombre.data, form.descripcion.data)
            flash("Categoría creada.", "success")
            return redirect(url_for("categorias.lista"))
        except ErrorNegocio as e:
            flash(e.mensaje, "danger")
    return render_template("categorias/formulario.html", form=form, modo="crear")


@categorias_bp.route("/<int:categoria_id>/editar", methods=["GET", "POST"])
@rol_requerido(*GESTION)
def editar(categoria_id):
    try:
        categoria = cat_servicio.obtener_categoria(categoria_id)
    except ErrorNegocio as e:
        flash(e.mensaje, "danger")
        return redirect(url_for("categorias.lista"))

    form = CategoriaForm(obj=categoria)
    if form.validate_on_submit():
        try:
            cat_servicio.actualizar_categoria(categoria_id, form.nombre.data, form.descripcion.data)
            flash("Categoría actualizada.", "success")
            return redirect(url_for("categorias.lista"))
        except ErrorNegocio as e:
            flash(e.mensaje, "danger")
    return render_template("categorias/formulario.html", form=form, modo="editar")


@categorias_bp.route("/<int:categoria_id>/eliminar", methods=["GET", "POST"])
@rol_requerido(*GESTION)
def eliminar(categoria_id):
    try:
        categoria = cat_servicio.obtener_categoria(categoria_id)
    except ErrorNegocio as e:
        flash(e.mensaje, "danger")
        return redirect(url_for("categorias.lista"))

    if request.method == "POST":
        try:
            cat_servicio.eliminar_categoria(categoria_id)
            flash("Categoría eliminada.", "success")
        except ErrorNegocio as e:
            flash(e.mensaje, "danger")
        return redirect(url_for("categorias.lista"))

    return render_template(
        "confirmar.html", form=FlaskForm(),
        titulo="Eliminar categoría",
        mensaje=f"¿Seguro que quieres eliminar la categoría «{categoria.nombre}»?",
        accion_url=url_for("categorias.eliminar", categoria_id=categoria_id),
        volver_url=url_for("categorias.lista"), confirmar_texto="Sí, eliminar",
    )
