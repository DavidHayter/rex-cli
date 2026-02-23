# Changelog

All notable changes to Rex CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-23

### Added
- 🔐 **encrypt** — AES-256-GCM, ChaCha20-Poly1305, Fernet encryption/decryption
- 📋 **json** — Beautify, minify, validate, and query (JMESPath) JSON
- 📄 **yaml** — Lint, validate, YAML↔JSON conversion
- 🔑 **password** — Secure random passwords and passphrases
- ⏰ **cron** — Generate, explain, and list cron expression presets
- 🔒 **hash** — MD5, SHA-256, SHA-512, BLAKE2, HMAC generation and verification
- 📦 **base64** — Encode/decode with URL-safe variant support
- 🎫 **jwt** — Decode and inspect JWT tokens with expiry check
- 🆔 **uuid** — Generate UUID v1, v4, v5
- 📜 **cert** — SSL/TLS certificate inspection and expiry monitoring
- 🌐 **net** — DNS lookup, port scanning, ping
- Full stdin pipe support across all commands
- File input/output support for all data commands
- Rich terminal output with colored tables and panels
