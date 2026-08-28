"""Rutas generales: inicio y panel de control."""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

from ..extensiones import db
from ..modelos import Producto, Proveedor, Venta, Categoria

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return redirect(url_for("main.dashboard"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    resumen = {
        "productos": db.session.scalar(db.select(db.func.count(Producto.id))),
        "proveedores": db.session.scalar(db.select(db.func.count(Proveedor.id))),
        "categorias": db.session.scalar(db.select(db.func.count(Categoria.id))),
        "ventas": db.session.scalar(db.select(db.func.count(Venta.id))),
    }
    bajo_stock = db.session.scalars(
        db.select(Producto).where(Producto.stock_actual <= Producto.stock_minimo)
    ).all()
    return render_template("main/dashboard.html", resumen=resumen, bajo_stock=bajo_stock)
