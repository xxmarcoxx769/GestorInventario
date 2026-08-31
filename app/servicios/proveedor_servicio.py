"""Lógica de negocio para proveedores y suministros (producto_proveedor)."""
from ..extensiones import db
from ..modelos import Proveedor, ProductoProveedor, Producto, Compra
from .errores import NoEncontrado, Conflicto


# --------------------------- PROVEEDORES ---------------------------

def listar_proveedores(buscar=None):
    consulta = db.select(Proveedor)
    if buscar:
        patron = f"%{buscar.strip()}%"
        consulta = consulta.where(
            db.or_(Proveedor.nombre.ilike(patron), Proveedor.cif.ilike(patron))
        )
    return db.session.scalars(consulta.order_by(Proveedor.nombre)).all()


def obtener_proveedor(proveedor_id: int) -> Proveedor:
    proveedor = db.session.get(Proveedor, proveedor_id)
    if proveedor is None:
        raise NoEncontrado("El proveedor no existe.")
    return proveedor


def _validar_cif_unico(cif: str, excluir_id: int | None = None):
    consulta = db.select(Proveedor).where(Proveedor.cif == cif)
    if excluir_id is not None:
        consulta = consulta.where(Proveedor.id != excluir_id)
    if db.session.scalar(consulta):
        raise Conflicto(f"Ya existe un proveedor con el CIF «{cif}».")


def crear_proveedor(datos: dict) -> Proveedor:
    cif = datos["cif"].strip().upper()
    _validar_cif_unico(cif)
    proveedor = Proveedor(
        nombre=datos["nombre"].strip(),
        cif=cif,
        contacto=(datos.get("contacto") or "").strip() or None,
        email=(datos.get("email") or "").strip() or None,
        telefono=(datos.get("telefono") or "").strip() or None,
        condiciones_pago=(datos.get("condiciones_pago") or "").strip() or None,
        activo=datos.get("activo", True),
    )
    db.session.add(proveedor)
    db.session.commit()
    return proveedor


def actualizar_proveedor(proveedor_id: int, datos: dict) -> Proveedor:
    proveedor = obtener_proveedor(proveedor_id)
    cif = datos["cif"].strip().upper()
    _validar_cif_unico(cif, excluir_id=proveedor_id)
    proveedor.nombre = datos["nombre"].strip()
    proveedor.cif = cif
    proveedor.contacto = (datos.get("contacto") or "").strip() or None
    proveedor.email = (datos.get("email") or "").strip() or None
    proveedor.telefono = (datos.get("telefono") or "").strip() or None
    proveedor.condiciones_pago = (datos.get("condiciones_pago") or "").strip() or None
    proveedor.activo = datos.get("activo", True)
    db.session.commit()
    return proveedor


def eliminar_proveedor(proveedor_id: int) -> None:
    proveedor = obtener_proveedor(proveedor_id)
    tiene_compras = db.session.scalar(
        db.select(Compra.id).where(Compra.proveedor_id == proveedor_id).limit(1)
    )
    if tiene_compras:
        raise Conflicto(
            "No se puede eliminar: el proveedor tiene compras registradas. "
            "Desactívalo en su lugar."
        )
    db.session.delete(proveedor)  # elimina en cascada sus suministros
    db.session.commit()


# --------------------------- SUMINISTROS (producto_proveedor) ---------------------------

def listar_suministros(proveedor_id: int):
    obtener_proveedor(proveedor_id)
    return db.session.scalars(
        db.select(ProductoProveedor)
        .join(Producto)
        .where(ProductoProveedor.proveedor_id == proveedor_id)
        .order_by(Producto.nombre)
    ).all()


def obtener_suministro(suministro_id: int) -> ProductoProveedor:
    suministro = db.session.get(ProductoProveedor, suministro_id)
    if suministro is None:
        raise NoEncontrado("El suministro no existe.")
    return suministro


def _desmarcar_preferentes(producto_id: int, excluir_id: int | None = None):
    """Solo puede haber un proveedor preferente por producto."""
    consulta = db.select(ProductoProveedor).where(
        ProductoProveedor.producto_id == producto_id,
        ProductoProveedor.preferente.is_(True),
    )
    if excluir_id is not None:
        consulta = consulta.where(ProductoProveedor.id != excluir_id)
    for otro in db.session.scalars(consulta):
        otro.preferente = False


def agregar_suministro(proveedor_id: int, datos: dict) -> ProductoProveedor:
    obtener_proveedor(proveedor_id)
    producto_id = datos["producto_id"]
    if db.session.get(Producto, producto_id) is None:
        raise NoEncontrado("El producto seleccionado no existe.")

    existe = db.session.scalar(
        db.select(ProductoProveedor).where(
            ProductoProveedor.proveedor_id == proveedor_id,
            ProductoProveedor.producto_id == producto_id,
        )
    )
    if existe:
        raise Conflicto("Este proveedor ya suministra ese producto.")

    preferente = datos.get("preferente", False)
    if preferente:
        _desmarcar_preferentes(producto_id)

    suministro = ProductoProveedor(
        proveedor_id=proveedor_id,
        producto_id=producto_id,
        precio_proveedor=datos["precio_proveedor"],
        plazo_entrega_dias=datos.get("plazo_entrega_dias"),
        preferente=preferente,
    )
    db.session.add(suministro)
    db.session.commit()
    return suministro


def actualizar_suministro(suministro_id: int, datos: dict) -> ProductoProveedor:
    suministro = obtener_suministro(suministro_id)
    preferente = datos.get("preferente", False)
    if preferente:
        _desmarcar_preferentes(suministro.producto_id, excluir_id=suministro_id)
    suministro.precio_proveedor = datos["precio_proveedor"]
    suministro.plazo_entrega_dias = datos.get("plazo_entrega_dias")
    suministro.preferente = preferente
    db.session.commit()
    return suministro


def eliminar_suministro(suministro_id: int) -> int:
    suministro = obtener_suministro(suministro_id)
    proveedor_id = suministro.proveedor_id
    db.session.delete(suministro)
    db.session.commit()
    return proveedor_id


def comparativa_producto(producto_id: int):
    """Proveedores de un producto ordenados por precio ascendente (más barato primero)."""
    producto = db.session.get(Producto, producto_id)
    if producto is None:
        raise NoEncontrado("El producto no existe.")
    suministros = db.session.scalars(
        db.select(ProductoProveedor)
        .where(ProductoProveedor.producto_id == producto_id)
        .order_by(ProductoProveedor.precio_proveedor.asc())
    ).all()
    return producto, suministros
