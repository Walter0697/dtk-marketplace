#!/usr/bin/env python3
"""Validate DTK marketplace configs."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SENSITIVE_HEADER = re.compile(
    r"(?i)(authorization|x-api-key|api-key|x-auth-token|cookie)\s*:\s*([^\"'\s]+(?:\s+[^\"'\s]+)?)"
)
SENSITIVE_QUERY = re.compile(
    r"(?i)[?&](?:access_token|api_key|apikey|key|secret|token|password)=([^&\"'\s]+)"
)
PRIVATE_KEY = re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----")
AUTHENTICATED_URL = re.compile(r"https?://[^/\s:@]+:[^/\s@]+@")
SAFE_REFERENCE = re.compile(r"^(?:Bearer\s+|Basic\s+)?(?:\$[A-Z_][A-Z0-9_]*|\$\{[^}]+\}|<[^>]+>)$")

VALID_FORMATS = {"json", "yaml", "toml", "hcl", "csv", "ini", "xml", "xaml"}
HOOK_RULE_KEYS = {"command_prefix", "command_contains", "retention_days"}


def config_paths() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.json")
        if ".git" not in path.parts
    )


def is_safe_reference(value: str) -> bool:
    return bool(SAFE_REFERENCE.fullmatch(value.strip()))


def validate_request(path: Path, request: str, errors: list[str]) -> None:
    if PRIVATE_KEY.search(request):
        errors.append(f"{path}: request contains a private key")
    if AUTHENTICATED_URL.search(request):
        errors.append(f"{path}: request must not contain credentials in a URL")
    for match in SENSITIVE_HEADER.finditer(request):
        value = match.group(2)
        if not is_safe_reference(value):
            errors.append(
                f"{path}: sensitive header {match.group(1)!r} must use an environment variable or placeholder"
            )
    for match in SENSITIVE_QUERY.finditer(request):
        value = match.group(1)
        if not is_safe_reference(value):
            errors.append(
                f"{path}: sensitive query parameter must use an environment variable or placeholder"
            )


def validate_hook_rule(path: Path, hook_rule: object, errors: list[str]) -> None:
    if not isinstance(hook_rule, dict):
        errors.append(f"{path}: hook_rule must be an object")
        return
    unknown = set(hook_rule) - HOOK_RULE_KEYS
    if unknown:
        errors.append(f"{path}: hook_rule has unknown keys: {sorted(unknown)}")
    prefix = hook_rule.get("command_prefix")
    if prefix is not None and not isinstance(prefix, str):
        errors.append(f"{path}: hook_rule.command_prefix must be a string")
    contains = hook_rule.get("command_contains")
    if contains is not None:
        if not isinstance(contains, list) or not all(isinstance(s, str) for s in contains):
            errors.append(f"{path}: hook_rule.command_contains must be an array of strings")
    retention = hook_rule.get("retention_days")
    if retention is not None and not isinstance(retention, int):
        errors.append(f"{path}: hook_rule.retention_days must be an integer")
    if isinstance(prefix, str) and "$" in prefix:
        if not contains:
            errors.append(
                f"{path}: hook_rule.command_prefix contains '$' so "
                "hook_rule.command_contains must be non-empty"
            )


def validate_configs() -> tuple[list[str], int]:
    errors: list[str] = []
    seen_ids: dict[str, Path] = {}
    count = 0

    for path in config_paths():
        count += 1
        relative = path.relative_to(ROOT).as_posix()
        if len(path.relative_to(ROOT).parts) < 2:
            errors.append(f"{relative}: configs must live inside a category folder")
        try:
            raw = path.read_bytes()
            config = json.loads(raw)
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{relative}: invalid JSON: {error}")
            continue
        if not isinstance(config, dict):
            errors.append(f"{relative}: config root must be an object")
            continue

        config_id = config.get("id") or config.get("name")
        if not isinstance(config_id, str) or not config_id.strip():
            errors.append(f"{relative}: id or name is required")
            continue
        if path.stem != config_id:
            errors.append(f"{relative}: filename must match config id {config_id!r}")
        if config.get("id") and config.get("name") and config["id"] != config["name"]:
            errors.append(f"{relative}: id and name must match when both are present")
        if config_id in seen_ids:
            errors.append(f"{relative}: duplicate id also used by {seen_ids[config_id]}")
        else:
            seen_ids[config_id] = path

        source = config.get("source")
        if not isinstance(source, str) or not source.strip():
            errors.append(f"{relative}: source is required")
        request = config.get("request")
        if not isinstance(request, str) or not request.strip():
            errors.append(f"{relative}: request is required")
        else:
            validate_request(Path(relative), request, errors)
        allow = config.get("allow")
        if not isinstance(allow, list) or not all(isinstance(item, str) for item in allow):
            errors.append(f"{relative}: allow must be an array of strings")
        fmt = config.get("format")
        if fmt is not None:
            if not isinstance(fmt, str):
                errors.append(f"{relative}: format must be a string")
            elif fmt not in VALID_FORMATS:
                errors.append(f"{relative}: unknown format {fmt!r}, expected one of {sorted(VALID_FORMATS)}")
        if "notes" in config and not isinstance(config["notes"], str):
            errors.append(f"{relative}: notes must be a string")
        if "hook_rule" in config:
            validate_hook_rule(Path(relative), config["hook_rule"], errors)

    return errors, count


def main() -> int:
    errors, count = validate_configs()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print(f"validated {count} marketplace configs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
