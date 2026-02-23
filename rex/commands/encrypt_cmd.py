"""Encrypt & decrypt data with multiple algorithms."""

import os
import base64
import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich import box

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

console = Console()
app = typer.Typer(no_args_is_help=True)

ALGORITHMS = ["aes-256-gcm", "chacha20-poly1305", "fernet"]


def _derive_key(password: str, salt: bytes, key_length: int = 32) -> bytes:
    """Derive a key from password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=key_length,
        salt=salt,
        iterations=480000,
    )
    return kdf.derive(password.encode())


@app.command("enc")
def encrypt(
    data: Optional[str] = typer.Argument(None, help="Data to encrypt (or pipe via stdin)"),
    password: str = typer.Option(..., "--password", "-p", prompt=True, hide_input=True, help="Encryption password"),
    algorithm: str = typer.Option("aes-256-gcm", "--algo", "-a", help="Algorithm: aes-256-gcm, chacha20-poly1305, fernet"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write result to file"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Encrypt a file"),
):
    """Encrypt data or files."""
    algo = algorithm.lower()
    if algo not in ALGORITHMS:
        console.print(f"[red]✗ Unknown algorithm: {algorithm}. Use: {', '.join(ALGORITHMS)}[/red]")
        raise typer.Exit(1)

    # Get input data
    if file:
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)
        plaintext = file.read_bytes()
    elif data:
        plaintext = data.encode()
    elif not sys.stdin.isatty():
        plaintext = sys.stdin.buffer.read()
    else:
        console.print("[red]✗ No data provided. Pass data as argument, --file, or pipe via stdin.[/red]")
        raise typer.Exit(1)

    salt = os.urandom(16)
    key = _derive_key(password, salt)

    if algo == "aes-256-gcm":
        nonce = os.urandom(12)
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        payload = {"alg": algo, "salt": base64.b64encode(salt).decode(), "nonce": base64.b64encode(nonce).decode(), "data": base64.b64encode(ciphertext).decode()}

    elif algo == "chacha20-poly1305":
        nonce = os.urandom(12)
        chacha = ChaCha20Poly1305(key)
        ciphertext = chacha.encrypt(nonce, plaintext, None)
        payload = {"alg": algo, "salt": base64.b64encode(salt).decode(), "nonce": base64.b64encode(nonce).decode(), "data": base64.b64encode(ciphertext).decode()}

    elif algo == "fernet":
        fernet_key = base64.urlsafe_b64encode(_derive_key(password, salt))
        f = Fernet(fernet_key)
        ciphertext = f.encrypt(plaintext)
        payload = {"alg": algo, "salt": base64.b64encode(salt).decode(), "data": ciphertext.decode()}

    result = base64.b64encode(json.dumps(payload).encode()).decode()

    if output:
        output.write_text(result)
        console.print(f"[green]✓ Encrypted data written to {output}[/green]")
    else:
        console.print(Panel(result, title=f"🔐 Encrypted ({algo})", border_style="green", box=box.ROUNDED))


@app.command("dec")
def decrypt(
    data: Optional[str] = typer.Argument(None, help="Encrypted data (or pipe via stdin)"),
    password: str = typer.Option(..., "--password", "-p", prompt=True, hide_input=True, help="Decryption password"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write result to file"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Decrypt from file"),
):
    """Decrypt data or files."""
    # Get input
    if file:
        if not file.exists():
            console.print(f"[red]✗ File not found: {file}[/red]")
            raise typer.Exit(1)
        raw = file.read_text().strip()
    elif data:
        raw = data.strip()
    elif not sys.stdin.isatty():
        raw = sys.stdin.read().strip()
    else:
        console.print("[red]✗ No data provided.[/red]")
        raise typer.Exit(1)

    try:
        payload = json.loads(base64.b64decode(raw))
    except Exception:
        console.print("[red]✗ Invalid encrypted data format.[/red]")
        raise typer.Exit(1)

    algo = payload.get("alg", "")
    salt = base64.b64decode(payload["salt"])
    key = _derive_key(password, salt)

    try:
        if algo == "aes-256-gcm":
            nonce = base64.b64decode(payload["nonce"])
            ciphertext = base64.b64decode(payload["data"])
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)

        elif algo == "chacha20-poly1305":
            nonce = base64.b64decode(payload["nonce"])
            ciphertext = base64.b64decode(payload["data"])
            chacha = ChaCha20Poly1305(key)
            plaintext = chacha.decrypt(nonce, ciphertext, None)

        elif algo == "fernet":
            fernet_key = base64.urlsafe_b64encode(_derive_key(password, salt))
            f = Fernet(fernet_key)
            plaintext = f.decrypt(payload["data"].encode())

        else:
            console.print(f"[red]✗ Unknown algorithm: {algo}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]✗ Decryption failed. Wrong password or corrupted data.[/red]")
        raise typer.Exit(1)

    if output:
        output.write_bytes(plaintext)
        console.print(f"[green]✓ Decrypted data written to {output}[/green]")
    else:
        try:
            console.print(Panel(plaintext.decode(), title="🔓 Decrypted", border_style="green", box=box.ROUNDED))
        except UnicodeDecodeError:
            console.print(f"[green]✓ Decrypted {len(plaintext)} bytes (binary data — use --output to save)[/green]")


@app.command("algorithms")
def list_algorithms():
    """List supported encryption algorithms."""
    from rich.table import Table

    table = Table(title="🔐 Supported Algorithms", box=box.ROUNDED, border_style="green")
    table.add_column("Algorithm", style="bold cyan")
    table.add_column("Key Derivation", style="white")
    table.add_column("Notes", style="dim")

    table.add_row("aes-256-gcm", "PBKDF2-SHA256 (480k iterations)", "Default. NIST standard, authenticated encryption")
    table.add_row("chacha20-poly1305", "PBKDF2-SHA256 (480k iterations)", "Fast on devices without AES hardware acceleration")
    table.add_row("fernet", "PBKDF2-SHA256 (480k iterations)", "High-level symmetric encryption (AES-128-CBC + HMAC)")

    console.print(table)
