"""YAML lint, validate & convert operations."""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box

import yaml

console = Console()
app = typer.Typer(no_args_is_help=True)


def _read_input(data: Optional[str], file: Optional[Path]) -> str:
    """Read input from argument, file, or stdin."""
    if file:
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)
        return file.read_text()
    elif data:
        return data
    elif not sys.stdin.isatty():
        return sys.stdin.read()
    else:
        console.print("[red]✗ No input. Pass YAML as argument, --file, or pipe via stdin.[/red]")
        raise typer.Exit(1)


@app.command("lint")
def lint(
    file: Path = typer.Argument(..., help="YAML file to lint"),
    strict: bool = typer.Option(False, "--strict", "-s", help="Strict mode (warn on duplicates)"),
):
    """Lint a YAML file for syntax errors."""
    if not file.exists():
        console.print(f"[red]✗ File not found: {file}[/red]")
        raise typer.Exit(1)

    content = file.read_text()
    errors = []
    warnings = []

    try:
        docs = list(yaml.safe_load_all(content))
        doc_count = len(docs)
    except yaml.YAMLError as e:
        if hasattr(e, "problem_mark"):
            mark = e.problem_mark
            errors.append(f"Line {mark.line + 1}, Col {mark.column + 1}: {e.problem}")
        else:
            errors.append(str(e))
        doc_count = 0

    # Check common issues
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        if "\t" in line:
            warnings.append(f"Line {i}: Tab character found (use spaces)")
        if line.rstrip() != line and line.strip():
            warnings.append(f"Line {i}: Trailing whitespace")

    if errors:
        console.print(f"[red]✗ {file.name} — {len(errors)} error(s)[/red]")
        for err in errors:
            console.print(f"  [red]• {err}[/red]")
        raise typer.Exit(1)
    elif warnings and strict:
        console.print(f"[yellow]⚠ {file.name} — Valid with {len(warnings)} warning(s)[/yellow]")
        for warn in warnings:
            console.print(f"  [yellow]• {warn}[/yellow]")
    else:
        console.print(f"[green]✓ {file.name} — Valid YAML ({doc_count} document(s))[/green]")


@app.command("validate")
def validate(
    data: Optional[str] = typer.Argument(None, help="YAML string"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Read from file"),
):
    """Validate YAML syntax."""
    raw = _read_input(data, file)
    try:
        parsed = yaml.safe_load(raw)
        console.print(f"[green]✓ Valid YAML (type: {type(parsed).__name__})[/green]")
    except yaml.YAMLError as e:
        console.print(f"[red]✗ Invalid YAML: {e}[/red]")
        raise typer.Exit(1)


@app.command("to-json")
def to_json(
    data: Optional[str] = typer.Argument(None, help="YAML string"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Read from file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write to file"),
    indent: int = typer.Option(2, "--indent", "-i", help="JSON indentation"),
):
    """Convert YAML to JSON."""
    raw = _read_input(data, file)
    try:
        parsed = yaml.safe_load(raw)
        result = json.dumps(parsed, indent=indent, ensure_ascii=False)

        if output:
            output.write_text(result)
            console.print(f"[green]✓ JSON written to {output}[/green]")
        else:
            syntax = Syntax(result, "json", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="📄 YAML → JSON", border_style="green", box=box.ROUNDED))
    except yaml.YAMLError as e:
        console.print(f"[red]✗ Invalid YAML: {e}[/red]")
        raise typer.Exit(1)


@app.command("to-yaml")
def from_json(
    data: Optional[str] = typer.Argument(None, help="JSON string"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Read JSON from file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write to file"),
):
    """Convert JSON to YAML."""
    raw = _read_input(data, file)
    try:
        parsed = json.loads(raw)
        result = yaml.dump(parsed, default_flow_style=False, allow_unicode=True, sort_keys=False)

        if output:
            output.write_text(result)
            console.print(f"[green]✓ YAML written to {output}[/green]")
        else:
            syntax = Syntax(result, "yaml", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="📄 JSON → YAML", border_style="green", box=box.ROUNDED))
    except json.JSONDecodeError as e:
        console.print(f"[red]✗ Invalid JSON: {e}[/red]")
        raise typer.Exit(1)
