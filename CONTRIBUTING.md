# Contributing

Contributions to this repository must arrive through pull requests, matching the workflow of the parent repository.

## Workflow

1. Create a branch or fork.
2. Add a new category folder or update an existing one.
3. Include one or more DTK config JSON files in that category.
4. Validate the config shape and naming before opening a PR.
5. Open a pull request for review.

## Layout

- Category folders live at the repository root, for example `n8n/`.
- Config files should stay inside their category folder.
- Use descriptive file names that match the target source or endpoint.

## Config expectations

- Prefer reusable list or detail views over one-off payload slices.
- Keep the `allow` surface focused on the fields that matter for the use case.
- Include a short `notes` field when the intent is not obvious from the file name.

## Pull requests

- Keep related config changes together when they belong to the same source.
- Avoid unrelated formatting or structural churn.
- Add context in the PR description about what the config covers and why it belongs in the marketplace.
