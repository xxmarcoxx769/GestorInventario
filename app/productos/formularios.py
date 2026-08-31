"""Formularios de productos y categorías."""
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    DecimalField,
    IntegerField,
    BooleanField,
    SelectField,
    TextAreaField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ProductoForm(FlaskForm):
    referencia = StringField("Referencia interna", validators=[DataRequired(), Length(max=40)])
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=150)])
    categoria_id = SelectField("Categoría", coerce=int, validators=[DataRequired()])
    precio_venta = DecimalField(
        "Precio de venta (€)", places=2, validators=[DataRequired(), NumberRange(min=0)]
    )
    coste_adquisicion = DecimalField(
        "Coste de adquisición (€)", places=2, validators=[DataRequired(), NumberRange(min=0)]
    )
    stock_minimo = IntegerField(
        "Stock mínimo", default=0, validators=[Optional(), NumberRange(min=0)]
    )
    stock_inicial = IntegerField(
        "Stock inicial", default=0, validators=[Optional(), NumberRange(min=0)]
    )
    activo = BooleanField("Activo", default=True)
    submit = SubmitField("Guardar")


class CategoriaForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=80)])
    descripcion = TextAreaField("Descripción", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Guardar")
