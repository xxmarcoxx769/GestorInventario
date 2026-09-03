# Gestor de Inventario para una Empresa de Suministros Tecnológicos

**Proyecto Final de Python — Propuesta A**

**Nombre y apellidos:** Marco Jiménez Lorente
**Fecha:** _[completar]_


---

## Índice de contenidos

1. Descripción general del proyecto
2. Objetivos y alcance del proyecto
3. Stack tecnológico y alternativas evaluadas
4. Modelo de datos: explicación de la base de datos y esquema
5. Explicación de los requisitos de la aplicación
6. Manual de instalación
7. Conclusiones
8. Evolutivos del proyecto

---

## 1. Descripción general del proyecto

El proyecto consiste en una **aplicación web** para la gestión integral de una
empresa de suministros tecnológicos. La empresa ha crecido en volumen de productos
y ventas, pero su sistema anterior solo permitía **registrar datos**, sin ofrecer
análisis ni información estratégica. Esto provocaba roturas de stock inesperadas,
acumulación de productos de baja rotación, desconocimiento del margen real por
producto y dificultad para comparar proveedores.

La aplicación desarrollada no se limita a almacenar información: la **analiza y la
transforma en conocimiento útil** para la toma de decisiones. Permite gestionar
productos, categorías, proveedores, ventas, compras e inventario, y ofrece un panel
de análisis con métricas e indicadores calculados dinámicamente (productos más
vendidos y más rentables, evolución de ventas, estimación de días hasta agotar
stock, etc.).

La aplicación incorpora un **sistema de autenticación con control de accesos por
rol** (administrador, responsable de almacén y responsable financiero), de forma que
cada usuario accede únicamente a las funcionalidades que le corresponden.

Una decisión de diseño importante es que **toda la lógica de la interfaz se resuelve
en el servidor con Python**: los formularios dinámicos, las confirmaciones de las
acciones y hasta las gráficas se generan en el backend, sin utilizar JavaScript. Con
ello el proyecto demuestra de forma clara la comunicación entre el backend y el
frontend usando exclusivamente Python.

---

## 2. Objetivos y alcance del proyecto

### 2.1. Objetivos

Los objetivos del proyecto son claros, medibles y realistas:

- **Centralizar la gestión** del catálogo (productos y categorías), los proveedores,
  las ventas, las compras y el inventario en una única aplicación.
- **Garantizar la integridad del stock**: que cada cambio de existencias quede
  registrado como un movimiento de inventario y que las ventas y compras actualicen
  el stock de forma automática y consistente.
- **Controlar el acceso** mediante autenticación segura y **tres roles** con permisos
  diferenciados.
- **Aportar información para la decisión**: calcular márgenes, detectar riesgo de
  rotura de stock, medir la rotación y estimar los días restantes hasta agotar cada
  producto.
- **Comparar proveedores** por precio y condiciones para un mismo producto.
- **Visualizar métricas** mediante gráficas generadas en el servidor.
- **Ser reproducible**: que cualquier persona (incluido el tribunal) pueda instalarlo
  y ejecutarlo sin problemas de versiones, mediante un entorno virtual y dependencias
  fijadas.

### 2.2. Alcance

**Incluido en el proyecto:**

- Autenticación por sesión y control de accesos por rol.
- CRUD de productos y categorías.
- CRUD de proveedores y gestión de suministros (relación producto–proveedor con
  precio por proveedor), incluyendo comparativa de precios.
- Registro de ventas que descuentan stock, y de compras con flujo
  pendiente → recibida que incrementa stock.
- Historial completo de movimientos de inventario (entradas, salidas y ajustes) y
  ajuste manual de stock por recuento.
- Panel de análisis con KPIs y gráficas (Matplotlib) y estimación de días hasta
  agotar stock.
- Interfaz web responsive con Bootstrap, servida íntegramente desde el servidor.

**Fuera del alcance (para acotar el proyecto):**

- No hay pasarela de pago ni gestión contable/fiscal.
- No hay gestión de clientes como entidad (CRM); el cliente de una venta es un campo
  de texto opcional.
- No hay envío de correos ni notificaciones externas.
- La gestión de usuarios se realiza por línea de comandos (creación de
  administradores), no desde una interfaz gráfica de administración de usuarios.
- No es una aplicación multi-idioma ni multi-empresa.

---

## 3. Stack tecnológico y alternativas evaluadas

### 3.1. Stack tecnológico

| Capa | Tecnología | Función |
|---|---|---|
| Lenguaje | **Python 3.13** | Lenguaje principal del proyecto |
| Framework web | **Flask 3.1** | Servidor web y enrutado (patrón *application factory* + *blueprints*) |
| ORM | **SQLAlchemy 2.0** (Flask-SQLAlchemy) | Mapeo objeto-relacional (programación orientada a objetos) |
| Base de datos | **SQLite 3** | Base de datos relacional en un único fichero, sin servidor |
| Autenticación | **Flask-Login** | Sesión de usuario y control de acceso |
| Formularios | **Flask-WTF / WTForms** | Validación de formularios y protección CSRF |
| Plantillas | **Jinja2** | Renderizado del HTML en el servidor |
| Estilos | **Bootstrap 5** | Diseño responsive (servido en local) |
| Gráficas | **Matplotlib** | Generación de gráficas en el servidor (backend `Agg`) |
| Seguridad | **Werkzeug** | Hash de contraseñas |

### 3.2. Alternativas evaluadas

| Elección | Alternativa evaluada | Motivo de la decisión |
|---|---|---|
| **Flask** | Django | Flask es ligero y didáctico; Django incorpora ORM y panel de administración propios, pero resultaba excesivo para el alcance y ocultaba la lógica que se quería mostrar. |
| **SQLite 3** | PostgreSQL / MySQL | SQLite no requiere instalar ningún servidor: la base de datos es un fichero. Esto facilita enormemente que el proyecto se ejecute en cualquier equipo sin configuración. |
| **SQLAlchemy (ORM)** | Módulo `sqlite3` directo | El ORM permite trabajar con clases (POO), gestiona relaciones y transacciones, y mantiene el código portable y legible. |
| **Aplicación renderizada en servidor** | API REST + frontend (React) | El renderizado en servidor simplifica la ejecución (un solo proceso, sin compilar el frontend) y facilita las capturas para la documentación. |
| **Matplotlib en el servidor** | Chart.js (JavaScript) | Se optó por generar las gráficas en Python e inyectarlas como imágenes: evita depender de JavaScript, refuerza la comunicación backend↔frontend y funciona sin conexión a internet. |
| **Flask-Login (sesión)** | JWT | Para una aplicación renderizada en servidor, la sesión con cookie es más simple y natural que un token JWT. |

---

## 4. Modelo de datos: explicación de la base de datos y esquema

La aplicación utiliza una **base de datos relacional en SQLite 3**, gestionada
mediante el ORM SQLAlchemy. El esquema consta de **10 tablas** que cubren usuarios y
roles, catálogo, proveedores, ventas, compras y el historial de inventario.

El diagrama entidad-relación completo y el diccionario de datos se encuentran en el
documento [modelo-datos.md](modelo-datos.md). A continuación se resume el diseño:

- **`usuarios`**: credenciales y rol (ADMIN, ALMACEN, FINANCIERO).
- **`categorias`** y **`productos`**: catálogo. Cada producto guarda referencia,
  precio de venta, coste de adquisición, stock y stock mínimo. El **margen de beneficio se calcula** (precio − coste), no se almacena editable.
- **`proveedores`** y **`producto_proveedor`**: proveedores y la relación N:M que
  indica qué proveedor suministra qué producto y a qué precio.
- **`ventas`** y **`lineas_venta`**: cada línea **congela** el precio y el coste en el
  momento de la venta, para que las métricas históricas sean correctas.
- **`compras`** y **`lineas_compra`**: compras a proveedores, con estado
  (PENDIENTE / RECIBIDA / CANCELADA).
- **`movimientos_inventario`**: **fuente de verdad del stock**. Toda entrada, salida
  o ajuste queda registrada aquí; el campo `stock_actual` de `productos` es un
  contador que se mantiene sincronizado en la misma transacción.

Consideraciones específicas de SQLite tenidas en cuenta: activación de claves foráneas
(`PRAGMA foreign_keys = ON`), uso de `Numeric` para importes y fechas en formato
ISO-8601.

### 4.1. Tablas de la base de datos (con datos de ejemplo)

A continuación se muestran las 10 tablas de la base de datos con datos de ejemplo,
visualizadas desde DBeaver.

![Tabla usuarios](img/usuarios_page-0001.jpg)
*Figura 1. Tabla `usuarios`.*

![Tabla categorias](img/categorias_page-0001.jpg)
*Figura 2. Tabla `categorias`.*

![Tabla productos](img/productos_page-0001.jpg)
*Figura 3. Tabla `productos`.*

![Tabla proveedores](img/proveedores_page-0001.jpg)
*Figura 4. Tabla `proveedores`.*

![Tabla producto_proveedor](img/producto_proveedor_page-0001.jpg)
*Figura 5. Tabla `producto_proveedor` (relación N:M productos–proveedores).*

![Tabla ventas](img/ventas_page-0001.jpg)
*Figura 6. Tabla `ventas`.*

![Tabla lineas_venta](img/lineas_venta_page-0001.jpg)
*Figura 7. Tabla `lineas_venta`.*

![Tabla compras](img/compras_page-0001.jpg)
*Figura 8. Tabla `compras`.*

![Tabla lineas_compra](img/lineas_compra_page-0001.jpg)
*Figura 9. Tabla `lineas_compra`.*

![Tabla movimientos_inventario](img/movimientos_inventario_page-0001.jpg)
*Figura 10. Tabla `movimientos_inventario` (fuente de verdad del stock).*

---

## 5. Explicación de los requisitos de la aplicación

Cada requisito funcional se acompaña de capturas de pantalla que demuestran su
funcionamiento.

### 5.1. Requisitos funcionales

**RF1 — Registro y control de acceso.**
La aplicación incluye autenticación mediante email y contraseña (contraseñas
almacenadas con hash). Existen tres roles con permisos diferenciados. Cada vista está
protegida según el rol mediante un decorador `rol_requerido`.

![Pantalla de inicio de sesión](img/Pantalla_inicio_sesion.png)
*Figura 11. Pantalla de inicio de sesión.*

![Acceso denegado (error 403)](img/Error403.png)
*Figura 12. Mensaje de acceso denegado (error 403) al intentar una acción sin permiso.*

**RF2 — Base de datos relacional.**
La información se almacena en 10 tablas relacionadas correctamente diseñadas. El esquema,
el diagrama entidad-relación y las tablas con datos de ejemplo se detallan en el
**apartado 4** (Figuras 1–10).

**RF3 — Gestión de productos y categorías.**
Alta, edición y baja de productos y categorías. La referencia de producto y el nombre
de categoría son únicos. El margen se muestra calculado. La baja está protegida: no se
puede eliminar un producto con movimientos, ventas o compras asociados.

![Listado de productos](img/Listado_productos.png)
*Figura 13. Listado de productos con su margen y stock.*

![Formulario de alta de producto](img/Formulario_alta_producto.png)
*Figura 14. Formulario de alta de producto.*

![Formulario de edición de producto](img/Formulario_editar_producto.png)
*Figura 15. Formulario de edición de producto.*

**RF4 — Gestión de inventario y actualización automática de stock.**
Las ventas generan movimientos de **salida** y las compras recibidas generan
movimientos de **entrada**, actualizando el stock en la misma transacción. Existe un
**historial completo de movimientos** (entradas, salidas y ajustes) y un **ajuste
manual** por recuento físico.

![Historial de movimientos de inventario](img/Historial_movimientos_inventario.png)
*Figura 16. Historial de movimientos de inventario.*

![Formulario de ajuste de stock](img/Formulario_ajuste_stock.png)
*Figura 17. Formulario de ajuste de stock.*

**RF5 — Registro de ventas.**
Registro de ventas con varias líneas; cada venta descuenta stock y valida que haya
existencias suficientes (si no, se revierte la operación completa). El detalle muestra
el beneficio por línea y total.

![Formulario de nueva venta](img/Formulario_nueva_venta.png)
*Figura 18. Formulario de nueva venta con varias líneas.*

![Detalle de una venta](img/Detalles_venta.png)
*Figura 19. Detalle de una venta con el beneficio calculado.*

**RF6 — Gestión avanzada de proveedores.**
Alta de proveedores con datos completos (nombre, CIF, contacto, condiciones de pago…).
Asociación de productos a uno o varios proveedores con su precio, y **comparativa de
precios** entre proveedores para un mismo producto. Registro de compras (histórico).

![Ficha de proveedor](img/Detalles_proveedor.png)
*Figura 20. Ficha de un proveedor con los productos que suministra.*

![Comparativa de proveedores](img/Comparativa_proveedores.png)
*Figura 21. Comparativa de precios de un producto entre proveedores.*

**RF7 — Análisis, métricas y visualización.**
Panel de análisis con KPIs (ingresos, coste, beneficio, nº de ventas) filtrables por
rango de fechas, gráficas de evolución de ventas, productos más vendidos, más rentables
y de menor rotación, y una tabla con la **estimación de días hasta agotar stock** según
el ritmo de ventas. Las gráficas se generan en el servidor con Matplotlib.

![Panel de análisis (KPIs y evolución)](img/Analisis_metricas.png)
*Figura 22. Panel de análisis: KPIs y evolución de ventas.*

![Panel de análisis (rankings)](img/Analisis_metricas_2.png)
*Figura 23. Panel de análisis: productos más vendidos, más rentables y de menor rotación.*

![Panel de análisis (días hasta agotar stock)](img/Analisis_metricas_3.png)
*Figura 24. Panel de análisis: estimación de días hasta agotar stock.*

### 5.2. Requisitos no funcionales

- **Usabilidad:** interfaz sencilla, clara e intuitiva (Bootstrap), con navegación por
  menú y mensajes de confirmación de las acciones.
- **Seguridad:** contraseñas con hash, protección CSRF en los formularios y control de
  acceso por rol.
- **Portabilidad y reproducibilidad:** entorno virtual con dependencias fijadas; base de
  datos en un único fichero; sin dependencias externas de internet (Bootstrap y gráficas
  en local).
- **Mantenibilidad:** arquitectura en capas (rutas → servicios → modelos) y código
  organizado en *blueprints* por módulo.

---

## 6. Manual de instalación

### 6.1. Requisitos previos

- **Python 3.13** (o 3.11 o superior). Comprobar con `python --version`.

### 6.2. Instalación desde cero (Windows / PowerShell)

Desde la carpeta del proyecto:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask --app run init-db
flask --app run seed
flask --app run run
```

En Linux/macOS, sustituir la línea de activación por `source .venv/bin/activate`.

La aplicación quedará disponible en **http://localhost:5000**.

> Si PowerShell bloquea la activación del entorno, ejecutar una vez
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, o bien invocar directamente el
> intérprete del entorno: `.venv\Scripts\python.exe run.py`.

- `init-db` crea las tablas de la base de datos (fichero `instance/gestor.sqlite`).
- `seed` carga datos de ejemplo (usuarios, productos, proveedores, ventas y compras).

### 6.3. Usuarios de ejemplo

Tras ejecutar `seed`, se pueden usar estos usuarios (contraseña común: **Demo1234**):

| Email | Rol |
|---|---|
| admin@gestor.com | ADMIN |
| almacen@gestor.com | ALMACEN |
| finanzas@gestor.com | FINANCIERO |

Para crear un administrador propio de forma interactiva:
`flask --app run crear-admin`.

---

## 7. Conclusiones

### 7.1. Conclusiones generales

El proyecto cumple los objetivos planteados: se ha construido una aplicación web
funcional que no solo almacena datos, sino que los transforma en información útil para
la gestión. La arquitectura en capas y la organización en *blueprints* han facilitado
añadir los módulos de forma ordenada, y el diseño del inventario basado en movimientos
como fuente de verdad garantiza la coherencia del stock.

### 7.2. Aprendizajes y experiencias adquiridas

- Diseño de una **base de datos relacional** y su implementación con un **ORM**
  (relaciones, transacciones, integridad).
- Uso de **Flask** con el patrón *application factory*, *blueprints*, autenticación y
  control de acceso por rol.
- Aplicación de **lógica de negocio** no trivial: transacciones atómicas, congelación
  de precios, cálculo de métricas y estimaciones.
- Generación de **gráficas en el servidor** con Matplotlib y su integración en el HTML
  sin JavaScript, reforzando la comunicación backend↔frontend con Python.
- Buenas prácticas de **reproducibilidad**: entorno virtual, dependencias fijadas y
  eliminación de dependencias externas de internet.

---

## 8. Evolutivos del proyecto

Posibles mejoras y ampliaciones para futuros desarrollos:

- **Generación de informes en PDF** y **exportación de datos** (CSV/Excel).
- **Sistema de alertas automáticas** por bajo stock o riesgo de rotura.
- **Predicción básica de ventas** y **simulación de pedidos óptimos** según la demanda
  histórica.
- **Gestión de usuarios desde la interfaz** (además del comando de consola actual).
- **Paginación y búsqueda avanzada** en los listados con muchos registros.
- **Anulación de ventas** con movimientos de inventario compensatorios.
- **Pruebas automatizadas** integradas (por ejemplo, con `pytest`) y despliegue.
