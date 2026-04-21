"""CLI de Exceland Factory usando Typer."""
from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from exceland_factory.factory import build_all_products, build_product
from exceland_factory.registry import list_products
from exceland_factory.validators import validate_spec
from exceland_factory.warehouse import list_published, publish_all_products, publish_product

app = typer.Typer(
    name="exceland",
    help="🏭  Exceland Factory — generador de plantillas Excel comerciales",
    no_args_is_help=True,
)
console = Console()


@app.command("build")
def cmd_build(
    spec: Path = typer.Option(..., "--spec", "-s", help="Path al archivo YAML de spec"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Path de salida .xlsx"),
) -> None:
    """Construye un único producto Excel desde un spec YAML."""
    console.print(f"[bold cyan]⚙  Construyendo:[/] {spec}")

    result = build_product(str(spec), output)

    if result.success:
        console.print(f"[bold green]✅  Generado:[/] {result.output_path}")
    else:
        console.print(f"[bold red]❌  Error:[/] {result.error}")
        raise typer.Exit(code=1)


@app.command("build-all")
def cmd_build_all(
    output_dir: Path | None = typer.Option(None, "--output-dir", "-d", help="Directorio de salida"),
) -> None:
    """Construye todos los productos registrados en product_registry.yaml."""
    console.print("[bold cyan]⚙  Construyendo todos los productos...[/]")

    results = build_all_products(output_dir)

    table = Table(title="Resultados", show_header=True, header_style="bold magenta")
    table.add_column("Slug", style="cyan")
    table.add_column("Estado", justify="center")
    table.add_column("Path")
    table.add_column("Error")

    ok = 0
    fail = 0
    for r in results:
        status = "[green]✅ OK[/]" if r.success else "[red]❌ FAIL[/]"
        table.add_row(r.slug, status, r.output_path, r.error or "")
        if r.success:
            ok += 1
        else:
            fail += 1

    console.print(table)
    console.print(f"\n[bold]Total:[/] {ok} OK, {fail} con error")

    if fail > 0:
        raise typer.Exit(code=1)


@app.command("validate-spec")
def cmd_validate_spec(
    spec: Path = typer.Option(..., "--spec", "-s", help="Path al archivo YAML de spec"),
) -> None:
    """Valida un spec YAML sin generar el archivo."""
    console.print(f"[bold cyan]🔍  Validando:[/] {spec}")
    errors = validate_spec(spec)

    if not errors:
        console.print("[bold green]✅  Spec válido.[/]")
    else:
        for err in errors:
            console.print(f"[bold red]❌[/]  {err}")
        raise typer.Exit(code=1)


@app.command("list")
def cmd_list() -> None:
    """Lista todos los productos disponibles en el registry."""
    products = list_products()
    console.print("[bold]Productos registrados:[/]")
    for p in products:
        console.print(f"  • [cyan]{p}[/]")


@app.command("publish")
def cmd_publish(
    spec: Path = typer.Option(..., "--spec", "-s", help="Path al archivo YAML de spec"),
    no_overwrite: bool = typer.Option(False, "--no-overwrite", help="Fallar si ya existe en warehouse"),
) -> None:
    """Publica un producto al warehouse (build + copia + manifest)."""
    console.print(f"[bold cyan]📦  Publicando:[/] {spec}")

    result = publish_product(str(spec), overwrite=not no_overwrite)

    if result.success:
        console.print(f"[bold green]✅  Publicado:[/] {result.warehouse_path}")
    else:
        console.print(f"[bold red]❌  Error:[/] {result.error}")
        raise typer.Exit(code=1)


@app.command("publish-all")
def cmd_publish_all(
    no_overwrite: bool = typer.Option(False, "--no-overwrite", help="Fallar si alguno ya existe"),
) -> None:
    """Publica todos los productos registrados al warehouse."""
    console.print("[bold cyan]📦  Publicando todos los productos...[/]")

    results = publish_all_products(overwrite=not no_overwrite)

    table = Table(title="Warehouse", show_header=True, header_style="bold magenta")
    table.add_column("Slug", style="cyan")
    table.add_column("Estado", justify="center")
    table.add_column("Warehouse Path")
    table.add_column("Error")

    ok = 0
    fail = 0
    for r in results:
        status = "[green]✅ OK[/]" if r.success else "[red]❌ FAIL[/]"
        table.add_row(r.slug, status, r.warehouse_path, r.error or "")
        if r.success:
            ok += 1
        else:
            fail += 1

    console.print(table)
    console.print(f"\n[bold]Total:[/] {ok} publicados, {fail} con error")

    if fail > 0:
        raise typer.Exit(code=1)


@app.command("warehouse-list")
def cmd_warehouse_list() -> None:
    """Lista todos los productos publicados en el warehouse."""
    products = list_published()

    if not products:
        console.print("[yellow]⚠  Warehouse vacío. Ejecutá publish-all primero.[/]")
        return

    table = Table(title="Warehouse — Productos publicados", show_header=True, header_style="bold magenta")
    table.add_column("Slug", style="cyan")
    table.add_column("Título")
    table.add_column("Versión", justify="center")
    table.add_column("Precio ARS", justify="right")
    table.add_column("Estado", justify="center")
    table.add_column("Publicado")

    for p in products:
        table.add_row(
            p["slug"],
            p["title"],
            p["version"],
            f"${p['price_ars']:,.0f}",
            f"[green]{p['status']}[/]",
            p["published_at"][:19].replace("T", " "),
        )

    console.print(table)


@app.command("suggest")
def cmd_suggest(
    prompt: str = typer.Option(..., "--prompt", "-p", help="Descripción en lenguaje natural"),
) -> None:
    """Analiza un prompt y sugiere el tipo de planilla sin generar archivos."""
    from exceland_factory.spec_compiler import suggest_prompt

    console.print(f"[bold cyan]🔍  Analizando:[/] {prompt}\n")
    result = suggest_prompt(prompt)

    if not result["matched"]:
        console.print(f"[bold yellow]⚠  {result['message']}[/]\n")
        console.print("[bold]Intentá con:[/]")
        for s in result["suggestions"]:
            console.print(f"  • {s}")
        raise typer.Exit(code=1)

    console.print(f"[bold green]✅  Intent detectado:[/] [cyan]{result['intent']}[/]  "
                  f"(confianza: {result['confidence']:.0%})\n")
    console.print(f"[bold]Título sugerido:[/]  {result['title']}")
    console.print(f"[bold]Subtítulo:[/]        {result['subtitle']}")
    console.print(f"[bold]Categoría:[/]        {result['category']}")
    console.print(f"[bold]Fórmulas:[/]         {', '.join(result['formulas'])}")
    console.print(f"[bold]KPIs:[/]             {', '.join(result['kpis'])}")
    console.print(f"[bold]Tags:[/]             {', '.join(result['tags'])}")

    if result["alternatives"]:
        console.print("\n[bold]Alternativas:[/]")
        for alt in result["alternatives"]:
            console.print(f"  • {alt['intent']} ({alt['confidence']:.0%}) — {alt['title']}")

    console.print(f"\n[dim]Scores: {result['scores']}[/]")


@app.command("compile")
def cmd_compile(
    prompt: str = typer.Option(..., "--prompt", "-p", help="Descripción en lenguaje natural"),
    out: Path = typer.Option(..., "--out", "-o", help="Path de salida del spec YAML"),
    slug: str | None = typer.Option(None, "--slug", help="Slug personalizado"),
    title: str | None = typer.Option(None, "--title", help="Título personalizado"),
) -> None:
    """Compila un prompt a un spec YAML válido y buildable."""
    from exceland_factory.spec_compiler import compile_prompt

    console.print(f"[bold cyan]⚙  Compilando:[/] {prompt}\n")
    result = compile_prompt(prompt, out, slug=slug, title=title)

    if not result.success:
        console.print(f"[bold red]❌  Error:[/] {result.error}")
        if result.suggestions:
            console.print("\n[bold]Sugerencias:[/]")
            for s in result.suggestions:
                console.print(f"  • {s}")
        raise typer.Exit(code=1)

    console.print(f"[bold green]✅  Spec generado:[/] {result.spec_path}")
    console.print(f"[bold]Intent:[/]     {result.intent}  (confianza: {result.confidence:.0%})")
    console.print(f"\n[dim]Siguiente paso:[/]  exceland build --spec {result.spec_path}")


@app.command("generate")
def cmd_generate(
    prompt: str = typer.Option(..., "--prompt", "-p", help="Descripción en lenguaje natural"),
    out_dir: Path = typer.Option(Path("specs"), "--out-dir", help="Directorio para el spec generado"),
    slug: str | None = typer.Option(None, "--slug", help="Slug personalizado"),
    title: str | None = typer.Option(None, "--title", help="Título personalizado"),
    publish: bool = typer.Option(False, "--publish", help="Publicar al warehouse tras el build"),
) -> None:
    """Compila un prompt, buildea el xlsx y opcionalmente publica al warehouse."""
    from exceland_factory.spec_compiler import compile_prompt, suggest_prompt

    console.print(f"[bold cyan]🚀  Generando desde prompt:[/] {prompt}\n")

    # 1. Detectar intent
    suggestion = suggest_prompt(prompt)
    if not suggestion["matched"]:
        console.print(f"[bold red]❌  No se pudo detectar el tipo de planilla.[/]")
        console.print("[bold]Intentá con:[/]")
        for s in suggestion["suggestions"]:
            console.print(f"  • {s}")
        raise typer.Exit(code=1)

    intent = suggestion["intent"]
    console.print(f"[bold]Intent:[/] [cyan]{intent}[/]  (confianza: {suggestion['confidence']:.0%})")

    # 2. Compilar spec
    from exceland_factory.nl_parser import normalize
    auto_slug = slug or f"auto_{intent}"
    spec_path = out_dir / f"{auto_slug}.yaml"

    compile_result = compile_prompt(prompt, spec_path, slug=auto_slug, title=title)
    if not compile_result.success:
        console.print(f"[bold red]❌  Error compilando spec:[/] {compile_result.error}")
        raise typer.Exit(code=1)

    console.print(f"[bold green]✅  Spec generado:[/] {compile_result.spec_path}")

    # 3. Build
    console.print(f"\n[bold cyan]⚙  Construyendo xlsx...[/]")
    build_result = build_product(str(spec_path))
    if not build_result.success:
        console.print(f"[bold red]❌  Build falló:[/] {build_result.error}")
        raise typer.Exit(code=1)

    console.print(f"[bold green]✅  xlsx generado:[/] {build_result.output_path}")

    # 4. Publish (opcional)
    if publish:
        console.print(f"\n[bold cyan]📦  Publicando al warehouse...[/]")
        pub_result = publish_product(str(spec_path))
        if pub_result.success:
            console.print(f"[bold green]✅  Publicado:[/] {pub_result.warehouse_path}")
        else:
            console.print(f"[bold yellow]⚠  Publish falló:[/] {pub_result.error}")

    console.print(f"\n[bold]Listo.[/] Spec: {compile_result.spec_path} | xlsx: {build_result.output_path}")
