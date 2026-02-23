"""Inspect SSL/TLS certificates."""

import ssl
import socket
from datetime import datetime, timezone
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()
app = typer.Typer(no_args_is_help=True)


@app.command("inspect")
def inspect(
    host: str = typer.Argument(..., help="Hostname to check (e.g., google.com)"),
    port: int = typer.Option(443, "--port", "-p", help="Port number"),
    timeout: int = typer.Option(10, "--timeout", "-t", help="Connection timeout in seconds"),
):
    """Inspect SSL/TLS certificate of a remote host."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                protocol = ssock.version()
    except ssl.SSLCertVerificationError as e:
        console.print(f"[red]✗ SSL Verification Error: {e}[/red]")
        raise typer.Exit(1)
    except (socket.timeout, socket.gaierror, ConnectionRefusedError) as e:
        console.print(f"[red]✗ Connection failed: {e}[/red]")
        raise typer.Exit(1)

    # Parse dates
    not_before = datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    now = datetime.now(tz=timezone.utc)
    days_left = (not_after - now).days
    is_expired = days_left < 0

    # Subject & Issuer
    subject = dict(x[0] for x in cert.get("subject", ()))
    issuer = dict(x[0] for x in cert.get("issuer", ()))

    # SAN
    san_list = [entry[1] for entry in cert.get("subjectAltName", ())]

    # Display
    table = Table(title=f"📜 Certificate — {host}:{port}", box=box.ROUNDED, border_style="green")
    table.add_column("Field", style="bold cyan", min_width=18)
    table.add_column("Value", style="white")

    table.add_row("Common Name", subject.get("commonName", "N/A"))
    table.add_row("Organization", subject.get("organizationName", "N/A"))
    table.add_row("Issuer", issuer.get("organizationName", "N/A"))
    table.add_row("Issuer CN", issuer.get("commonName", "N/A"))
    table.add_row("Serial Number", cert.get("serialNumber", "N/A"))
    table.add_row("Valid From", not_before.strftime("%Y-%m-%d %H:%M:%S UTC"))
    table.add_row("Valid Until", not_after.strftime("%Y-%m-%d %H:%M:%S UTC"))

    if is_expired:
        table.add_row("Status", f"[red bold]EXPIRED ({abs(days_left)} days ago)[/red bold]")
    elif days_left <= 30:
        table.add_row("Status", f"[yellow bold]EXPIRING SOON ({days_left} days left)[/yellow bold]")
    else:
        table.add_row("Status", f"[green]Valid ({days_left} days remaining)[/green]")

    table.add_row("Protocol", protocol or "N/A")
    if cipher:
        table.add_row("Cipher", f"{cipher[0]} ({cipher[2]} bit)")

    if san_list:
        table.add_row("SANs", ", ".join(san_list[:5]))
        if len(san_list) > 5:
            table.add_row("", f"[dim]... and {len(san_list) - 5} more[/dim]")

    console.print(table)


@app.command("expiry")
def expiry(
    host: str = typer.Argument(..., help="Hostname to check"),
    port: int = typer.Option(443, "--port", "-p"),
    warn_days: int = typer.Option(30, "--warn", "-w", help="Warning threshold in days"),
):
    """Quick check certificate expiry (useful for monitoring scripts)."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
    except Exception as e:
        console.print(f"[red]CRITICAL — {host}: {e}[/red]")
        raise typer.Exit(2)

    not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    days_left = (not_after - datetime.now(tz=timezone.utc)).days

    if days_left < 0:
        console.print(f"[red]CRITICAL — {host}: Certificate expired {abs(days_left)} days ago[/red]")
        raise typer.Exit(2)
    elif days_left <= warn_days:
        console.print(f"[yellow]WARNING — {host}: Certificate expires in {days_left} days[/yellow]")
        raise typer.Exit(1)
    else:
        console.print(f"[green]OK — {host}: Certificate valid for {days_left} days[/green]")
