from exceland_factory.skills.skill_registry import register_skill


def build_conciliador_spec() -> dict:
    return {
        "slug": "conciliador_macro",
        "title": "Conciliador Bancario (Macro)",
        "subtitle": "Cruzar movimientos automáticamente",
        "version": "1.0.0",
        "price_ars": 0,
        "category": "finanzas",
        "sheets": [
            {"name": "BIENVENIDA", "type": "welcome", "protected": True},
            {
                "name": "MOVIMIENTOS",
                "type": "input",
                "protected": False,
                "fields": [
                    {"id": "fecha", "label": "Fecha", "row": 5, "col": 2, "input_type": "text"},
                    {"id": "monto", "label": "Monto", "row": 6, "col": 2, "input_type": "currency"},
                ],
            },
            {
                "name": "BANCO",
                "type": "input",
                "protected": False,
                "fields": [
                    {"id": "fecha_banco", "label": "Fecha banco", "row": 5, "col": 5, "input_type": "text"},
                    {"id": "monto_banco", "label": "Monto banco", "row": 6, "col": 5, "input_type": "currency"},
                ],
            },
            {"name": "RESULTADO", "type": "dashboard", "protected": True},
        ],
        "formulas": [],
    }


register_skill(
    "conciliador_bancario_macro",
    build_conciliador_spec,
    meta={
        "name": "Conciliador Bancario",
        "category": "finanzas",
        "description": "Cruza movimientos internos contra extracto bancario.",
        "formulas": [],
        "preview_text": "Comparás movimientos vs banco y detectás diferencias.",
        "use_case": "Ideal para conciliación bancaria manual o semi automática.",
        "delivery_mode": "excel_con_macros",
        "has_macros": True,
        "quote_required": False,
    },
)
