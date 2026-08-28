"""Control de accesos por rol."""
from functools import wraps

from flask import abort
from flask_login import current_user


def rol_requerido(*roles):
    """Restringe una vista a los roles indicados.

    Uso:
        @rol_requerido(RolUsuario.ADMIN, RolUsuario.ALMACEN)
        def crear_producto(): ...
    """

    def decorador(vista):
        @wraps(vista)
        def envoltura(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.rol not in roles:
                abort(403)
            return vista(*args, **kwargs)

        return envoltura

    return decorador
