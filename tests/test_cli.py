"""Basic tests for Rex CLI commands."""

import json
from typer.testing import CliRunner
from rex.cli import app

runner = CliRunner()


class TestVersion:
    def test_version(self):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Rex" in result.output

    def test_info(self):
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "Available Commands" in result.output


class TestJson:
    def test_beautify(self):
        result = runner.invoke(app, ["json", "beautify", '{"a":1,"b":2}'])
        assert result.exit_code == 0
        assert '"a"' in result.output

    def test_minify(self):
        result = runner.invoke(app, ["json", "minify", '{"a": 1, "b": 2}'])
        assert result.exit_code == 0

    def test_validate_valid(self):
        result = runner.invoke(app, ["json", "validate", '{"key": "value"}'])
        assert result.exit_code == 0
        assert "Valid" in result.output

    def test_validate_invalid(self):
        result = runner.invoke(app, ["json", "validate", '{invalid}'])
        assert result.exit_code == 1


class TestYaml:
    def test_validate(self):
        result = runner.invoke(app, ["yaml", "validate", "key: value"])
        assert result.exit_code == 0
        assert "Valid" in result.output

    def test_to_json(self):
        result = runner.invoke(app, ["yaml", "to-json", "name: rex\nversion: 1"])
        assert result.exit_code == 0


class TestPassword:
    def test_generate(self):
        result = runner.invoke(app, ["password", "generate"])
        assert result.exit_code == 0
        assert "Generated" in result.output

    def test_generate_count(self):
        result = runner.invoke(app, ["password", "generate", "--count", "5"])
        assert result.exit_code == 0

    def test_passphrase(self):
        result = runner.invoke(app, ["password", "passphrase"])
        assert result.exit_code == 0


class TestCron:
    def test_explain(self):
        result = runner.invoke(app, ["cron", "explain", "0 9 * * 1-5"])
        assert result.exit_code == 0
        assert "Minute" in result.output

    def test_presets(self):
        result = runner.invoke(app, ["cron", "presets"])
        assert result.exit_code == 0
        assert "daily" in result.output

    def test_generate_preset(self):
        result = runner.invoke(app, ["cron", "generate", "daily"])
        assert result.exit_code == 0


class TestHash:
    def test_sha256(self):
        result = runner.invoke(app, ["hash", "generate", "hello"])
        assert result.exit_code == 0

    def test_all_algorithms(self):
        result = runner.invoke(app, ["hash", "generate", "hello", "--all"])
        assert result.exit_code == 0
        assert "MD5" in result.output
        assert "SHA256" in result.output

    def test_verify_correct(self):
        import hashlib
        expected = hashlib.sha256(b"test").hexdigest()
        result = runner.invoke(app, ["hash", "verify", "test", "--expected", expected])
        assert result.exit_code == 0
        assert "matches" in result.output


class TestBase64:
    def test_encode(self):
        result = runner.invoke(app, ["base64", "encode", "hello world"])
        assert result.exit_code == 0
        assert "aGVsbG8gd29ybGQ=" in result.output

    def test_decode(self):
        result = runner.invoke(app, ["base64", "decode", "aGVsbG8gd29ybGQ="])
        assert result.exit_code == 0
        assert "hello world" in result.output


class TestUuid:
    def test_generate_v4(self):
        result = runner.invoke(app, ["uuid", "generate"])
        assert result.exit_code == 0

    def test_generate_v5(self):
        result = runner.invoke(app, ["uuid", "generate", "--version", "5", "--name", "example.com"])
        assert result.exit_code == 0

    def test_generate_count(self):
        result = runner.invoke(app, ["uuid", "generate", "--count", "3"])
        assert result.exit_code == 0


class TestJwt:
    def test_decode(self):
        # Test JWT (header.payload.signature)
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlJleCIsImlhdCI6MTUxNjIzOTAyMn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        result = runner.invoke(app, ["jwt", "decode", token])
        assert result.exit_code == 0
        assert "Rex" in result.output
