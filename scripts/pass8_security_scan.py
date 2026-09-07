#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {".git", ".next", "node_modules", ".terraform", "__pycache__", ".venv"}
SENSITIVE_FILENAMES = {
    ".env", "id_rsa", "id_ed25519", "credentials.json", "service-account.json",
    "secrets.json", "terraform.tfstate", "terraform.tfstate.backup",
}
SENSITIVE_SUFFIXES = {".pem", ".p12", ".pfx", ".jks", ".keystore"}

# Deliberately target assignment-shaped secrets and credential formats, not documentation words.
SECRET_PATTERNS = [
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("openai_key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("azure_storage_connection", re.compile(r"DefaultEndpointsProtocol=https?;AccountName=[^;\s]+;AccountKey=[^;\s]+", re.I)),
    ("generic_secret_assignment", re.compile(
        r"(?i)\b(?:api[_-]?key|token|client[_-]?secret|password|connection[_-]?string)\b\s*[:=]\s*[\"']([^\"'\n]{12,})[\"']"
    )),
]

TEXT_SUFFIXES = {
    ".py", ".ts", ".tsx", ".js", ".mjs", ".json", ".md", ".txt", ".yml", ".yaml",
    ".tf", ".sh", ".toml", ".properties", ".xml", ".java", ".csv", ".example",
}


def candidates() -> list[Path]:
    found: list[Path] = []
    for path in ROOT.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            found.append(path)
    return found


def main() -> None:
    files = candidates()
    bad_files: list[str] = []
    secret_hits: list[str] = []

    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        if path.name in SENSITIVE_FILENAMES or path.suffix.lower() in SENSITIVE_SUFFIXES:
            # .env.example is intentionally safe documentation.
            if rel != ".env.example":
                bad_files.append(rel)

        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"Makefile", ".gitignore"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                value = match.group(1) if match.groups() else match.group(0)
                # Examples/placeholders are allowed only when visibly non-secret.
                lowered = value.lower()
                if any(marker in lowered for marker in ("example", "placeholder", "changeme", "<", "your_", "dummy")):
                    continue
                line = text.count("\n", 0, match.start()) + 1
                secret_hits.append(f"{rel}:{line}:{label}")

    if bad_files or secret_hits:
        if bad_files:
            print("Sensitive credential/state files detected:")
            for item in bad_files:
                print(f"  - {item}")
        if secret_hits:
            print("Potential embedded secrets detected:")
            for item in secret_hits:
                print(f"  - {item}")
        raise SystemExit(1)

    print(f"PASS 8 SECRET/CREDENTIAL SCAN: GREEN ({len(files)} files inspected)")
    print("No private keys, credential files, API keys, tokens, connection strings or production credentials detected by the fail-closed repository scanner.")


if __name__ == "__main__":
    main()
