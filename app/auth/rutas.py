"""Rutas de autenticación: login y logout."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from ..extensiones import db
from ..modelos import Usuario
from .formularios import LoginForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        usuario = db.session.scalar(
            db.select(Usuario).filter_by(email=form.email.data.lower().strip())
        )
        if usuario is None or not usuario.check_password(form.password.data):
            flash("Email o contraseña incorrectos.", "danger")
        elif not usuario.activo:
            flash("Este usuario está desactivado.", "warning")
        else:
            login_user(usuario, remember=form.recordar.data)
            siguiente = request.args.get("next")
            return redirect(siguiente or url_for("main.dashboard"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))
