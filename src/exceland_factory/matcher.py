"""
Matcher: mapea un ParsedPrompt a un intent y a la configuración de template.
Sin LLM — reglas de keywords + scoring por categoría.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from exceland_factory.nl_parser import ParsedPrompt


# ---------------------------------------------------------------------------
# Intent definitions
# ---------------------------------------------------------------------------

@dataclass
class IntentConfig:
    """Configuración completa de un intent reconocido."""
    intent: str                          # slug del intent
    title: str                           # título sugerido para el producto
    subtitle: str                        # subtítulo sugerido
    category: str                        # categoría del catálogo
    input_sheet_name: str                # nombre de la hoja de input
    tags: list[str] = field(default_factory=list)
    formulas: list[str] = field(default_factory=list)   # formula_refs del catálogo
    kpi_refs: list[tuple[str, str]] = field(default_factory=list)  # (label, MOTOR!Cx)
    price_ars: float = 0.0
    confidence: float = 0.0              # score de matching (0–1)


# ---------------------------------------------------------------------------
# Keyword maps por intent
# ---------------------------------------------------------------------------

_INTENT_KEYWORDS: dict[str, list[str]] = {
    "caja": [
        "caja", "flujo", "ingresos", "egresos", "efectivo", "dinero",
        "cobros", "pagos", "gastos", "entradas", "salidas", "saldo",
        "diario", "diaria", "movimientos", "tesoreria", "liquidez",
        "ganando", "ganancia", "perdiendo", "perdida", "resultado",
        "plata", "guita", "billetera",
    ],
    "precios": [
        "precio", "precios", "margen", "costo", "costos", "markup",
        "ganancia", "rentabilidad", "venta", "vender", "cobrar",
        "descuento", "descuentos", "competencia", "mercado",
        "cuanto cobrar", "cuanto vender", "precio ideal",
        "poner precio", "fijar precio",
    ],
    "stock": [
        "stock", "inventario", "mercaderia", "productos", "unidades",
        "reponer", "reposicion", "alerta", "alertas", "minimo",
        "rotacion", "dias", "agotado", "faltante", "deposito",
        "almacen", "bodega", "existencias", "controlar stock",
        "cuando reponer", "cuanto tengo",
    ],
    "punto_equilibrio": [
        "equilibrio", "break even", "breakeven", "cubrir costos",
        "costos fijos", "cuanto vender", "minimo vender",
        "no perder", "no perdo", "cubrir gastos", "punto critico",
        "umbral", "rentable", "cuando soy rentable",
        "cuantas unidades", "ventas minimas",
    ],
}

# Pesos extra para frases compuestas (boost de score)
_PHRASE_BOOSTS: dict[str, list[str]] = {
    "caja": ["flujo de caja", "caja diaria", "estoy ganando", "estoy perdiendo"],
    "precios": ["precio ideal", "cuanto cobrar", "fijar precio", "poner precio"],
    "stock": ["controlar stock", "cuando reponer", "nivel de stock"],
    "punto_equilibrio": ["punto de equilibrio", "break even", "cubrir costos", "no perder plata"],
}


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _score_intent(parsed: ParsedPrompt, intent: str) -> float:
    """
    Calcula score de matching entre el prompt y un intent.
    Retorna valor entre 0.0 y 1.0.
    """
    keywords = _INTENT_KEYWORDS[intent]
    phrases = _PHRASE_BOOSTS.get(intent, [])

    score = 0.0
    total_possible = len(keywords) + len(phrases) * 2

    # Score por keywords individuales
    for kw in keywords:
        if parsed.contains(kw):
            score += 1.0

    # Boost por frases compuestas (valen doble)
    for phrase in phrases:
        if parsed.contains(phrase):
            score += 2.0

    return min(score / max(total_possible * 0.15, 1.0), 1.0)


# ---------------------------------------------------------------------------
# Intent templates
# ---------------------------------------------------------------------------

def _build_intent_config(intent: str, confidence: float) -> IntentConfig:
    """Construye la IntentConfig completa para un intent dado."""

    configs: dict[str, dict] = {
        "caja": {
            "title": "Caja Diaria",
            "subtitle": "Control de ingresos y egresos de tu negocio",
            "category": "cashflow",
            "input_sheet_name": "CAJA",
            "tags": ["caja", "flujo", "ingresos", "egresos", "resultado"],
            "formulas": ["ingresos_totales", "egresos_totales", "flujo_caja_neto", "saldo_acumulado"],
            "kpi_refs": [
                ("Ingresos totales", "MOTOR!C2"),
                ("Egresos totales", "MOTOR!C3"),
                ("Flujo neto", "MOTOR!C4"),
                ("Saldo acumulado", "MOTOR!C5"),
            ],
            "price_ars": 4900.0,
        },
        "precios": {
            "title": "Calculadora de Precios",
            "subtitle": "Determiná el precio ideal con margen controlado",
            "category": "pricing",
            "input_sheet_name": "DATOS",
            "tags": ["precio", "margen", "costo", "markup", "rentabilidad"],
            "formulas": ["precio_venta_con_margen", "margen_bruto", "margen_bruto_pesos", "markup"],
            "kpi_refs": [
                ("Precio sugerido", "MOTOR!C2"),
                ("Margen bruto %", "MOTOR!C3"),
                ("Margen en $", "MOTOR!C4"),
                ("Markup", "MOTOR!C5"),
            ],
            "price_ars": 3900.0,
        },
        "stock": {
            "title": "Control de Stock",
            "subtitle": "Inventario, alertas y rotación para tu negocio",
            "category": "stock",
            "input_sheet_name": "STOCK",
            "tags": ["stock", "inventario", "reposicion", "alertas", "rotacion"],
            "formulas": [
                "alerta_stock_minimo", "dias_stock_restante",
                "costo_reposicion_promedio", "rotacion_inventario",
            ],
            "kpi_refs": [
                ("Alerta stock mínimo", "MOTOR!C2"),
                ("Días de stock restante", "MOTOR!C3"),
                ("Costo reposición promedio", "MOTOR!C4"),
                ("Rotación inventario", "MOTOR!C5"),
            ],
            "price_ars": 4500.0,
        },
        "punto_equilibrio": {
            "title": "Punto de Equilibrio",
            "subtitle": "Cuánto tenés que vender para no perder",
            "category": "financial",
            "input_sheet_name": "DATOS",
            "tags": ["punto_equilibrio", "break_even", "costos_fijos", "rentabilidad"],
            "formulas": [
                "punto_equilibrio_unidades", "punto_equilibrio_pesos",
                "margen_bruto", "resultado_neto",
            ],
            "kpi_refs": [
                ("Punto equilibrio (uds)", "MOTOR!C2"),
                ("Margen bruto %", "MOTOR!C3"),
                ("Punto equilibrio ($)", "MOTOR!C4"),
                ("Resultado neto", "MOTOR!C5"),
            ],
            "price_ars": 3500.0,
        },
    }

    cfg = configs[intent]
    return IntentConfig(
        intent=intent,
        confidence=confidence,
        **cfg,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class MatchResult:
    """Resultado del matching de un prompt."""

    def __init__(
        self,
        matched: bool,
        primary: IntentConfig | None = None,
        alternatives: list[IntentConfig] | None = None,
        raw_scores: dict[str, float] | None = None,
    ) -> None:
        self.matched = matched
        self.primary = primary
        self.alternatives = alternatives or []
        self.raw_scores = raw_scores or {}

    def __repr__(self) -> str:
        if self.matched and self.primary:
            return f"MatchResult(intent={self.primary.intent}, confidence={self.primary.confidence:.2f})"
        return "MatchResult(matched=False)"


_MIN_CONFIDENCE = 0.10   # umbral mínimo para considerar un match


def match_intent(prompt: str) -> MatchResult:
    """
    Analiza un prompt y retorna el intent más probable con su configuración.

    Returns:
        MatchResult con primary (mejor match) y alternatives (otros candidatos).
    """
    parsed = ParsedPrompt(prompt)

    scores: dict[str, float] = {
        intent: _score_intent(parsed, intent)
        for intent in _INTENT_KEYWORDS
    }

    # Ordenar por score descendente
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_intent, best_score = ranked[0]

    if best_score < _MIN_CONFIDENCE:
        return MatchResult(matched=False, raw_scores=scores)

    primary = _build_intent_config(best_intent, best_score)

    # Alternativas: otros intents con score > 0 (excluyendo el primero)
    alternatives = [
        _build_intent_config(intent, score)
        for intent, score in ranked[1:]
        if score > 0
    ]

    return MatchResult(
        matched=True,
        primary=primary,
        alternatives=alternatives,
        raw_scores=scores,
    )
