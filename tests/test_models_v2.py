"""Tests de modelos v2: validar estructura sin ejecutar motor."""
from __future__ import annotations

import pytest

from exceland_factory.models import (
    FormulaSpecV2,
    InputSpecV2,
    KpiSpecV2,
    ProductSpec,
    SheetSpec,
    SheetType,
)


class TestInputSpecV2:
    def test_input_spec_v2_minimal(self):
        """InputSpecV2 válido con campos mínimos."""
        inp = InputSpecV2(id="costo_unitario", label="Costo unitario")
        assert inp.id == "costo_unitario"
        assert inp.label == "Costo unitario"
        assert inp.type.value == "text"

    def test_input_spec_v2_with_validation(self):
        """InputSpecV2 con validación."""
        inp = InputSpecV2(
            id="precio",
            label="Precio",
            type="currency",
            validation="positive_number",
            required=True,
        )
        assert inp.validation == "positive_number"
        assert inp.required is True

    def test_input_spec_v2_invalid_id(self):
        """ID con espacios debe fallar."""
        with pytest.raises(ValueError, match="identificador Python válido"):
            InputSpecV2(id="precio venta", label="Precio")

    def test_input_spec_v2_valid_id_with_underscore(self):
        """ID con underscore es válido."""
        inp = InputSpecV2(id="precio_venta", label="Precio de venta")
        assert inp.id == "precio_venta"


class TestFormulaSpecV2:
    def test_formula_spec_v2_minimal(self):
        """FormulaSpecV2 válido con campos mínimos."""
        f = FormulaSpecV2(id="margen", formula="margen_bruto")
        assert f.id == "margen"
        assert f.formula == "margen_bruto"
        assert f.inputs == {}

    def test_formula_spec_v2_with_inputs(self):
        """FormulaSpecV2 con inputs simbólicos."""
        f = FormulaSpecV2(
            id="precio_venta",
            formula="precio_venta_con_margen",
            inputs={"costo_unitario": "costo_unitario", "margen_objetivo": "margen_objetivo"},
        )
        assert f.inputs["costo_unitario"] == "costo_unitario"

    def test_formula_spec_v2_invalid_id(self):
        """ID con caracteres inválidos debe fallar."""
        with pytest.raises(ValueError, match="identificador Python válido"):
            FormulaSpecV2(id="precio-venta", formula="margen_bruto")


class TestKpiSpecV2:
    def test_kpi_spec_v2_minimal(self):
        """KpiSpecV2 válido con campos mínimos."""
        kpi = KpiSpecV2(id="kpi_precio", label="Precio de venta", source="precio_venta")
        assert kpi.id == "kpi_precio"
        assert kpi.source == "precio_venta"
        assert kpi.style == "kpi_neutral"

    def test_kpi_spec_v2_with_style(self):
        """KpiSpecV2 con estilo personalizado."""
        kpi = KpiSpecV2(
            id="kpi_margen",
            label="Margen",
            source="margen",
            style="kpi_positive",
        )
        assert kpi.style == "kpi_positive"


class TestSheetSpecV2Compatibility:
    def test_sheet_spec_accepts_legacy_fields(self):
        """SheetSpec acepta campos legacy (fields, formulas, kpis)."""
        sheet = SheetSpec(
            name="DATOS",
            type=SheetType.input,
            fields=[{"id": "x", "label": "X", "row": 5, "col": 2}],
            formulas=[{"id": "f1", "formula_ref": "margen_bruto"}],
            kpis=[{"label": "KPI", "ref": "MOTOR!C2"}],
        )
        assert len(sheet.fields) == 1
        assert len(sheet.formulas) == 1
        assert len(sheet.kpis) == 1

    def test_sheet_spec_accepts_v2_fields(self):
        """SheetSpec acepta campos v2 (inputs, derived, outputs)."""
        sheet = SheetSpec(
            name="DATOS",
            type=SheetType.input,
            inputs=[{"id": "costo", "label": "Costo"}],
            derived=[{"id": "margen", "formula": "margen_bruto"}],
            outputs=[{"id": "kpi_margen", "label": "Margen", "source": "margen"}],
        )
        assert len(sheet.inputs) == 1
        assert len(sheet.derived) == 1
        assert len(sheet.outputs) == 1

    def test_sheet_spec_accepts_both_legacy_and_v2(self):
        """SheetSpec puede tener ambos contratos simultáneamente."""
        sheet = SheetSpec(
            name="DATOS",
            type=SheetType.input,
            fields=[{"id": "x", "label": "X", "row": 5, "col": 2}],
            inputs=[{"id": "costo", "label": "Costo"}],
        )
        assert len(sheet.fields) == 1
        assert len(sheet.inputs) == 1


class TestProductSpecV2Compatibility:
    def test_product_spec_with_legacy_sheets(self):
        """ProductSpec con hojas legacy funciona."""
        spec = ProductSpec(
            slug="test_legacy",
            title="Test Legacy",
            sheets=[{
                "name": "DATOS",
                "type": "input",
                "fields": [{"id": "x", "label": "X", "row": 5, "col": 2}],
            }],
        )
        assert spec.slug == "test_legacy"
        assert len(spec.sheets[0].fields) == 1

    def test_product_spec_with_v2_sheets(self):
        """ProductSpec con hojas v2 funciona."""
        spec = ProductSpec(
            slug="test_v2",
            title="Test V2",
            sheets=[{
                "name": "DATOS",
                "type": "input",
                "inputs": [{"id": "costo", "label": "Costo", "type": "currency"}],
                "derived": [{"id": "margen", "formula": "margen_bruto"}],
                "outputs": [{"id": "kpi_margen", "label": "Margen", "source": "margen"}],
            }],
        )
        assert spec.slug == "test_v2"
        assert len(spec.sheets[0].inputs) == 1
        assert len(spec.sheets[0].derived) == 1
        assert len(spec.sheets[0].outputs) == 1
