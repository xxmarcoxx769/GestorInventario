"""Rutas de inventario: historial de movimientos y ajuste manual de stock.

Permisos: ver historial = cualquier rol; ajustar stock = ADMIN o ALMACEN.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import InputRequired, NumberRange, Optional, DataRequired

from ..modelos import RolUsuario, TipoMovimiento
from ..auth.decoradores import rol_requerido
from ..servicios import inventario_servicio as servicio
from ..servicios import producto_servicio
from ..servicios.errores import ErrorNegocio

inventario_bp = Blueprint("inventario", __name__, url_prefix="/inventario")
GESTION = (RolUsuario.ADMIN, RolUsuario.ALMACEN)


class AjusteForm(FlaskForm):
    producto_id = SelectField("Producto", coerce=int, validators=[DataRequired()])
    nuevo_stock = IntegerField("Nuevo stock (recuento físico)", validators=[InputRequired(), NumberRange(min=0)])
    motivo = StringField("Motivo", validators=[Optional()])
    submit = SubmitField("Registrar ajuste")


@inventario_bp.route("/")
@login_required
def movimientos():
    producto_id = request.args.get("producto_id", type=int)
    tipo = request.args.get("tipo", type=str) or None
    movs = servicio.listar_movimientos(producto_id=producto_id, tipo=tipo)
    productos = producto_servicio.listar_productos()
    return render_template(
        "inventario/movimientos.html",
        movimientos=movs,
        productos=productos,
        filtro={"producto_id": producto_id, "tipo": tipo or ""},
        tipos=TipoMovimiento.TODOS,
        puede_gestionar=current_user.rol in GESTION,
    )


@inventario_bp.route("/ajuste", methods=["GET", "POST"])
@rol_requerido(*GESTION)
def ajuste():
    form = AjusteForm()
    productos = producto_servicio.listar_productos()
    form.producto_id.choices = [
        (p.id, f"{p.referencia} · {p.nombre} (stock: {p.stock_actual})") for p in productos
    ]
    if not productos:
        flash("Crea al menos un producto antes de ajustar stock.", "warning")
        return redirect(url_for("productos.lista"))

    if form.validate_on_submit():
        try:
            servicio.ajustar_stock(
                form.producto_id.data, form.nuevo_stock.data,
                current_user.id, form.motivo.data,
            )
            flash("Ajuste de stock registrado.", "success")
            return redirect(url_for("inventario.movimientos"))
        except ErrorNegocio as e:
            flash(e.mensaje, "danger")

    return render_template("inventario/ajuste.html", form=form)
