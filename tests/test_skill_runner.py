"""Tests para la capa skills."""
from __future__ import annotations

from pathlib import Path

import pytest

import exceland_factory.skills  # noqa: F401 — dispara auto-registro
from exceland_factory.skills.skill_registry import get_skill, SKILLS
from exceland_factory.skills.skill_runner import build_from_skill


def test_skill_registered():
    """precios_y_rentabilidad debe estar en el registry tras importar el paquete."""
    assert "precios_y_rentabilidad" in SKILLS


def test_get_skill_returns_callable():
    fn = get_skill("precios_y_rentabilidad")
    assert callable(fn)


def test_get_skill_missing_raises():
    with pytest.raises(KeyError, match="no existe"):
        get_skill("skill_que_no_existe")


def test_skill_fn_returns_valid_dict():
    fn = get_skill("precios_y_rentabilidad")
    spec_dict = fn()
    assert isinstance(spec_dict, dict)
    assert spec_dict["slug"] == "precio_margen_skill"
    assert "sheets" in spec_dict
    assert len(spec_dict["sheets"]) > 0


def test_build_from_skill(tmp_path: Path):
    output = tmp_path / "precio_skill.xlsx"
    result = build_from_skill("precios_y_rentabilidad", output)
    assert result.success, f"Build falló: {result.error}"
    assert output.exists()
    assert output.stat().st_size > 0


# --- caja_y_flujo ---

def test_caja_skill_registered():
    assert "caja_y_flujo" in SKILLS


def test_caja_skill_fn_returns_valid_dict():
    fn = get_skill("caja_y_flujo")
    spec_dict = fn()
    assert isinstance(spec_dict, dict)
    assert spec_dict["slug"] == "caja_flujo_skill"
    assert "sheets" in spec_dict
    assert len(spec_dict["sheets"]) > 0


def test_build_from_skill_caja(tmp_path: Path):
    output = tmp_path / "caja_skill.xlsx"
    result = build_from_skill("caja_y_flujo", output)
    assert result.success, f"Build falló: {result.error}"
    assert output.exists()
    assert output.stat().st_size > 0


# --- conciliador_bancario_macro ---

def test_conciliador_skill_registered():
    assert "conciliador_bancario_macro" in SKILLS


def test_conciliador_skill_meta():
    from exceland_factory.skills.skill_registry import get_skill_meta
    meta = get_skill_meta("conciliador_bancario_macro")
    assert meta["delivery_mode"] == "excel_con_macros"
    assert meta["has_macros"] is True
    assert meta["quote_required"] is False


def test_conciliador_skill_fn_returns_valid_dict():
    fn = get_skill("conciliador_bancario_macro")
    spec_dict = fn()
    assert isinstance(spec_dict, dict)
    assert spec_dict["slug"] == "conciliador_bancario_macro"
    assert "sheets" in spec_dict
    assert len(spec_dict["sheets"]) > 0
    assert "macros" in spec_dict
    assert spec_dict["macros"][0]["name"] == "ConciliarExtracto"


def test_build_from_skill_conciliador(tmp_path: Path):
    output = tmp_path / "conciliador_macro.xlsx"
    result = build_from_skill("conciliador_bancario_macro", output)
    assert result.success, f"Build falló: {result.error}"
    assert output.exists()
    assert output.stat().st_size > 0
