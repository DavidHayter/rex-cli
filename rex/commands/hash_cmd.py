"""Generate hashes — MD5, SHA, BLAKE2, HMAC."""

import hashlib
import hmac as hmac_lib
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()
app = typer.Typer(no_args_is_help=True)

ALGORITHMS = ["md5", "sha1", "sha256", "sha512", "blake2b", "blake2s"]


@app.command("generate")
def generate(
    data: Optional[str] = typer.Argument(None, help="Data to hash"),
    algorithm: str = typer.Option("sha256", "--algo", "-a", help="Hash algorithm"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Hash a file"),
    all_algos: bool = typer.Option(False, "--all", help="Show hash for all algorithms"),
):
    """Generate a hash digest."""
    if file:
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)
        content = file.read_bytes()
        source = str(file)
    elif data:
        content = data.encode()
        source = f"string ({len(data)} chars)"
    elif not sys.stdin.isatty():
        content = sys.stdin.buffer.read()
        source = "stdin"
    else:
        console.print("[red]✗ No input provided.[/red]")
        raise typer.Exit(1)

    if all_algos:
        table = Table(title=f"🔒 Hash Digests — {source}", box=box.ROUNDED, border_style="green")
        table.add_column("Algorithm", style="bold cyan", min_width=10)
        table.add_column("Digest", style="white")

        for algo in ALGORITHMS:
            h = hashlib.new(algo)
            h.update(content)
            table.add_row(algo.upper(), h.hexdigest())

        console.print(table)
    else:
        algo = algorithm.lower()
        if algo not in ALGORITHMS:
            console.print(f"[red]✗ Unknown algorithm: {algo}. Use: {', '.join(ALGORITHMS)}[/red]")
            raise typer.Exit(1)

        h = hashlib.new(algo)
        h.update(content)
        digest = h.hexdigest()

        console.print(Panel(
            f"[bold white]{digest}[/bold white]",
            title=f"🔒 {algo.upper()} — {source}",
            border_style="green",
            box=box.ROUNDED,
        ))


@app.command("hmac")
def hmac_generate(
    data: Optional[str] = typer.Argument(None, help="Data to hash"),
    key: str = typer.Option(..., "--key", "-k", help="HMAC secret key"),
    algorithm: str = typer.Option("sha256", "--algo", "-a", help="Hash algorithm"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Hash a file"),
):
    """Generate an HMAC digest."""
    if file:
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)
        content = file.read_bytes()
    elif data:
        content = data.encode()
    elif not sys.stdin.isatty():
        content = sys.stdin.buffer.read()
    else:
        console.print("[red]✗ No input provided.[/red]")
        raise typer.Exit(1)

    algo = algorithm.lower()
    if algo not in ALGORITHMS:
        console.print(f"[red]✗ Unknown algorithm: {algo}[/red]")
        raise typer.Exit(1)

    digest = hmac_lib.new(key.encode(), content, algo).hexdigest()

    console.print(Panel(
        f"[bold white]{digest}[/bold white]",
        title=f"🔒 HMAC-{algo.upper()}",
        border_style="green",
        box=box.ROUNDED,
    ))


@app.command("verify")
def verify(
    data: Optional[str] = typer.Argument(None, help="Data to verify"),
    expected: str = typer.Option(..., "--expected", "-e", help="Expected hash to compare"),
    algorithm: str = typer.Option("sha256", "--algo", "-a", help="Hash algorithm"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Verify a file"),
):
    """Verify data against a known hash."""
    if file:
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)
        content = file.read_bytes()
    elif data:
        content = data.encode()
    elif not sys.stdin.isatty():
        content = sys.stdin.buffer.read()
    else:
        console.print("[red]✗ No input provided.[/red]")
        raise typer.Exit(1)

    algo = algorithm.lower()
    h = hashlib.new(algo)
    h.update(content)
    actual = h.hexdigest()

    if actual == expected.lower():
        console.print(f"[green]✓ Hash matches! ({algo.upper()})[/green]")
    else:
        console.print(f"[red]✗ Hash mismatch![/red]")
        console.print(f"  [dim]Expected: {expected}[/dim]")
        console.print(f"  [dim]Actual:   {actual}[/dim]")
        raise typer.Exit(1)
