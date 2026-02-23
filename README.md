<div align="center">

# 🦖 Rex

**A Swiss Army Knife CLI for DevOps Engineers**

[![PyPI version](https://img.shields.io/pypi/v/rex-cli?style=flat-square&color=06D6A0)](https://pypi.org/project/rex-cli/)
[![Python](https://img.shields.io/pypi/pyversions/rex-cli?style=flat-square)](https://pypi.org/project/rex-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/github/actions/workflow/status/DavidHayter/rex-cli/test.yml?style=flat-square&label=tests)](https://github.com/DavidHayter/rex-cli/actions)

*Encrypt secrets, lint configs, generate passwords, inspect certificates — all from your terminal.*

[Installation](#-installation) · [Quick Start](#-quick-start) · [Commands](#-commands) · [Contributing](#-contributing)

</div>

---

## ⚡ Installation

```bash
# From PyPI
pip install rex-cli

# With JMESPath query support
pip install rex-cli[query]

# From source
git clone https://github.com/DavidHayter/rex-cli.git
cd rex-cli
pip install -e ".[dev]"
```

Verify installation:
```bash
rex version
```

## 🚀 Quick Start

```bash
# Encrypt a secret
rex encrypt enc "my-database-password" -p

# Beautify a JSON file
rex json beautify --file config.json --output pretty.json

# Lint your Kubernetes YAML
rex yaml lint deployment.yaml

# Generate a secure password
rex password generate --length 32

# Explain a cron expression
rex cron explain "*/5 9-17 * * 1-5"

# Hash a file
rex hash generate --file backup.tar.gz --all

# Check SSL certificate expiry
rex cert expiry example.com

# Scan open ports
rex net port 192.168.1.1 22,80,443,8080
```

## 📖 Commands

### 🔐 `rex encrypt` — Encryption & Decryption

Encrypt and decrypt data using industry-standard algorithms with password-based key derivation (PBKDF2, 480k iterations).

```bash
# Encrypt with AES-256-GCM (default)
rex encrypt enc "sensitive data" -p
> Enter password: ****

# Encrypt with ChaCha20-Poly1305
rex encrypt enc "sensitive data" -p --algo chacha20-poly1305

# Encrypt a file
rex encrypt enc -p --file secrets.env --output secrets.enc

# Decrypt
rex encrypt dec "eyJhbGci..." -p

# List supported algorithms
rex encrypt algorithms
```

| Algorithm | Description |
|-----------|-------------|
| `aes-256-gcm` | Default. NIST standard, authenticated encryption |
| `chacha20-poly1305` | Fast on devices without AES hardware support |
| `fernet` | High-level symmetric encryption (AES-128-CBC + HMAC) |

---

### 📋 `rex json` — JSON Operations

```bash
# Beautify
rex json beautify '{"name":"rex","version":1}' --indent 4

# Beautify from file and save
rex json beautify --file raw.json --output pretty.json

# Minify
rex json minify --file config.json

# Validate
rex json validate --file package.json

# Query with JMESPath (requires: pip install rex-cli[query])
cat data.json | rex json query "users[?age > `30`].name"
```

---

### 📄 `rex yaml` — YAML Operations

```bash
# Lint a YAML file
rex yaml lint deployment.yaml

# Strict mode (warns on tabs, trailing whitespace)
rex yaml lint values.yaml --strict

# Convert YAML to JSON
rex yaml to-json --file values.yaml --output values.json

# Convert JSON to YAML
rex yaml to-yaml --file config.json --output config.yaml

# Validate YAML syntax
rex yaml validate "key: value"
```

---

### 🔑 `rex password` — Password Generation

```bash
# Generate a 24-char password (default)
rex password generate

# Custom length, multiple passwords
rex password generate --length 48 --count 5

# No symbols
rex password generate --length 16 --no-symbols

# Exclude ambiguous characters
rex password generate --exclude "0OlI1"

# Generate a passphrase
rex password passphrase --words 6 --separator "-"

# Capitalized passphrase
rex password passphrase --words 5 --capitalize --separator "."
```

---

### ⏰ `rex cron` — Cron Expressions

```bash
# Explain a cron expression
rex cron explain "30 2 * * 0"

# Show all presets
rex cron presets

# Use a preset
rex cron generate daily
rex cron generate backup-nightly
rex cron generate business-hours

# Build custom expression
rex cron generate --minute "*/15" --hour "9-17" --weekday "1-5"
```

**DevOps-focused presets:** `health-check`, `backup-nightly`, `cleanup-weekly`, `log-rotation`, `cert-renewal`, and more.

---

### 🔒 `rex hash` — Hash Generation

```bash
# SHA-256 hash (default)
rex hash generate "hello world"

# All algorithms at once
rex hash generate "hello world" --all

# Hash a file
rex hash generate --file backup.tar.gz --algo sha512

# HMAC
rex hash hmac "message" --key "my-secret" --algo sha256

# Verify a hash
rex hash verify "hello" --expected "2cf24dba..."
```

| Algorithm | Output Length |
|-----------|-------------|
| `md5` | 128-bit |
| `sha1` | 160-bit |
| `sha256` | 256-bit |
| `sha512` | 512-bit |
| `blake2b` | 512-bit |
| `blake2s` | 256-bit |

---

### 📦 `rex base64` — Base64 Operations

```bash
# Encode
rex base64 encode "hello world"

# Decode
rex base64 decode "aGVsbG8gd29ybGQ="

# URL-safe encoding
rex base64 encode "https://example.com?q=test" --url-safe

# File operations
rex base64 encode --file image.png --output image.b64
rex base64 decode --file image.b64 --output restored.png

# Pipe support
echo "secret" | rex base64 encode
```

---

### 🎫 `rex jwt` — JWT Token Inspection

```bash
# Decode a JWT
rex jwt decode "eyJhbGciOiJIUzI1NiIs..."

# Pipe from clipboard
pbpaste | rex jwt decode

# Shows:
# - Header (algorithm, type)
# - Payload (all claims)
# - Expiry status (VALID / EXPIRED)
# - Issued at, subject, issuer, audience
```

---

### 🆔 `rex uuid` — UUID Generation

```bash
# Generate UUID v4 (random)
rex uuid generate

# Multiple UUIDs
rex uuid generate --count 10

# UUID v1 (timestamp-based)
rex uuid generate --version 1

# UUID v5 (namespace + name)
rex uuid generate --version 5 --name "example.com"

# Uppercase
rex uuid generate --upper
```

---

### 📜 `rex cert` — SSL/TLS Certificate Inspection

```bash
# Full certificate details
rex cert inspect google.com

# Check expiry (great for monitoring scripts)
rex cert expiry google.com
rex cert expiry --warn 60 production-api.company.com

# Custom port
rex cert inspect mail.example.com --port 465
```

Exit codes for `cert expiry` (perfect for monitoring):
- `0` — Certificate is valid
- `1` — Certificate expiring soon (within --warn days)
- `2` — Certificate expired or connection failed

---

### 🌐 `rex net` — Network Utilities

```bash
# DNS lookup
rex net dns example.com
rex net dns example.com --type MX
rex net dns example.com --type TXT

# Port scanning
rex net port 192.168.1.1 22,80,443
rex net port server.com 8000-8010

# Ping
rex net ping 8.8.8.8
rex net ping google.com --count 10
```

---

## 🔧 Pipe Support

Rex supports Unix pipes across all commands:

```bash
# Chain commands
echo '{"key":"value"}' | rex json beautify
cat config.yaml | rex yaml to-json
echo "secret" | rex base64 encode
echo "secret" | rex hash generate --all
pbpaste | rex jwt decode
```

## 🧪 Development

```bash
# Clone and install
git clone https://github.com/DavidHayter/rex-cli.git
cd rex-cli
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=rex --cov-report=html

# Lint
ruff check rex/
ruff format rex/

# Type check
mypy rex/
```

## 📦 Project Structure

```
rex-cli/
├── rex/
│   ├── __init__.py          # Version & metadata
│   ├── cli.py               # Main CLI entry point
│   └── commands/
│       ├── encrypt_cmd.py   # Encryption & decryption
│       ├── json_cmd.py      # JSON operations
│       ├── yaml_cmd.py      # YAML operations
│       ├── password_cmd.py  # Password generation
│       ├── cron_cmd.py      # Cron expressions
│       ├── hash_cmd.py      # Hash generation
│       ├── base64_cmd.py    # Base64 encode/decode
│       ├── jwt_cmd.py       # JWT inspection
│       ├── uuid_cmd.py      # UUID generation
│       ├── cert_cmd.py      # SSL/TLS inspection
│       └── network_cmd.py   # Network utilities
├── tests/
│   └── test_cli.py          # Test suite
├── pyproject.toml            # Package configuration
├── LICENSE                   # MIT License
├── CHANGELOG.md              # Version history
└── README.md                 # This file
```

## 🗺️ Roadmap

- [ ] `rex k8s` — Kubernetes context switcher & resource inspector
- [ ] `rex docker` — Docker image size analyzer & cleanup
- [ ] `rex env` — .env file encryption & diff
- [ ] `rex tf` — Terraform state inspector
- [ ] `rex log` — Log parser with pattern matching
- [ ] Plugin system for community extensions

## 📝 License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with 🦖 by [Merthan](https://github.com/DavidHayter)**

*If Rex saved you some time, consider giving it a ⭐*

</div>
