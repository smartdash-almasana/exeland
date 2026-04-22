"""
prepare_static_deploy.py
Copia los artefactos necesarios a dist_static/ para deploy estático.

Estructura generada:
  dist_static/
  ├─ index.html
  ├─ scripts/
  │  └─ products.js
  ├─ assets/
  │  ├─ logo/
  │  ├─ images/
  │  └─ videos/
  └─ warehouse/
     ├─ manifest.json
     └─ templates/
        ├─ caja_diaria.xlsx
        ├─ precio_margen.xlsx
        ├─ stock_control.xlsx
        └─ punto_equilibrio.xlsx

Uso:
  python scripts/prepare_static_deploy.py
  python scripts/prepare_static_deploy.py --clean   # borra dist_static/ antes de copiar

Para probar localmente tras generar:
  python -m http.server 8080 --directory dist_static
  # Abrir: http://localhost:8080
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DIST = REPO_ROOT / "dist_static"

TEMPLATES_SRC = REPO_ROOT / "warehouse" / "templates"


def clean(dist: Path) -> None:
    if dist.exists():
        shutil.rmtree(dist)
        print(f"  🗑  Limpiado: {dist}")


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  ✓  {src.relative_to(REPO_ROOT)}  →  {dst.relative_to(REPO_ROOT)}")


def copy_dir(src: Path, dst: Path) -> None:
    if not src.exists():
        print(f"  ⚠  Directorio no existe, saltando: {src.relative_to(REPO_ROOT)}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, dirs_exist_ok=True)
    print(f"  ✓  {src.relative_to(REPO_ROOT)}/  →  {dst.relative_to(REPO_ROOT)}/")


def verify_sources() -> list[str]:
    """Verifica que todos los archivos fuente existan antes de copiar."""
    errors = []
    required = [
        REPO_ROOT / "web" / "index.html",
        REPO_ROOT / "web" / "scripts" / "products.js",
        REPO_ROOT / "warehouse" / "manifest.json",
    ]
    for path in required:
        if not path.exists():
            errors.append(f"Falta: {path.relative_to(REPO_ROOT)}")

    if not any(TEMPLATES_SRC.glob("*.xlsx")):
        errors.append("No hay archivos .xlsx en warehouse/templates/. Ejecutá publish-all primero.")

    return errors


def build(dist: Path) -> None:
    print(f"\n📦  Generando dist_static en: {dist}\n")

    # 1. index.html
    copy_file(REPO_ROOT / "web" / "index.html", dist / "index.html")

    # 2. scripts/
    copy_dir(REPO_ROOT / "web" / "scripts", dist / "scripts")

    # 3. assets/ (logo, images, videos — pueden estar vacíos)
    copy_dir(REPO_ROOT / "web" / "assets", dist / "assets")

    # 4. warehouse/manifest.json
    copy_file(
        REPO_ROOT / "warehouse" / "manifest.json",
        dist / "warehouse" / "manifest.json",
    )

    # 5. warehouse/templates/ — todos los .xlsx publicados
    templates_dst = dist / "warehouse" / "templates"
    templates_dst.mkdir(parents=True, exist_ok=True)
    for src in sorted(TEMPLATES_SRC.glob("*.xlsx")):
        copy_file(src, templates_dst / src.name)

    print(f"\n✅  dist_static listo en: {dist}")
    print(f"\n▶  Para probar localmente:")
    print(f"   python -m http.server 8080 --directory dist_static")
    print(f"   Abrir: http://localhost:8080\n")


def print_tree(dist: Path) -> None:
    print("\n📁  Estructura generada:\n")
    for path in sorted(dist.rglob("*")):
        rel = path.relative_to(dist)
        depth = len(rel.parts) - 1
        indent = "   " * depth
        icon = "📄" if path.is_file() else "📁"
        size = f"  ({path.stat().st_size:,} bytes)" if path.is_file() else ""
        print(f"  {indent}{icon} {rel.name}{size}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera dist_static para deploy estático.")
    parser.add_argument("--clean", action="store_true", help="Limpiar dist_static/ antes de copiar")
    parser.add_argument("--out", default=str(DIST), help="Directorio de salida (default: dist_static/)")
    args = parser.parse_args()

    dist = Path(args.out)

    # Verificar fuentes
    errors = verify_sources()
    if errors:
        print("❌  Errores antes de copiar:")
        for e in errors:
            print(f"   • {e}")
        print("\nEjecutá primero: python -m exceland_factory publish-all")
        sys.exit(1)

    if args.clean:
        clean(dist)

    build(dist)
    print_tree(dist)


if __name__ == "__main__":
    main()
