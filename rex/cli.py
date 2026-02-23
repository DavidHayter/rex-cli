"""Rex CLI — Main entry point."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich import box

from rex import __version__
from rex.commands import (
    encrypt_cmd,
    json_cmd,
    yaml_cmd,
    password_cmd,
    cron_cmd,
    hash_cmd,
    base64_cmd,
    jwt_cmd,
    uuid_cmd,
    cert_cmd,
    network_cmd,
)

console = Console()

app = typer.Typer(
    name="rex",
    help="🦖 Rex — A Swiss Army Knife CLI for DevOps Engineers",
    add_completion=True,
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Register command groups
app.add_typer(encrypt_cmd.app, name="encrypt", help="🔐 Encrypt & decrypt data (AES-256, ChaCha20, Fernet)")
app.add_typer(json_cmd.app, name="json", help="📋 JSON beautify, minify, validate & query")
app.add_typer(yaml_cmd.app, name="yaml", help="📄 YAML lint, validate & convert")
app.add_typer(password_cmd.app, name="password", help="🔑 Generate secure passwords & passphrases")
app.add_typer(cron_cmd.app, name="cron", help="⏰ Generate & explain cron expressions")
app.add_typer(hash_cmd.app, name="hash", help="🔒 Generate hashes (MD5, SHA, BLAKE2, HMAC)")
app.add_typer(base64_cmd.app, name="base64", help="📦 Base64 encode & decode")
app.add_typer(jwt_cmd.app, name="jwt", help="🎫 Decode & inspect JWT tokens")
app.add_typer(uuid_cmd.app, name="uuid", help="🆔 Generate UUIDs (v1, v4, v5)")
app.add_typer(cert_cmd.app, name="cert", help="📜 Inspect SSL/TLS certificates")
app.add_typer(network_cmd.app, name="net", help="🌐 Network utilities (DNS, ping, port check)")


@app.command("version")
def version():
    """Show Rex version."""
    console.print(
        Panel(
            f"[bold green]🦖 Rex[/bold green] v{__version__}\n"
            f"[dim]A Swiss Army Knife CLI for DevOps Engineers[/dim]",
            box=box.ROUNDED,
            border_style="green",
        )
    )


@app.command("info")
def info():
    """Show all available command groups."""
    commands = [
        ("encrypt", "Encrypt & decrypt data", "AES-256-GCM, ChaCha20-Poly1305, Fernet"),
        ("json", "JSON operations", "beautify, minify, validate, query (JMESPath)"),
        ("yaml", "YAML operations", "lint, validate, to-json conversion"),
        ("password", "Password generation", "random, passphrase, custom policies"),
        ("cron", "Cron expressions", "generate from natural language, explain, validate"),
        ("hash", "Hash generation", "MD5, SHA-256, SHA-512, BLAKE2, HMAC"),
        ("base64", "Base64 operations", "encode, decode, file support"),
        ("jwt", "JWT inspection", "decode headers & payload, check expiry"),
        ("uuid", "UUID generation", "v1, v4, v5 with namespace support"),
        ("cert", "Certificate inspection", "SSL/TLS cert details, expiry check"),
        ("net", "Network utilities", "DNS lookup, ping, port check, whois"),
    ]

    from rich.table import Table

    table = Table(
        title="🦖 Rex — Available Commands",
        box=box.ROUNDED,
        border_style="green",
        title_style="bold green",
    )
    table.add_column("Command", style="bold cyan", min_width=12)
    table.add_column("Description", style="white")
    table.add_column("Features", style="dim")

    for cmd, desc, features in commands:
        table.add_row(f"rex {cmd}", desc, features)

    console.print(table)
    console.print("\n[dim]Run [bold]rex <command> --help[/bold] for detailed usage.[/dim]")


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
