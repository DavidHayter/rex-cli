"""Network utilities — DNS lookup, port check, headers."""

import socket
import subprocess
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()
app = typer.Typer(no_args_is_help=True)


@app.command("dns")
def dns_lookup(
    hostname: str = typer.Argument(..., help="Hostname to resolve"),
    record_type: str = typer.Option("A", "--type", "-t", help="Record type: A, AAAA, CNAME, MX, NS, TXT"),
):
    """DNS lookup for a hostname."""
    table = Table(title=f"🌐 DNS Lookup — {hostname}", box=box.ROUNDED, border_style="green")
    table.add_column("Type", style="bold cyan")
    table.add_column("Value", style="white")

    try:
        if record_type.upper() in ("A", "AAAA"):
            family = socket.AF_INET if record_type.upper() == "A" else socket.AF_INET6
            try:
                results = socket.getaddrinfo(hostname, None, family)
                seen = set()
                for result in results:
                    ip = result[4][0]
                    if ip not in seen:
                        seen.add(ip)
                        table.add_row(record_type.upper(), ip)
            except socket.gaierror:
                console.print(f"[yellow]No {record_type.upper()} records found.[/yellow]")
                return
        else:
            # For MX, NS, TXT etc - try using dig/nslookup if available
            try:
                result = subprocess.run(
                    ["dig", "+short", hostname, record_type.upper()],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    for line in result.stdout.strip().split("\n"):
                        table.add_row(record_type.upper(), line.strip())
                else:
                    console.print(f"[yellow]No {record_type.upper()} records found.[/yellow]")
                    return
            except FileNotFoundError:
                console.print("[yellow]'dig' not available. Install dnsutils for advanced record types.[/yellow]")
                # Fallback to basic A record
                results = socket.getaddrinfo(hostname, None)
                seen = set()
                for result in results:
                    ip = result[4][0]
                    if ip not in seen:
                        seen.add(ip)
                        table.add_row("A", ip)

    except socket.gaierror as e:
        console.print(f"[red]✗ DNS resolution failed: {e}[/red]")
        raise typer.Exit(1)

    console.print(table)


@app.command("port")
def port_check(
    host: str = typer.Argument(..., help="Host to check"),
    ports: str = typer.Argument(..., help="Ports to check (comma-separated or range: 80,443 or 8000-8010)"),
    timeout: float = typer.Option(2.0, "--timeout", "-t", help="Timeout in seconds"),
):
    """Check if ports are open on a host."""
    port_list = []
    for part in ports.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            port_list.extend(range(int(start), int(end) + 1))
        else:
            port_list.append(int(part))

    table = Table(title=f"🔌 Port Check — {host}", box=box.ROUNDED, border_style="green")
    table.add_column("Port", style="bold cyan", min_width=8)
    table.add_column("Status", style="white")
    table.add_column("Service", style="dim")

    for port in sorted(port_list):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                try:
                    service = socket.getservbyport(port)
                except OSError:
                    service = "unknown"
                table.add_row(str(port), "[green]● OPEN[/green]", service)
            else:
                table.add_row(str(port), "[red]● CLOSED[/red]", "—")
        except socket.gaierror:
            console.print(f"[red]✗ Cannot resolve host: {host}[/red]")
            raise typer.Exit(1)
        except Exception as e:
            table.add_row(str(port), f"[yellow]● ERROR[/yellow]", str(e))

    console.print(table)


@app.command("ping")
def ping(
    host: str = typer.Argument(..., help="Host to ping"),
    count: int = typer.Option(4, "--count", "-c", help="Number of pings"),
):
    """Ping a host."""
    flag = "-c" if sys.platform != "win32" else "-n"
    try:
        result = subprocess.run(
            ["ping", flag, str(count), host],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            console.print(f"[green]✓ {host} is reachable[/green]\n")
            console.print(result.stdout)
        else:
            console.print(f"[red]✗ {host} is unreachable[/red]\n")
            console.print(result.stderr or result.stdout)
            raise typer.Exit(1)
    except FileNotFoundError:
        console.print("[red]✗ ping command not found.[/red]")
        raise typer.Exit(1)
    except subprocess.TimeoutExpired:
        console.print(f"[red]✗ Ping to {host} timed out.[/red]")
        raise typer.Exit(1)
