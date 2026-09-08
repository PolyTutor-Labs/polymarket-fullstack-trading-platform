#!/usr/bin/env python3
"""Lightweight pre-publication secret scan for PolyTutor.

This is a basic safeguard, not a replacement for GitHub secret scanning,
gitleaks, or trufflehog. It never prints matched credential values.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SKIP_DIRS = {
    ".git",
    "node_modules",
    ".next",
    "out",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    ".idea",
    ".vscode",
    "logs",
    ".playwright-mcp",
    ".codex",
    "output",
    "_DataMetricPulls",
}

PLACEHOLDER_VALUES = {
    "",
    "...",
    "xxx",
    "changeme",
    "change-me",
    "placeholder",
    "example",
    "dummy",
    "fake",
    "todo",
    "null",
    "none",
    "true",
    "false",
    "your_api_key_here",
    "your-api-key-here",
}

PLACEHOLDER_SUBSTR = (
    "your_",
    "example",
    "placeholder",
    "changeme",
    "dummy",
    "fake",
    "todo",
    "replace_me",
    "insert_",
    "xxxx",
    "localhost",
)

# High-risk assignment names. Require a real-looking value, not the word alone.
ASSIGNMENT_PATTERNS = (
    (
        "possible private-key assignment",
        re.compile(
            r"(?i)\b(?:POLYMARKET_)?PRIVATE_KEY\s*[=:]\s*['\"]?"
            r"(0x[a-fA-F0-9]{64}|[a-fA-F0-9]{64})\b"
        ),
    ),
    (
        "possible seed phrase / mnemonic assignment",
        re.compile(
            r"(?i)\b(?:MNEMONIC|SEED_PHRASE|SEED_PHRASE_WORDS)\s*[=:]\s*['\"]"
            r"([a-z]+(?:\s+[a-z]+){11,23})['\"]"
        ),
    ),
    (
        "possible Supabase service-role key assignment",
        re.compile(
            r"(?i)\bSUPABASE_SERVICE(?:_ROLE)?_KEY\s*[=:]\s*['\"]?"
            r"(eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,})"
        ),
    ),
    (
        "possible committed API-secret assignment",
        re.compile(
            r"(?i)\b(?:POLYMARKET_SECRET|POLYMARKET_PASSPHRASE|API_SECRET|"
            r"CLIENT_SECRET|WEBHOOK_SECRET)\s*[=:]\s*['\"]"
            r"([A-Za-z0-9_\-+/=]{24,})['\"]"
        ),
    ),
)

BEARER_RE = re.compile(
    r"(?i)(?:Authorization\s*[:=]\s*['\"]?Bearer|Bearer)\s+"
    r"([A-Za-z0-9_\-\.]{32,})"
)

PEM_RE = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")

MAX_FILE_BYTES = 2_000_000


def is_placeholder(value: str) -> bool:
    cleaned = value.strip().strip("'\"").rstrip(".")
    if cleaned.lower() in PLACEHOLDER_VALUES:
        return True
    lower = cleaned.lower()
    if any(token in lower for token in PLACEHOLDER_SUBSTR):
        return True
    if len(cleaned) < 16:
        return True
    return False


def looks_binary(sample: bytes) -> bool:
    if b"\x00" in sample:
        return True
    return False


def iter_files() -> tuple[list[Path], int]:
    scanned: list[Path] = []
    skipped = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            try:
                size = path.stat().st_size
            except OSError:
                skipped += 1
                continue
            if size > MAX_FILE_BYTES:
                skipped += 1
                continue
            scanned.append(path)
    return scanned, skipped


def scan_text(rel: str, text: str, findings: list[str]) -> None:
    if PEM_RE.search(text):
        findings.append(f"{rel} — possible private-key block")

    for label, pattern in ASSIGNMENT_PATTERNS:
        for match in pattern.finditer(text):
            value = match.group(1)
            if is_placeholder(value):
                continue
            line_no = text.count("\n", 0, match.start()) + 1
            findings.append(f"{rel}:{line_no} — {label}")

    for match in BEARER_RE.finditer(text):
        value = match.group(1)
        if is_placeholder(value) or value.startswith("{") or value.startswith("$"):
            continue
        line_no = text.count("\n", 0, match.start()) + 1
        findings.append(f"{rel}:{line_no} — possible Bearer token")


def main() -> int:
    files, skipped = iter_files()
    findings: list[str] = []
    scanned = 0
    text_skipped = 0

    for path in files:
        try:
            raw = path.read_bytes()
        except OSError:
            text_skipped += 1
            continue
        if looks_binary(raw[:8192]):
            text_skipped += 1
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = raw.decode("latin-1")
            except UnicodeDecodeError:
                text_skipped += 1
                continue
        scanned += 1
        rel = path.relative_to(ROOT).as_posix()
        scan_text(rel, text, findings)

    skipped += text_skipped
    print(f"Files scanned: {scanned}")
    print(f"Files skipped: {skipped}")

    if findings:
        print("Secret scan: FAIL")
        print(f"{len(findings)} suspicious findings.")
        print()
        for item in findings:
            print(item)
        return 1

    print("Secret scan: PASS")
    print("0 suspicious committed secrets found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
