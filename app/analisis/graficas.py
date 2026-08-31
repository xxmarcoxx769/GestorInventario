"""Generación de gráficas en el servidor con Matplotlib.

Se usa la API orientada a objetos (Figure + FigureCanvasAgg), que es segura en
un servidor web (no depende del estado global de pyplot ni de una GUI). Cada
figura se serializa a PNG en memoria y se devuelve como data URI base64, listo
para inyectar en un <img> de la plantilla. No interviene JavaScript.
"""
import base64
import io

from matplotlib.figure import Figure

COLOR_PRIMARIO = "#0d6efd"
COLOR_EXITO = "#198754"
COLOR_AVISO = "#fd7e14"


def _figura_a_datauri(fig) -> str:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
    buffer.seek(0)
    datos = base64.b64encode(buffer.read()).decode("ascii")
    return f"data:image/png;base64,{datos}"


def barras_horizontal(etiquetas, valores, titulo, color=COLOR_PRIMARIO, sufijo=""):
    """Gráfica de barras horizontales (ideal para rankings con nombres largos)."""
    if not etiquetas:
        return None
    fig = Figure(figsize=(6.2, 3.6))
    ax = fig.subplots()
    posiciones = range(len(etiquetas))
    barras = ax.barh(list(posiciones), [float(v) for v in valores], color=color)
    ax.set_yticks(list(posiciones))
    ax.set_yticklabels(etiquetas, fontsize=9)
    ax.invert_yaxis()  # el mayor arriba
    ax.set_title(titulo, fontsize=11, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for barra, valor in zip(barras, valores):
        ax.text(barra.get_width(), barra.get_y() + barra.get_height() / 2,
                f" {float(valor):.0f}{sufijo}", va="center", fontsize=9)
    fig.tight_layout()
    return _figura_a_datauri(fig)


def linea_temporal(etiquetas, valores, titulo, color=COLOR_PRIMARIO):
    """Gráfica de línea para la evolución temporal de ventas."""
    if not etiquetas:
        return None
    fig = Figure(figsize=(9.5, 3.2))
    ax = fig.subplots()
    x = list(range(len(etiquetas)))
    y = [float(v) for v in valores]
    ax.plot(x, y, marker="o", color=color, linewidth=2)
    ax.fill_between(x, y, alpha=0.1, color=color)
    ax.set_title(titulo, fontsize=11, fontweight="bold")
    ax.set_ylabel("€")
    ax.set_ylim(bottom=0)
    ax.margins(x=0.02)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    # Mostrar como máximo ~12 etiquetas en el eje X para evitar solapes
    paso = max(1, len(etiquetas) // 12)
    posiciones = x[::paso]
    ax.set_xticks(posiciones)
    ax.set_xticklabels([etiquetas[i] for i in posiciones], rotation=45, ha="right", fontsize=8)
    fig.tight_layout()
    return _figura_a_datauri(fig)
