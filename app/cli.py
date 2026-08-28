"""Comandos de consola: inicialización de la BD, creación de admin y datos de ejemplo."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import click

from .extensiones import db
from .modelos import (
    Usuario,
    RolUsuario,
    Categoria,
    Producto,
    Proveedor,
    ProductoProveedor,
    Venta,
    LineaVenta,
    Compra,
    LineaCompra,
    EstadoCompra,
    MovimientoInventario,
    TipoMovimiento,
)


def registrar_comandos(app):
    app.cli.add_command(init_db)
    app.cli.add_command(crear_admin)
    app.cli.add_command(seed)


@click.command("init-db")
def init_db():
    """Crea todas las tablas de la base de datos."""
    db.create_all()
    click.echo("Base de datos inicializada (tablas creadas).")


@click.command("crear-admin")
@click.option("--nombre", default="Administrador")
@click.option("--email", prompt=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def crear_admin(nombre, email, password):
    """Crea un usuario con rol ADMIN."""
    email = email.lower().strip()
    if db.session.scalar(db.select(Usuario).filter_by(email=email)):
        click.echo(f"Ya existe un usuario con email {email}.")
        return
    admin = Usuario(nombre=nombre, email=email, rol=RolUsuario.ADMIN)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    click.echo(f"Administrador creado: {email}")


@click.command("seed")
def seed():
    """Carga datos de ejemplo (usuarios, catálogo, proveedores, ventas y movimientos)."""
    if db.session.scalar(db.select(Usuario).limit(1)):
        click.echo("La base de datos ya contiene datos. Seed omitido.")
        return

    ahora = datetime.now(timezone.utc)

    # --- Usuarios (uno por rol) ---
    usuarios = {
        RolUsuario.ADMIN: Usuario(nombre="Admin Demo", email="admin@gestor.com", rol=RolUsuario.ADMIN),
        RolUsuario.ALMACEN: Usuario(nombre="Ana Almacén", email="almacen@gestor.com", rol=RolUsuario.ALMACEN),
        RolUsuario.FINANCIERO: Usuario(nombre="Fran Finanzas", email="finanzas@gestor.com", rol=RolUsuario.FINANCIERO),
    }
    for u in usuarios.values():
        u.set_password("Demo1234")
        db.session.add(u)

    # --- Categorías ---
    cat_portatiles = Categoria(nombre="Portátiles", descripcion="Equipos portátiles")
    cat_perifericos = Categoria(nombre="Periféricos", descripcion="Ratones, teclados, monitores")
    cat_redes = Categoria(nombre="Redes", descripcion="Routers, switches y cableado")
    db.session.add_all([cat_portatiles, cat_perifericos, cat_redes])

    # --- Productos ---
    productos = [
        Producto(referencia="PORT-001", nombre="Portátil Pro 14\"", categoria=cat_portatiles,
                 precio_venta=Decimal("1200.00"), coste_adquisicion=Decimal("900.00"),
                 stock_actual=0, stock_minimo=5),
        Producto(referencia="RAT-014", nombre="Ratón inalámbrico", categoria=cat_perifericos,
                 precio_venta=Decimal("25.00"), coste_adquisicion=Decimal("12.00"),
                 stock_actual=0, stock_minimo=20),
        Producto(referencia="MON-027", nombre="Monitor 27\" 4K", categoria=cat_perifericos,
                 precio_venta=Decimal("350.00"), coste_adquisicion=Decimal("240.00"),
                 stock_actual=0, stock_minimo=8),
        Producto(referencia="ROUT-002", nombre="Router WiFi 6", categoria=cat_redes,
                 precio_venta=Decimal("95.00"), coste_adquisicion=Decimal("60.00"),
                 stock_actual=0, stock_minimo=10),
    ]
    db.session.add_all(productos)

    # --- Proveedores ---
    prov_a = Proveedor(nombre="TecnoDistribución S.L.", cif="B12345678",
                       contacto="Laura Gómez", email="ventas@tecnodist.com",
                       telefono="911234567", condiciones_pago="30 días")
    prov_b = Proveedor(nombre="MegaComponentes S.A.", cif="A87654321",
                       contacto="Pedro Ruiz", email="pedidos@megacomp.com",
                       telefono="931112233", condiciones_pago="Contado")
    db.session.add_all([prov_a, prov_b])

    db.session.flush()  # asignar IDs antes de crear relaciones y movimientos

    # --- Suministros (producto_proveedor) ---
    db.session.add_all([
        ProductoProveedor(producto=productos[0], proveedor=prov_a,
                          precio_proveedor=Decimal("900.00"), plazo_entrega_dias=7, preferente=True),
        ProductoProveedor(producto=productos[0], proveedor=prov_b,
                          precio_proveedor=Decimal("920.00"), plazo_entrega_dias=3, preferente=False),
        ProductoProveedor(producto=productos[1], proveedor=prov_b,
                          precio_proveedor=Decimal("12.00"), plazo_entrega_dias=2, preferente=True),
        ProductoProveedor(producto=productos[2], proveedor=prov_a,
                          precio_proveedor=Decimal("240.00"), plazo_entrega_dias=5, preferente=True),
        ProductoProveedor(producto=productos[3], proveedor=prov_a,
                          precio_proveedor=Decimal("60.00"), plazo_entrega_dias=4, preferente=True),
    ])

    admin = usuarios[RolUsuario.ADMIN]
    almacen = usuarios[RolUsuario.ALMACEN]

    # --- Compra recibida: genera ENTRADAS y sube el stock ---
    compra = Compra(proveedor=prov_a, usuario=almacen, estado=EstadoCompra.RECIBIDA,
                    fecha=ahora - timedelta(days=20))
    entradas = [(productos[0], 15), (productos[2], 12), (productos[3], 25)]
    total_compra = Decimal("0")
    for producto, cantidad in entradas:
        coste = producto.coste_adquisicion
        compra.lineas.append(LineaCompra(producto=producto, cantidad=cantidad, coste_unitario=coste))
        total_compra += coste * cantidad
        producto.stock_actual += cantidad
        db.session.add(MovimientoInventario(
            producto=producto, tipo=TipoMovimiento.ENTRADA, cantidad=cantidad,
            motivo="Compra inicial", usuario=almacen, compra=compra,
            fecha=ahora - timedelta(days=20)))
    compra.total = total_compra
    db.session.add(compra)

    # Entrada de ratones por ajuste (para que haya varias fuentes de stock)
    productos[1].stock_actual += 40
    db.session.add(MovimientoInventario(
        producto=productos[1], tipo=TipoMovimiento.ENTRADA, cantidad=40,
        motivo="Stock inicial", usuario=almacen, fecha=ahora - timedelta(days=20)))

    # --- Ventas: generan SALIDAS y bajan el stock ---
    ventas_demo = [
        (18, [(productos[0], 3), (productos[1], 5)], "Cliente Mostrador"),
        (10, [(productos[2], 4), (productos[3], 6)], "Oficinas del Sur"),
        (3, [(productos[0], 2), (productos[1], 8), (productos[3], 5)], "Cliente Mostrador"),
    ]
    for dias_atras, lineas, cliente in ventas_demo:
        venta = Venta(usuario=admin, cliente=cliente, fecha=ahora - timedelta(days=dias_atras))
        total_venta = Decimal("0")
        for producto, cantidad in lineas:
            venta.lineas.append(LineaVenta(
                producto=producto, cantidad=cantidad,
                precio_unitario=producto.precio_venta,
                coste_unitario=producto.coste_adquisicion))
            total_venta += producto.precio_venta * cantidad
            producto.stock_actual -= cantidad
            db.session.add(MovimientoInventario(
                producto=producto, tipo=TipoMovimiento.SALIDA, cantidad=cantidad,
                motivo="Venta", usuario=admin, venta=venta,
                fecha=ahora - timedelta(days=dias_atras)))
        venta.total = total_venta
        db.session.add(venta)

    db.session.commit()
    click.echo("Datos de ejemplo cargados.")
    click.echo("Usuarios demo (contraseña: Demo1234):")
    click.echo("  admin@gestor.com     -> ADMIN")
    click.echo("  almacen@gestor.com   -> ALMACEN")
    click.echo("  finanzas@gestor.com  -> FINANCIERO")
