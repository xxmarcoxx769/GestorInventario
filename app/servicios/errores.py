"""Errores de negocio compartidos por la capa de servicios."""


class ErrorNegocio(Exception):
    """Error de regla de negocio. `codigo` mapea a un estado HTTP orientativo."""

    codigo = 400

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class NoEncontrado(ErrorNegocio):
    codigo = 404


class Conflicto(ErrorNegocio):
    codigo = 409
