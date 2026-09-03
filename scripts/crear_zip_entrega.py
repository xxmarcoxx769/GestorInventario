"""Crea el ZIP de entrega del proyecto, limpio y con la estructura original.

Incluye todo el código y la carpeta docs, y EXCLUYE lo que no debe entregarse:
el entorno virtual, las cachés de Python, la base de datos generada, el
repositorio git y la configuración de herramientas.

Uso:
    .venv\\Scripts\\python.exe scripts\\crear_zip_entrega.py

El ZIP se genera en el escritorio (carpeta padre del proyecto) con el nombre
GestorInventario_entrega.zip y dentro cuelga todo de una carpeta GestorInventario/.
"""
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
NOMBRE_CARPETA = RAIZ.name  # GestorInventario
SALIDA = RAIZ.parent / "GestorInventario_entrega.zip"

# Carpetas que se excluyen por completo (en cualquier nivel)
DIRS_EXCLUIDOS = {".venv", "venv", "env", "__pycache__", ".git", ".claude", "instance",
                  ".pytest_cache", ".idea", ".vscode"}
# Ficheros que se excluyen
FICHEROS_EXCLUIDOS = {".env", "GestorInventario_entrega.zip"}
# Extensiones excluidas
EXT_EXCLUIDAS = {".pyc", ".pyo"}


def debe_incluirse(ruta: Path) -> bool:
    partes = set(ruta.relative_to(RAIZ).parts)
    if partes & DIRS_EXCLUIDOS:
        return False
    if ruta.name in FICHEROS_EXCLUIDOS:
        return False
    if ruta.suffix.lower() in EXT_EXCLUIDAS:
        return False
    return True


def main():
    if SALIDA.exists():
        SALIDA.unlink()

    incluidos = []
    with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED) as z:
        for ruta in sorted(RAIZ.rglob("*")):
            if not ruta.is_file():
                continue
            if not debe_incluirse(ruta):
                continue
            arcname = Path(NOMBRE_CARPETA) / ruta.relative_to(RAIZ)
            z.write(ruta, arcname)
            incluidos.append(ruta.relative_to(RAIZ).as_posix())

    tam_mb = SALIDA.stat().st_size / (1024 * 1024)
    print(f"ZIP creado: {SALIDA}")
    print(f"Ficheros incluidos: {len(incluidos)} | Tamaño: {tam_mb:.2f} MB")

    # Comprobaciones útiles
    hay_pdf = any(p.lower().endswith((".pdf", ".docx")) for p in incluidos)
    print()
    print("Comprobaciones:")
    print(f"  - Incluye la memoria en PDF/Word: {'SÍ' if hay_pdf else 'NO (¡añádela!)'}")
    print(f"  - requirements.txt incluido: {'SÍ' if 'requirements.txt' in incluidos else 'NO'}")
    print(f"  - run.py incluido: {'SÍ' if 'run.py' in incluidos else 'NO'}")
    print(f"  - .venv excluido: {'SÍ' if not any('.venv' in p for p in incluidos) else 'NO'}")
    print(f"  - __pycache__ excluido: {'SÍ' if not any('__pycache__' in p for p in incluidos) else 'NO'}")
    print(f"  - instance/ (BD) excluido: {'SÍ' if not any(p.startswith('instance/') for p in incluidos) else 'NO'}")
    if not hay_pdf:
        print()
        print("  AVISO: no se ha encontrado ningún PDF/Word. Genera la memoria en PDF")
        print("         (por ejemplo en docs/) y vuelve a ejecutar este script.")


if __name__ == "__main__":
    main()
