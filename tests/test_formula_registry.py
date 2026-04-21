"""Tests del catálogo de fórmulas y registry."""
from __future__ import annotations

import pytest

from exceland_factory.registry import (
    get_formula,
    get_validation,
    load_formula_catalog,
    load_validation_catalog,
    resolve_formula,
)


class TestLoadFormulaCatalog:
    def test_catalog_loads(self):
        catalog = load_formula_catalog()
        assert isinstance(catalog, dict)
        assert len(catalog) > 0

    def test_required_formulas_present(self):
        catalog = load_formula_catalog()
        required = [
            "margen_bruto",
            "precio_venta_con_margen",
            "punto_equilibrio_unidades",
            "ingresos_totales",
            "egresos_totales",
            "resultado_neto",
            "costo_reposicion_promedio",
            "alerta_stock_minimo",
        ]
        for slug in required:
            assert slug in catalog, f"Fórmula requerida ausente: {slug}"

    def test_formula_has_required_fields(self):
        catalog = load_formula_catalog()
        formula = catalog["margen_bruto"]
        assert formula.category
        assert formula.description
        assert formula.excel_formula
        assert formula.output_type
        assert isinstance(formula.inputs, dict)

    def test_get_formula_returns_correct(self):
        f = get_formula("margen_bruto")
        assert f.category == "pricing"
        assert "{precio_venta}" in f.excel_formula

    def test_get_formula_raises_on_unknown(self):
        with pytest.raises(KeyError, match="no encontrada"):
            get_formula("formula_inexistente_xyz")

    def test_all_formulas_have_valid_output_type(self):
        from exceland_factory.models import OutputType
        catalog = load_formula_catalog()
        valid_types = {t.value for t in OutputType}
        for slug, f in catalog.items():
            assert f.output_type.value in valid_types, (
                f"output_type inválido en '{slug}': {f.output_type}"
            )


class TestResolveFormula:
    def test_resolve_margen_bruto(self):
        result = resolve_formula(
            "margen_bruto",
            {"precio_venta": "C7", "costo_unitario": "C8"},
        )
        assert "C7" in result
        assert "C8" in result
        assert "{" not in result, "Quedaron placeholders sin resolver"

    def test_resolve_punto_equilibrio(self):
        result = resolve_formula(
            "punto_equilibrio_unidades",
            {
                "costos_fijos": "DATOS!C9",
                "precio_venta": "DATOS!C7",
                "costo_variable_unitario": "DATOS!C8",
            },
        )
        assert "DATOS!C9" in result
        assert "{" not in result

    def test_resolve_partial_bindings_keeps_placeholder(self):
        # Si no se pasa un binding, el placeholder queda sin resolver
        result = resolve_formula("margen_bruto", {"precio_venta": "C7"})
        assert "C7" in result
        assert "{costo_unitario}" in result  # el que falta queda como está

    def test_resolve_unknown_formula_raises(self):
        with pytest.raises(KeyError):
            resolve_formula("no_existe", {})


class TestValidationCatalog:
    def test_validation_catalog_loads(self):
        catalog = load_validation_catalog()
        assert isinstance(catalog, dict)
        assert len(catalog) > 0

    def test_required_validations_present(self):
        catalog = load_validation_catalog()
        required = [
            "positive_number",
            "non_negative_number",
            "percentage_0_1",
            "integer_positive",
            "integer_non_negative",
        ]
        for slug in required:
            assert slug in catalog, f"Validación requerida ausente: {slug}"

    def test_get_validation_returns_definition(self):
        v = get_validation("positive_number")
        assert v is not None
        assert v.type == "decimal"
        assert v.operator == "greaterThan"

    def test_get_validation_returns_none_for_unknown(self):
        v = get_validation("validacion_que_no_existe")
        assert v is None
