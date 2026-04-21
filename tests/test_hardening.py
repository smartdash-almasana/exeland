"""Tests de hardening: validación de bindings incompletos en specs."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from exceland_factory.factory import build_product
from exceland_factory.validators import load_spec
from exceland_factory.workbook_builder import build_workbook


class TestBindingHardening:
    def test_missing_bindings_raises_clear_error(self, tmp_path: Path):
        """Un spec con fórmula sin bindings debe fallar con ValueError claro."""
        spec_file = tmp_path / "broken.yaml"
        spec_file.write_text(
            textwrap.dedent("""\
                slug: broken_test
                title: "Test Roto"
                sheets:
                  - name: DATOS
                    type: input
                    fields:
                      - id: precio
                        label: Precio
                        row: 5
                        col: 2
                  - name: MOTOR
                    type: engine
                    protected: true
                    hidden: true
                    formulas:
                      - id: margen_bruto
                        formula_ref: margen_bruto
                  - name: DASHBOARD
                    type: dashboard
                  - name: GUIA
                    type: guide
            """),
            encoding="utf-8",
        )
        spec = load_spec(spec_file)
        out = tmp_path / "broken.xlsx"
        result = build_workbook(spec, out)

        assert not result.success, "Debería haber fallado con bindings faltantes"
        assert result.error is not None
        assert "margen_bruto" in result.error
        assert "Placeholders requeridos" in result.error or "requiere bindings" in result.error

    def test_partial_bindings_raises_clear_error(self, tmp_path: Path):
        """Un spec con bindings parciales (falta uno) debe fallar con mensaje que indique cuál."""
        spec_file = tmp_path / "partial.yaml"
        spec_file.write_text(
            textwrap.dedent("""\
                slug: partial_test
                title: "Test Parcial"
                sheets:
                  - name: DATOS
                    type: input
                    fields:
                      - id: precio
                        label: Precio
                        row: 5
                        col: 2
                  - name: MOTOR
                    type: engine
                    protected: true
                    hidden: true
                    formulas:
                      - id: margen_bruto
                        formula_ref: margen_bruto
                        bindings:
                          precio_venta: DATOS!C5
                          # costo_unitario ausente a propósito
                  - name: DASHBOARD
                    type: dashboard
                  - name: GUIA
                    type: guide
            """),
            encoding="utf-8",
        )
        spec = load_spec(spec_file)
        out = tmp_path / "partial.xlsx"
        result = build_workbook(spec, out)

        assert not result.success, "Debería haber fallado con binding parcial"
        assert result.error is not None
        assert "costo_unitario" in result.error
        assert "Faltantes" in result.error

    def test_complete_bindings_succeeds(self, tmp_path: Path):
        """Un spec con todos los bindings completos debe buildear sin error."""
        spec_file = tmp_path / "complete.yaml"
        spec_file.write_text(
            textwrap.dedent("""\
                slug: complete_test
                title: "Test Completo"
                sheets:
                  - name: DATOS
                    type: input
                    fields:
                      - id: precio
                        label: Precio
                        row: 5
                        col: 2
                      - id: costo
                        label: Costo
                        row: 6
                        col: 2
                  - name: MOTOR
                    type: engine
                    protected: true
                    hidden: true
                    formulas:
                      - id: margen_bruto
                        formula_ref: margen_bruto
                        bindings:
                          precio_venta: DATOS!C5
                          costo_unitario: DATOS!C6
                  - name: DASHBOARD
                    type: dashboard
                  - name: GUIA
                    type: guide
            """),
            encoding="utf-8",
        )
        spec = load_spec(spec_file)
        out = tmp_path / "complete.xlsx"
        result = build_workbook(spec, out)

        assert result.success, f"Debería haber pasado: {result.error}"
        assert out.exists()

    def test_error_message_contains_spec_slug(self, tmp_path: Path):
        """El mensaje de error debe identificar el spec responsable."""
        spec_file = tmp_path / "slug_test.yaml"
        spec_file.write_text(
            textwrap.dedent("""\
                slug: mi_spec_roto
                title: "Test Slug"
                sheets:
                  - name: DATOS
                    type: input
                    fields:
                      - id: x
                        label: X
                        row: 5
                        col: 2
                  - name: MOTOR
                    type: engine
                    protected: true
                    hidden: true
                    formulas:
                      - id: margen_bruto
                        formula_ref: margen_bruto
                  - name: DASHBOARD
                    type: dashboard
                  - name: GUIA
                    type: guide
            """),
            encoding="utf-8",
        )
        spec = load_spec(spec_file)
        result = build_workbook(spec, tmp_path / "out.xlsx")

        assert not result.success
        assert "mi_spec_roto" in result.error

    def test_all_valid_specs_still_build(self, tmp_path: Path):
        """Los 4 specs válidos deben seguir buildeando sin error tras el hardening."""
        for slug in ["caja_diaria", "precio_margen", "stock_control", "punto_equilibrio"]:
            out = tmp_path / f"{slug}.xlsx"
            result = build_product(slug, out)
            assert result.success, f"Spec válido '{slug}' falló tras hardening: {result.error}"
            assert out.exists()
