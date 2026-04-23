"""
export_skills_catalog.py
Exporta el catálogo de skills registradas a web/skills_catalog.json.

Uso:
    python scripts/export_skills_catalog.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Asegurar que el paquete sea importable desde la raíz del repo
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import exceland_factory.skills  # noqa: F401 — dispara auto-registro
from exceland_factory.skills.skill_registry import list_skills

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = REPO_ROOT / "web" / "skills_catalog.json"


def main() -> None:
    catalog = list_skills()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    print(f"✅  {len(catalog)} skills exportadas → {OUTPUT.relative_to(REPO_ROOT)}")
    for skill in catalog:
        print(f"   • {skill['name']} ({skill['category']})")


if __name__ == "__main__":
    main()
