# Contributing

Contributions to this repository must arrive through pull requests, matching the workflow of the parent repository.

## Workflow

1. Create a branch or fork.
2. Add a new category folder or update an existing one.
3. Include one or more DTK config JSON files in that category.
4. Validate the config shape and naming before opening a PR.
5. Open a pull request for review.

Run the same validation used by CI:

```bash
python3 scripts/validate_marketplace.py
```

## Layout

- Category folders live at the repository root, for example `n8n/`.
- Config files should stay inside their category folder.
- Use descriptive file names that match the target source or endpoint.

## Config expectations

- Prefer reusable list or detail views over one-off payload slices.
- Keep the `allow` surface focused on the fields that matter for the use case.
- Include a short `notes` field when the intent is not obvious from the file name.
- Keep credentials in environment variables such as `$NOTION_TOKEN`; never include literal tokens,
  passwords, cookies, private keys, or authenticated URLs.

## hook_rule

The optional `hook_rule` field lets DTK automatically route matching shell commands
to this config without requiring the user to name the config explicitly.

```json
"hook_rule": {
  "command_prefix": "curl",
  "command_contains": ["api.github.com/repos/", "/issues"]
}
```

Fields:

- `command_prefix` — the start of the command string to match (literal, not a glob).
  When the prefix contains a shell variable such as `${N8N_BASE_URL%/}`, the prefix
  check is skipped at match time and `command_contains` carries the full burden.
- `command_contains` — a list of substrings that must all be present in the command
  string. Required and non-empty when `command_prefix` contains a `$`.
- `retention_days` — optional override for how long DTK keeps the stored payload.

Design guidelines:

- Use `command_prefix: "curl"` as a broad anchor and rely on `command_contains` for
  endpoint-level discrimination.
- For static base URLs (no env vars), include a unique URL path segment in
  `command_contains`, for example `"api.github.com/repos/"`.
- For endpoints where the URL contains a shell variable (such as
  `${VIKUNJA_BASE_URL%/}`), always set `command_contains` to at least one path
  segment and the auth env var name, for example `["/api/v1/projects", "$VIKUNJA_API_KEY"]`.
- To distinguish a list endpoint from a detail endpoint on the same path, append `?`
  (for list with query params) or `/` (for detail with an id segment), for example
  `"/commits?"` vs `"/commits/"`.
- To distinguish a sub-resource (such as issue timeline) from its parent list, add
  the sub-resource path segment as a third item so it scores higher in specificity
  sorting, for example `["/repos/", "/issues/", "/timeline"]`.
- Prefer discriminating by the path segment that uniquely identifies the endpoint
  rather than by request body, method flags, or query parameters that users may omit.
- When two configs share the same endpoint (such as alternative allowlists for the
  same URL), give them identical `hook_rule` values and document that they are
  alternatives; whichever is installed last wins routing.

Run `python3 scripts/validate_marketplace.py` to check `hook_rule` structure before
opening a pull request.

## Pull requests

- Keep related config changes together when they belong to the same source.
- Avoid unrelated formatting or structural churn.
- Add context in the PR description about what the config covers and why it belongs in the marketplace.
