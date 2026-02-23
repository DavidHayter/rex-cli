"""Generate UUIDs — v1, v4, v5."""

import uuid
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()
app = typer.Typer(no_args_is_help=True)

NAMESPACES = {
    "dns": uuid.NAMESPACE_DNS,
    "url": uuid.NAMESPACE_URL,
    "oid": uuid.NAMESPACE_OID,
    "x500": uuid.NAMESPACE_X500,
}


@app.command("generate")
def generate(
    version: int = typer.Option(4, "--version", "-v", help="UUID version (1, 4, or 5)"),
    count: int = typer.Option(1, "--count", "-c", help="Number of UUIDs"),
    upper: bool = typer.Option(False, "--upper", "-u", help="Uppercase output"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Name for v5 UUID"),
    namespace: str = typer.Option("dns", "--namespace", help="Namespace for v5: dns, url, oid, x500"),
):
    """Generate UUIDs."""
    if version not in (1, 4, 5):
        console.print("[red]✗ Supported versions: 1, 4, 5[/red]")
        raise typer.Exit(1)

    if version == 5 and not name:
        console.print("[red]✗ UUID v5 requires --name[/red]")
        raise typer.Exit(1)

    table = Table(title=f"🆔 UUID v{version}", box=box.ROUNDED, border_style="green")
    table.add_column("#", style="dim", width=4)
    table.add_column("UUID", style="bold white")

    for i in range(count):
        if version == 1:
            result = uuid.uuid1()
        elif version == 4:
            result = uuid.uuid4()
        elif version == 5:
            ns = NAMESPACES.get(namespace)
            if not ns:
                console.print(f"[red]✗ Unknown namespace: {namespace}[/red]")
                raise typer.Exit(1)
            result = uuid.uuid5(ns, name)

        uid = str(result).upper() if upper else str(result)
        table.add_row(str(i + 1), uid)

    console.print(table)
