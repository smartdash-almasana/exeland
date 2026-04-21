"""Modelos Pydantic para specs, catálogo y configuración."""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class OutputType(str, Enum):
    currency = "currency"
    percentage = "percentage"
    integer = "integer"
    number = "number"
    boolean = "boolean"
    text = "text"


class SheetType(str, Enum):
    welcome = "welcome"
    input = "input"
    engine = "engine"
    dashboard = "dashboard"
    guide = "guide"


class InputType(str, Enum):
    text = "text"
    currency = "currency"
    percentage = "percentage"
    integer = "integer"
    number = "number"
    date = "date"


class Category(str, Enum):
    pricing = "pricing"
    financial = "financial"
    stock = "stock"
    cashflow = "cashflow"


# ---------------------------------------------------------------------------
# Catalog models
# ---------------------------------------------------------------------------

class FormulaDefinition(BaseModel):
    """Define una fórmula reutilizable del catálogo."""
    category: str
    description: str
    inputs: dict[str, str]
    excel_formula: str
    output_type: OutputType
    notes: str = ""


class ValidationDefinition(BaseModel):
    """Define una regla de validación de celda."""
    type: str
    operator: str
    formula1: str
    formula2: str | None = None
    error_title: str = "Valor inválido"
    error_message: str = "El valor ingresado no es válido."
    show_error: bool = True


# ---------------------------------------------------------------------------
# Field / Sheet models (for spec parsing)
# ---------------------------------------------------------------------------

class FieldSpec(BaseModel):
    """Campo de entrada en una hoja de INPUT."""
    id: str
    label: str
    row: int
    col: int
    input_type: InputType = InputType.text
    default: Any = None
    validation: str | None = None
    required: bool = False
    example: str | None = None
    hint: str | None = None


class FormulaBinding(BaseModel):
    """Referencia a una fórmula del catálogo con bindings de parámetros."""
    id: str
    formula_ref: str
    bindings: dict[str, str] = Field(default_factory=dict)
    note: str = ""


class SheetSpec(BaseModel):
    """Definición de una hoja del workbook."""
    name: str
    type: SheetType
    protected: bool = True
    hidden: bool = False
    fields: list[FieldSpec] = Field(default_factory=list)
    formulas: list[FormulaBinding] = Field(default_factory=list)


class BrandingOverride(BaseModel):
    """Overrides de branding por producto (opcionales)."""
    primary_color: str | None = None
    secondary_color: str | None = None
    accent_color: str | None = None


# ---------------------------------------------------------------------------
# Product Spec (top-level)
# ---------------------------------------------------------------------------

class ProductSpec(BaseModel):
    """Spec completa de un producto Excel."""
    slug: str
    title: str
    subtitle: str = ""
    version: str = "1.0.0"
    price_ars: float = 0.0
    category: str = "general"
    branding: BrandingOverride = Field(default_factory=BrandingOverride)
    sheets: list[SheetSpec]
    formulas: list[str] = Field(default_factory=list)

    @field_validator("slug")
    @classmethod
    def slug_no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError("slug no puede contener espacios")
        return v.lower()

    @field_validator("sheets")
    @classmethod
    def at_least_one_sheet(cls, v: list[SheetSpec]) -> list[SheetSpec]:
        if not v:
            raise ValueError("El spec debe tener al menos una hoja")
        return v


# ---------------------------------------------------------------------------
# Product Registry
# ---------------------------------------------------------------------------

class ProductRegistryEntry(BaseModel):
    slug: str
    title: str
    subtitle: str = ""
    version: str = "1.0.0"
    spec_path: str
    category: str
    tags: list[str] = Field(default_factory=list)
    price_ars: float = 0.0
    compatible_with: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Build result
# ---------------------------------------------------------------------------

class BuildResult(BaseModel):
    slug: str
    output_path: str
    success: bool
    error: str | None = None
