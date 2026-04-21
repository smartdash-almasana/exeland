# Exceland Factory 🏭

Factoría semiautomática que genera plantillas Excel comerciales desde specs YAML.

**Stack:** `xlsxwriter` · `openpyxl` · `pydantic` · `typer` · `pytest`

---

## Instalación

```bash
# 1. Clonar y entrar al repo
cd exceland-factory

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 3. Instalar en modo desarrollo
pip install -e ".[dev]"

# O con requirements.txt
pip install -r requirements.txt
pip install -e .
```

---

## Comandos CLI

### Construir un producto
```bash
python -m exceland_factory build --spec specs/caja_diaria.yaml --output dist/caja_diaria.xlsx
```

### Construir todos los productos
```bash
python -m exceland_factory build-all
# Con directorio personalizado:
python -m exceland_factory build-all --output-dir dist/
```

### Validar un spec sin generar
```bash
python -m exceland_factory validate-spec --spec specs/caja_diaria.yaml
```

### Listar productos disponibles
```bash
python -m exceland_factory list
```

### Usando el script entry point (si instalaste con pip)
```bash
exceland build --spec specs/caja_diaria.yaml
exceland build-all
```

---

## Estructura del repo

```
exceland-factory/
├─ README.md
├─ pyproject.toml
├─ requirements.txt
├─ specs/                          # Un YAML por producto
│  ├─ caja_diaria.yaml
│  ├─ precio_margen.yaml
│  ├─ stock_control.yaml
│  └─ punto_equilibrio.yaml
├─ catalog/
│  ├─ formulas.yaml                # Catálogo canónico de fórmulas Excel
│  ├─ validations.yaml             # Reglas de validación de celdas
│  └─ product_registry.yaml        # Registro de productos disponibles
├─ assets/
│  └─ brand.json                   # Paleta de colores, tipografía, protección
├─ dist/                           # Archivos .xlsx generados (gitignored)
├─ tests/
│  ├─ conftest.py
│  ├─ test_formula_registry.py
│  ├─ test_spec_validation.py
│  ├─ test_build_cashflow.py
│  └─ test_build_all.py
└─ src/
   └─ exceland_factory/
      ├─ cli.py                    # CLI Typer
      ├─ config.py                 # Paths globales
      ├─ factory.py                # build_product / build_all_products
      ├─ workbook_builder.py       # Orquestador xlsxwriter
      ├─ style_system.py           # StyleBook centralizado
      ├─ models.py                 # Pydantic models
      ├─ registry.py               # Carga de catálogos
      ├─ validators.py             # Parser/validador de specs
      ├─ postprocess.py            # DataValidation con openpyxl
      ├─ protection.py             # Config de protección
      ├─ formulas/                 # Helpers Python puros
      ├─ layouts/                  # Builders de hojas
      └─ templates/                # Builder por producto
```

---

## Ejecutar tests

```bash
pytest                          # todos los tests
pytest -v                       # verbose
pytest tests/test_formula_registry.py   # un archivo
pytest --tb=short               # traceback corto
pytest --cov=exceland_factory   # con cobertura
```

---

## Cómo agregar una nueva fórmula

1. **Editar `catalog/formulas.yaml`** y agregar la entrada:

```yaml
formulas:
  mi_nueva_formula:
    category: financial         # pricing | financial | stock | cashflow
    description: "Descripción clara de qué calcula"
    inputs:
      variable_a: "Descripción de variable A"
      variable_b: "Descripción de variable B"
    excel_formula: "={variable_a}*{variable_b}"
    output_type: currency       # currency | percentage | integer | number | boolean | text
    notes: "Condiciones o advertencias opcionales"
```

2. **Opcionalmente**, agregar el helper Python en `src/exceland_factory/formulas/financial.py` (o el módulo correspondiente).

3. **Referenciarla en un spec YAML** bajo `sheets[].formulas[].formula_ref`.

4. Listo — no hay que tocar ningún otro archivo.

---

## Cómo crear un nuevo producto por YAML

1. **Crear `specs/mi_producto.yaml`**:

```yaml
slug: mi_producto
title: "Mi Producto"
subtitle: "Descripción breve"
version: "1.0.0"
price_ars: 4900
category: financial

branding:
  primary_color: "#1A3C5E"      # opcional, hereda de brand.json

sheets:
  - name: BIENVENIDA
    type: welcome
    protected: true

  - name: DATOS
    type: input
    protected: false
    fields:
      - id: mi_campo
        label: "Mi campo"
        row: 5
        col: 2
        input_type: currency    # text | currency | percentage | integer | number
        default: 0
        validation: positive_number   # ver catalog/validations.yaml
        required: true

  - name: MOTOR
    type: engine
    protected: true
    hidden: true
    formulas:
      - id: resultado
        formula_ref: resultado_neto   # debe existir en catalog/formulas.yaml
        bindings:
          ingresos_totales: DATOS!C5
          egresos_totales: DATOS!C6

  - name: DASHBOARD
    type: dashboard
    protected: true

  - name: GUIA
    type: guide
    protected: true

formulas:
  - resultado_neto
```

2. **Registrar en `catalog/product_registry.yaml`**:

```yaml
products:
  mi_producto:
    slug: mi_producto
    title: "Mi Producto"
    subtitle: "Descripción"
    version: "1.0.0"
    spec_path: "specs/mi_producto.yaml"
    category: financial
    tags: [tag1, tag2]
    price_ars: 4900
    compatible_with: [excel, google_sheets]
```

3. **Construir**:

```bash
python -m exceland_factory build --spec specs/mi_producto.yaml
# o tras registrar:
python -m exceland_factory build-all
```

---

## Diseño / Brand

Todos los estilos están en:
- **`assets/brand.json`** — paleta, tipografía, contraseña de protección
- **`src/exceland_factory/style_system.py`** — construye el `StyleBook` con todos los formats de xlsxwriter

Para cambiar colores o tipografía: editar `brand.json` únicamente. No tocar los templates.

**Contraseña por defecto de protección:** `exceland2025`

---

## Compatibilidad

| Feature | Excel | Google Sheets |
|---|---|---|
| Fórmulas | ✅ | ✅ |
| Protección de hojas | ✅ | ✅ parcial |
| Validación de datos | ✅ | ✅ |
| Hojas ocultas (MOTOR) | ✅ | ✅ |
| Macros VBA | ❌ No usamos | — |
