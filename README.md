# DTK Marketplace

DTK Marketplace is a generic catalog of reusable DTK configs.

## Layout

- Each top-level folder is a category or source.
- Nested folders are allowed when the source has meaningful variants, such as auth mode or account type.
- Each JSON file is one DTK config.

## Purpose

This repository is intended to act like a plugin catalog for DTK. The goal is to collect practical, reusable configs for real services and APIs without forcing them into a single format.

## Using a config

Each config is a JSON file that describes the source, request, and allowlist for a reusable DTK filter.

## Validation

Every pull request validates config structure, checks for literal credentials, and scans the
repository history with Gitleaks. Contributors only need to add or edit config JSON files.

```bash
python3 scripts/validate_marketplace.py
```

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the PR-based workflow.
