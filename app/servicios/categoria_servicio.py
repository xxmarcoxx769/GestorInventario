"""Lógica de negocio para categorías."""
from ..extensiones import db
from ..modelos import Categoria, Producto
from .errores import NoEncontrado, Conflicto


def listar_categorias():
    return db.session.scalars(db.select(Categoria).order_by(Categoria.nombre)).all()


def obtener_categoria(categoria_id: int) -> Categoria:
    categoria = db.session.get(Categoria, categoria_id)
    if categoria is None:
        raise NoEncontrado("La categoría no existe.")
    return categoria


def _validar_nombre_unico(nombre: str, excluir_id: int | None = None):
    consulta = db.select(Categoria).where(Categoria.nombre == nombre)
    if excluir_id is not None:
        consulta = consulta.where(Categoria.id != excluir_id)
    if db.session.scalar(consulta):
        raise Conflicto(f"Ya existe una categoría llamada «{nombre}».")


def crear_categoria(nombre: str, descripcion: str | None) -> Categoria:
    nombre = nombre.strip()
    _validar_nombre_unico(nombre)
    categoria = Categoria(nombre=nombre, descripcion=(descripcion or "").strip() or None)
    db.session.add(categoria)
    db.session.commit()
    return categoria


def actualizar_categoria(categoria_id: int, nombre: str, descripcion: str | None) -> Categoria:
    categoria = obtener_categoria(categoria_id)
    nombre = nombre.strip()
    _validar_nombre_unico(nombre, excluir_id=categoria_id)
    categoria.nombre = nombre
    categoria.descripcion = (descripcion or "").strip() or None
    db.session.commit()
    return categoria


def eliminar_categoria(categoria_id: int) -> None:
    categoria = obtener_categoria(categoria_id)
    tiene_productos = db.session.scalar(
        db.select(Producto.id).where(Producto.categoria_id == categoria_id).limit(1)
    )
    if tiene_productos:
        raise Conflicto("No se puede eliminar: la categoría tiene productos asociados.")
    db.session.delete(categoria)
    db.session.commit()
