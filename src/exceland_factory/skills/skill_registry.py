from typing import Callable

SKILLS: dict[str, dict] = {}


def register_skill(name: str, fn: Callable, meta: dict | None = None) -> None:
    SKILLS[name] = {"fn": fn, "meta": meta or {}}


def get_skill(name: str) -> Callable:
    if name not in SKILLS:
        raise KeyError(f"Skill '{name}' no existe")
    return SKILLS[name]["fn"]


def get_skill_meta(name: str) -> dict:
    if name not in SKILLS:
        raise KeyError(f"Skill '{name}' no existe")
    return SKILLS[name]["meta"]


def list_skills() -> list[dict]:
    result = []
    for name, data in SKILLS.items():
        meta = data.get("meta", {})
        result.append({
            "name": name,
            "category": meta.get("category", ""),
            "description": meta.get("description", ""),
            "formulas": meta.get("formulas", []),
            "preview_text": meta.get("preview_text", ""),
            "use_case": meta.get("use_case", ""),
            "delivery_mode": meta.get("delivery_mode", "plantilla"),
            "has_macros": meta.get("has_macros", False),
            "quote_required": meta.get("quote_required", False),
        })
    return result
