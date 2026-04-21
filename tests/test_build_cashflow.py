"""Tests de build del workbook caja_diaria."""
from __future__ import annotations

from pathlib import Path

import pytest

from exceland_factory.config import SPECS_DIR
from exceland_factory.factory import build_product
from exceland_factory.validators import load_spec
from exceland_factory.workbook_builder import build_workbook


class TestBuildCashflow:
    def test_build_caja_diaria_success(self, tmp_path: Path):
        out = tmp_path / "caja_diaria.xlsx"
        result = build_product("caja_diaria", out)
        assert result.success, f"Build falló: {result.error}"
        assert Path(result.output_path).exists()

    def test_output_file_is_xlsx(self, tmp_path: Path):
        out = tmp_path / "test.xlsx"
        result = build_product("caja_diaria", out)
        assert result.success
        assert result.output_path.endswith(".xlsx")

    def test_output_file_has_content(self, tmp_path: Path):
        out = tmp_path / "caja_diaria.xlsx"
        build_product("caja_diaria", out)
        assert out.stat().st_size > 5000, "El archivo parece demasiado pequeño"

    def test_build_returns_correct_slug(self, tmp_path: Path):
        out = tmp_path / "caja_diaria.xlsx"
        result = build_product("caja_diaria", out)
        assert result.slug == "caja_diaria"

    def test_build_via_spec_path(self, tmp_path: Path):
        spec_path = SPECS_DIR / "caja_diaria.yaml"
        out = tmp_path / "caja_diaria_path.xlsx"
        result = build_product(str(spec_path), out)
        assert result.success

    def test_build_workbook_directly(self, tmp_path: Path):
        spec = load_spec(SPECS_DIR / "caja_diaria.yaml")
        out = tmp_path / "direct.xlsx"
        result = build_workbook(spec, out)
        assert result.success
        assert out.exists()

    def test_build_creates_all_sheets(self, tmp_path: Path):
        """Verifica que el xlsx tenga las hojas correctas con openpyxl."""
        from openpyxl import load_workbook as oxl_load
        out = tmp_path / "caja_diaria.xlsx"
        build_product("caja_diaria", out)
        wb = oxl_load(str(out))
        sheet_names = wb.sheetnames
        assert "BIENVENIDA" in sheet_names
        assert "CAJA" in sheet_names
        assert "DASHBOARD" in sheet_names
        assert "GUIA" in sheet_names

    def test_result_has_output_path(self, tmp_path: Path):
        out = tmp_path / "caja_diaria.xlsx"
        result = build_product("caja_diaria", out)
        assert result.output_path is not None

    def test_error_on_bad_spec_path(self, tmp_path: Path):
        out = tmp_path / "bad.xlsx"
        result = build_product("spec_que_no_existe_xyz", out)
        assert not result.success
        assert result.error is not None
