"""Formularios de proveedores y suministros."""
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    DecimalField,
    IntegerField,
    BooleanField,
    SelectField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Email


class ProveedorForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=150)])
    cif = StringField("CIF", validators=[DataRequired(), Length(max=20)])
    contacto = StringField("Persona de contacto", validators=[Optional(), Length(max=120)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    telefono = StringField("Teléfono", validators=[Optional(), Length(max=30)])
    condiciones_pago = StringField("Condiciones de pago", validators=[Optional(), Length(max=120)])
    activo = BooleanField("Activo", default=True)
    submit = SubmitField("Guardar")


class SuministroForm(FlaskForm):
    producto_id = SelectField("Producto", coerce=int, validators=[DataRequired()])
    precio_proveedor = DecimalField(
        "Precio del proveedor (€)", places=2, validators=[DataRequired(), NumberRange(min=0)]
    )
    plazo_entrega_dias = IntegerField(
        "Plazo de entrega (días)", validators=[Optional(), NumberRange(min=0)]
    )
    preferente = BooleanField("Proveedor preferente para este producto")
    submit = SubmitField("Guardar")
