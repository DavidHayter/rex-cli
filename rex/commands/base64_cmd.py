"""Base64 encode & decode operations."""

import base64
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()
app = typer.Typer(no_args_is_help=True)


def _read_input(data: Optional[str], file: Optional[Path]) -> bytes:
    if file:
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)
        return file.read_bytes()
    elif data:
        return data.encode()
    elif not sys.stdin.isatty():
        return sys.stdin.buffer.read()
    else:
        console.print("[red]✗ No input provided.[/red]")
        raise typer.Exit(1)


@app.command("encode")
def encode(
    data: Optional[str] = typer.Argument(None, help="Data to encode"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Encode a file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write to file"),
    url_safe: bool = typer.Option(False, "--url-safe", "-u", help="Use URL-safe Base64"),
):
    """Encode data to Base64."""
    content = _read_input(data, file)

    if url_safe:
        result = base64.urlsafe_b64encode(content).decode()
    else:
        result = base64.b64encode(content).decode()

    if output:
        output.write_text(result)
        console.print(f"[green]✓ Encoded data written to {output}[/green]")
    else:
        console.print(Panel(result, title="📦 Base64 Encoded", border_style="green", box=box.ROUNDED))


@app.command("decode")
def decode(
    data: Optional[str] = typer.Argument(None, help="Base64 string to decode"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Read from file"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write to file"),
    url_safe: bool = typer.Option(False, "--url-safe", "-u", help="URL-safe Base64"),
):
    """Decode Base64 data."""
    content = _read_input(data, file)

    try:
        if url_safe:
            result = base64.urlsafe_b64decode(content)
        else:
            result = base64.b64decode(content)
    except Exception as e:
        console.print(f"[red]✗ Invalid Base64: {e}[/red]")
        raise typer.Exit(1)

    if output:
        output.write_bytes(result)
        console.print(f"[green]✓ Decoded data written to {output}[/green]")
    else:
        try:
            console.print(Panel(result.decode(), title="📦 Base64 Decoded", border_style="green", box=box.ROUNDED))
        except UnicodeDecodeError:
            console.print(f"[green]✓ Decoded {len(result)} bytes (binary — use --output to save)[/green]")
