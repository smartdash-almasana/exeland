"""Tests de validación de specs YAML."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

from exceland_factory.models import ProductSpec, SheetType
from exceland_factory.validators import load_spec, validate_spec


SPECS_DIR = Path(__file__).resolve().parents[1] / "specs"


class TestLoadSpec:
    def test_load_caja_diaria(self):
        spec = load_spec(SPECS_DIR / "caja_diaria.yaml")
        assert spec.slug == "caja_diaria"
        assert spec.title
        assert len(spec.sheets) > 0

    def test_load_precio_margen(self):
        spec = load_spec(SPECS_DIR / "precio_margen.yaml")
        assert spec.slug == "precio_margen"

    def test_load_stock_control(self):
        spec = load_spec(SPECS_DIR / "stock_control.yaml")
        assert spec.slug == "stock_control"

    def test_load_punto_equilibrio(self):
        spec = load_spec(SPECS_DIR / "punto_equilibrio.yaml")
        assert spec.slug == "punto_equilibrio"

    def test_raises_on_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_spec(SPECS_DIR / "no_existe.yaml")

    def test_all_specs_have_valid_sheet_types(self):
        valid_types = {t.value for t in SheetType}
        for yaml_file in SPECS_DIR.glob("*.yaml"):
            spec = load_spec(yaml_file)
            for sheet in spec.sheets:
                assert sheet.type.value in valid_types, (
                    f"Tipo de hoja inválido '{sheet.type}' en {yaml_file.name}"
                )

    def test_spec_has_at_least_one_input_sheet(self):
        for yaml_file in SPECS_DIR.glob("*.yaml"):
            spec = load_spec(yaml_file)
            sheet_types = [s.type for s in spec.sheets]
            assert SheetType.input in sheet_types or SheetType.welcome in sheet_types, (
                f"{yaml_file.name} no tiene hoja de input ni bienvenida"
            )


class TestValidateSpec:
    def test_valid_spec_returns_empty_errors(self):
        errors = validate_spec(SPECS_DIR / "caja_diaria.yaml")
        assert errors == []

    def test_missing_file_returns_error(self):
        errors = validate_spec(SPECS_DIR / "no_existe.yaml")
        assert len(errors) == 1
        assert "no encontrado" in errors[0].lower() or "no existe" in errors[0].lower()

    def test_invalid_yaml_returns_error(self, tmp_path: Path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("slug: [this is: bad yaml: {\n", encoding="utf-8")
        errors = validate_spec(bad)
        assert len(errors) > 0

    def test_missing_required_fields_returns_error(self, tmp_path: Path):
        # Spec sin 'sheets' — campo requerido
        minimal = tmp_path / "minimal.yaml"
        minimal.write_text(
            textwrap.dedent("""\
                slug: sin_hojas
                title: "Sin hojas"
            """),
            encoding="utf-8",
        )
        errors = validate_spec(minimal)
        assert len(errors) > 0

    def test_slug_no_spaces(self, tmp_path: Path):
        bad_slug = tmp_path / "bad_slug.yaml"
        bad_slug.write_text(
            textwrap.dedent("""\
                slug: "slug con espacios"
                title: "Test"
                sheets:
                  - name: DATOS
                    type: input
            """),
            encoding="utf-8",
        )
        errors = validate_spec(bad_slug)
        assert len(errors) > 0


class TestProductSpecModel:
    def test_parse_minimal_valid_spec(self):
        raw = {
            "slug": "test_minimal",
            "title": "Test",
            "sheets": [{"name": "DATOS", "type": "input"}],
        }
        spec = ProductSpec.model_validate(raw)
        assert spec.slug == "test_minimal"
        assert len(spec.sheets) == 1
        assert spec.price_ars == 0.0

    def test_branding_defaults(self):
        raw = {
            "slug": "test_brand",
            "title": "Test",
            "sheets": [{"name": "DATOS", "type": "input"}],
        }
        spec = ProductSpec.model_validate(raw)
        assert spec.branding.primary_color is None  # defaults a None

    def test_fields_parsed_correctly(self):
        raw = {
            "slug": "test_fields",
            "title": "Test",
            "sheets": [
                {
                    "name": "DATOS",
                    "type": "input",
                    "fields": [
                        {
                            "id": "costo",
                            "label": "Costo",
                            "row": 5,
                            "col": 2,
                            "input_type": "currency",
                            "required": True,
                        }
                    ],
                }
            ],
        }
        spec = ProductSpec.model_validate(raw)
        field = spec.sheets[0].fields[0]
        assert field.id == "costo"
        assert field.required is True
