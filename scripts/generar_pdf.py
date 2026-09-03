"""Convierte docs/memoria.md en docs/memoria.html con estilos de impresión.

Uso:
    .venv\\Scripts\\python.exe scripts\\generar_pdf.py

Después, abre docs/memoria.html en el navegador y usa Ctrl+P -> "Guardar como PDF"
(tamaño A4, márgenes normales y activando "Gráficos de fondo").
"""
from pathlib import Path

import markdown

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "docs" / "memoria.md"
SALIDA = RAIZ / "docs" / "memoria.html"

CSS = """
@page { size: A4; margin: 2cm; }
* { box-sizing: border-box; }
html, body { background: #ffffff; }
body {
  font-family: "Segoe UI", Arial, sans-serif;
  font-size: 11pt;
  line-height: 1.5;
  color: #1a1a1a;
  max-width: 900px;
  margin: 0 auto;
  padding: 1cm;
}
h1 { font-size: 24pt; color: #0d3b66; margin: 0 0 .3em; }
h2 { font-size: 17pt; color: #0d3b66; border-bottom: 2px solid #0d3b66;
     padding-bottom: .2em; margin-top: 1.2em; page-break-before: always; }
h3 { font-size: 13pt; color: #14507a; margin-top: 1em; }
h2:first-of-type { page-break-before: avoid; }
p { margin: .5em 0; text-align: justify; }
ul, ol { margin: .4em 0 .8em 1.2em; }
li { margin: .15em 0; }
code { background: #f2f4f7; padding: .1em .3em; border-radius: 3px;
       font-family: Consolas, monospace; font-size: .9em; }
pre { background: #f2f4f7; padding: .8em 1em; border-radius: 6px;
      overflow-x: auto; border: 1px solid #e0e4ea; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: .8em 0;
        font-size: .92em; page-break-inside: avoid; }
th, td { border: 1px solid #cbd2da; padding: .45em .6em; text-align: left;
         vertical-align: top; }
th { background: #0d3b66; color: #fff; }
tr:nth-child(even) td { background: #f6f8fa; }
img { max-width: 100%; height: auto; display: block; margin: .6em auto;
      border: 1px solid #d0d7de; border-radius: 4px; page-break-inside: avoid; }
/* Pies de figura: párrafos que son solo texto en cursiva */
p > em:only-child { display: block; text-align: center; color: #555;
                    font-size: .9em; margin-top: -.2em; margin-bottom: 1em; }
hr { display: none; }
blockquote { border-left: 4px solid #0d3b66; margin: .8em 0; padding: .3em 1em;
             background: #f6f8fa; color: #333; }
a { color: #0d3b66; }
"""


def main():
    texto = ENTRADA.read_text(encoding="utf-8")
    cuerpo = markdown.markdown(
        texto,
        extensions=["tables", "fenced_code", "sane_lists", "nl2br"],
    )
    html = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Memoria - Gestor de Inventario</title>
<style>{CSS}</style>
</head>
<body>
{cuerpo}
</body>
</html>
"""
    SALIDA.write_text(html, encoding="utf-8")
    print(f"Generado: {SALIDA}")


if __name__ == "__main__":
    main()
