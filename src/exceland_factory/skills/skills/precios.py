"""Skill: precios_y_rentabilidad — spec legacy mínimo compatible con ProductSpec."""
from exceland_factory.skills.skill_registry import register_skill


def build_precio_margen_spec() -> dict:
    return {
        "slug": "precio_margen_skill",
        "title": "Precio con Margen",
        "subtitle": "Calculá el precio ideal con margen controlado",
        "version": "1.0.0",
        "price_ars": 0,
        "category": "pricing",
        "sheets": [
            {"name": "BIENVENIDA", "type": "welcome", "protected": True},
            {
                "name": "INPUT",
                "type": "input",
                "protected": False,
                "fields": [
                    {
                        "id": "costo",
                        "label": "Costo del producto",
                        "row": 5,
                        "col": 2,
                        "input_type": "currency",
                        "default": 0,
                        "validation": "non_negative_number",
                    },
                    {
                        "id": "margen",
                        "label": "Margen deseado (0 a 1)",
                        "row": 6,
                        "col": 2,
                        "input_type": "percentage",
                        "default": 0,
                        "validation": "percentage_0_1",
                    },
                ],
            },
            {
                "name": "MOTOR",
                "type": "engine",
                "protected": True,
                "hidden": True,
                "formulas": [
                    {
                        "id": "precio_final",
                        "formula_ref": "precio_con_margen",
                        "bindings": {"costo": "INPUT!C5", "margen": "INPUT!C6"},
                    }
                ],
            },
            {"name": "DASHBOARD", "type": "dashboard", "protected": True},
            {"name": "GUIA", "type": "guide", "protected": True},
        ],
        "formulas": ["precio_con_margen"],
    }


register_skill(
    "precios_y_rentabilidad",
    build_precio_margen_spec,
    meta={
        "name": "Precios y Rentabilidad",
        "category": "pricing",
        "description": "Calculá el precio de venta ideal a partir del costo y margen deseado.",
        "formulas": ["precio_con_margen"],
        "preview_text": "Ingresás costo y margen → obtenés el precio de venta óptimo.",
        "use_case": "Ideal para negocios que quieren fijar precios con margen controlado.",
        "delivery_mode": "plantilla",
        "has_macros": False,
        "quote_required": False,
    },
)
