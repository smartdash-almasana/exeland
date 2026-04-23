"""Skill: caja_y_flujo — spec legacy mínimo compatible con ProductSpec."""
from exceland_factory.skills.skill_registry import register_skill


def build_caja_flujo_spec() -> dict:
    return {
        "slug": "caja_flujo_skill",
        "title": "Caja y Flujo de Fondos",
        "subtitle": "Control de ingresos, egresos y flujo neto",
        "version": "1.0.0",
        "price_ars": 0,
        "category": "cashflow",
        "sheets": [
            {"name": "BIENVENIDA", "type": "welcome", "protected": True},
            {
                "name": "CAJA",
                "type": "input",
                "protected": False,
                "fields": [
                    {
                        "id": "ingresos",
                        "label": "Ingresos del período",
                        "row": 5,
                        "col": 2,
                        "input_type": "currency",
                        "default": 0,
                        "validation": "non_negative_number",
                    },
                    {
                        "id": "egresos",
                        "label": "Egresos del período",
                        "row": 6,
                        "col": 2,
                        "input_type": "currency",
                        "default": 0,
                        "validation": "non_negative_number",
                    },
                    {
                        "id": "saldo_inicial",
                        "label": "Saldo inicial",
                        "row": 7,
                        "col": 2,
                        "input_type": "currency",
                        "default": 0,
                        "validation": "non_negative_number",
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
                        "id": "flujo_neto",
                        "formula_ref": "flujo_caja_neto",
                        "bindings": {"ingresos": "CAJA!C5", "egresos": "CAJA!C6"},
                    },
                    {
                        "id": "saldo_final",
                        "formula_ref": "saldo_acumulado",
                        "bindings": {"saldo_anterior": "CAJA!C7", "flujo_neto": "MOTOR!C2"},
                    },
                ],
            },
            {"name": "DASHBOARD", "type": "dashboard", "protected": True},
            {"name": "GUIA", "type": "guide", "protected": True},
        ],
        "formulas": ["flujo_caja_neto", "saldo_acumulado"],
    }


register_skill(
    "caja_y_flujo",
    build_caja_flujo_spec,
    meta={
        "name": "Caja y Flujo de Fondos",
        "category": "cashflow",
        "description": "Registrá ingresos y egresos del período y calculá el flujo neto y saldo final.",
        "formulas": ["flujo_caja_neto", "saldo_acumulado"],
        "preview_text": "Ingresás ingresos, egresos y saldo inicial → obtenés flujo neto y saldo final.",
        "use_case": "Ideal para negocios que necesitan controlar su liquidez período a período.",
        "delivery_mode": "plantilla",
        "has_macros": False,
        "quote_required": False,
    },
)
