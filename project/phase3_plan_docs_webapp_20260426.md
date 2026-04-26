# Phase 3 Plan — GitHub Pages Static Web App (DSCI441)

Date: 2026-04-26

## Objective

Build a GitHub-deployable static website in `docs/` that presents the DSCI441 project as a polished web app companion, while preserving the existing Streamlit app.

## Planned Outputs

1. `docs/index.html` (primary project page)
2. `docs/results.html` (deeper metrics/diagnostics page)
3. `docs/styles.css` + `docs/script.js`
4. `docs/assets/` with copied figure assets required for standalone GitHub Pages rendering
5. README links to docs entry points

## UX/Content Requirements

- Clear sections for:
  - problem framing,
  - dataset signal,
  - model comparison,
  - advanced diagnostics,
  - demo/deployment.
- Include static interactive elements (precomputed/fixed values) compatible with GitHub Pages.
- Ensure all links are relative and valid inside `docs/`.
- Keep style distinct from DSCI498 site.

## Validation

- `index.html` and `results.html` load locally with all assets.
- No broken links for local docs files.
- Existing Streamlit app remains untouched and still documented.

