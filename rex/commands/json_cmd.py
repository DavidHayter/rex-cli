"""JSON beautify, minify, validate & query operations."""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box

console = Console()
app = typer.Typer(no_args_is_help=True)


def _read_input(data: Optional[str], file: Optional[Path]) -> str:
    """Read JSON input from argument, file, or stdin."""
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
        console.print("[red]✗ No input. Pass JSON as argument, --file, or pipe via stdin.[/red]")
        raise typer.Exit(1)


@app.command("beautify")
def beautify(
    data: Optional[str] = typer.Argument(None, help="JSON string"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Read from file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write to file"),
    indent: int = typer.Option(2, "--indent", "-i", help="Indentation spaces"),
    sort_keys: bool = typer.Option(False, "--sort-keys", "-s", help="Sort object keys"),
):
    """Beautify / pretty-print JSON."""
    raw = _read_input(data, file)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        console.print(f"[red]✗ Invalid JSON: {e}[/red]")
        raise typer.Exit(1)

    result = json.dumps(parsed, indent=indent, sort_keys=sort_keys, ensure_ascii=False)

    if output:
        output.write_text(result)
        console.print(f"[green]✓ Beautified JSON written to {output}[/green]")
    else:
        syntax = Syntax(result, "json", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="📋 Beautified JSON", border_style="green", box=box.ROUNDED))


@app.command("minify")
def minify(
    data: Optional[str] = typer.Argument(None, help="JSON string"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Read from file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write to file"),
):
    """Minify JSON (remove whitespace)."""
    raw = _read_input(data, file)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        console.print(f"[red]✗ Invalid JSON: {e}[/red]")
        raise typer.Exit(1)

    result = json.dumps(parsed, separators=(",", ":"), ensure_ascii=False)

    if output:
        output.write_text(result)
        console.print(f"[green]✓ Minified JSON written to {output}[/green]")
    else:
        console.print(Panel(result, title="📋 Minified JSON", border_style="green", box=box.ROUNDED))


@app.command("validate")
def validate(
    data: Optional[str] = typer.Argument(None, help="JSON string"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Read from file"),
):
    """Validate JSON syntax."""
    raw = _read_input(data, file)
    try:
        parsed = json.loads(raw)
        obj_type = type(parsed).__name__
        if isinstance(parsed, dict):
            detail = f"{len(parsed)} keys"
        elif isinstance(parsed, list):
            detail = f"{len(parsed)} items"
        else:
            detail = obj_type
        console.print(f"[green]✓ Valid JSON ({detail})[/green]")
    except json.JSONDecodeError as e:
        console.print(f"[red]✗ Invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}[/red]")
        raise typer.Exit(1)


@app.command("query")
def query(
    expression: str = typer.Argument(..., help="JMESPath query expression"),
    data: Optional[str] = typer.Option(None, "--data", "-d", help="JSON string"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Read from file"),
):
    """Query JSON with JMESPath expressions."""
    try:
        import jmespath
    except ImportError:
        console.print("[red]✗ jmespath not installed. Run: pip install rex-cli[query][/red]")
        raise typer.Exit(1)

    if file:
        raw = file.read_text() if file.exists() else ""
    elif data:
        raw = data
    elif not sys.stdin.isatty():
        raw = sys.stdin.read()
    else:
        console.print("[red]✗ No input provided.[/red]")
        raise typer.Exit(1)

    try:
        parsed = json.loads(raw)
        result = jmespath.search(expression, parsed)
        formatted = json.dumps(result, indent=2, ensure_ascii=False)
        syntax = Syntax(formatted, "json", theme="monokai")
        console.print(Panel(syntax, title=f"🔍 Query: {expression}", border_style="cyan", box=box.ROUNDED))
    except json.JSONDecodeError as e:
        console.print(f"[red]✗ Invalid JSON: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗ Query error: {e}[/red]")
        raise typer.Exit(1)
