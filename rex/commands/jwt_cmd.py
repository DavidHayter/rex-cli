"""Decode & inspect JWT tokens."""

import json
import base64
import sys
from datetime import datetime, timezone
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich import box

console = Console()
app = typer.Typer(no_args_is_help=True)


def _b64decode_jwt(data: str) -> dict:
    """Decode a JWT segment (handles missing padding)."""
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    decoded = base64.urlsafe_b64decode(data)
    return json.loads(decoded)


@app.command("decode")
def decode(
    token: Optional[str] = typer.Argument(None, help="JWT token to decode"),
):
    """Decode and display JWT header and payload."""
    if not token:
        if not sys.stdin.isatty():
            token = sys.stdin.read().strip()
        else:
            console.print("[red]✗ No token provided.[/red]")
            raise typer.Exit(1)

    parts = token.strip().split(".")
    if len(parts) not in (2, 3):
        console.print("[red]✗ Invalid JWT format. Expected 2 or 3 segments.[/red]")
        raise typer.Exit(1)

    try:
        header = _b64decode_jwt(parts[0])
        payload = _b64decode_jwt(parts[1])
    except Exception as e:
        console.print(f"[red]✗ Failed to decode JWT: {e}[/red]")
        raise typer.Exit(1)

    # Header
    header_json = json.dumps(header, indent=2)
    console.print(Panel(
        Syntax(header_json, "json", theme="monokai"),
        title="🎫 JWT Header",
        border_style="cyan",
        box=box.ROUNDED,
    ))

    # Payload
    payload_json = json.dumps(payload, indent=2)
    console.print(Panel(
        Syntax(payload_json, "json", theme="monokai"),
        title="🎫 JWT Payload",
        border_style="green",
        box=box.ROUNDED,
    ))

    # Token info
    table = Table(title="📋 Token Details", box=box.ROUNDED, border_style="yellow")
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", style="white")

    table.add_row("Algorithm", header.get("alg", "N/A"))
    table.add_row("Type", header.get("typ", "N/A"))

    if "iss" in payload:
        table.add_row("Issuer", str(payload["iss"]))
    if "sub" in payload:
        table.add_row("Subject", str(payload["sub"]))
    if "aud" in payload:
        table.add_row("Audience", str(payload["aud"]))

    if "iat" in payload:
        iat = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        table.add_row("Issued At", iat.strftime("%Y-%m-%d %H:%M:%S UTC"))

    if "exp" in payload:
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        is_expired = now > exp
        status = "[red]EXPIRED[/red]" if is_expired else "[green]VALID[/green]"
        table.add_row("Expires", f"{exp.strftime('%Y-%m-%d %H:%M:%S UTC')} ({status})")

    if "nbf" in payload:
        nbf = datetime.fromtimestamp(payload["nbf"], tz=timezone.utc)
        table.add_row("Not Before", nbf.strftime("%Y-%m-%d %H:%M:%S UTC"))

    table.add_row("Signature", f"{'Present' if len(parts) == 3 else 'None'} ({len(parts[-1])} chars)")

    console.print(table)
