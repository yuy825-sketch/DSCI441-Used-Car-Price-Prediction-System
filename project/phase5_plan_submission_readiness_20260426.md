# Phase 5 Plan — Submission Readiness and Repository Hygiene

Date: 2026-04-26

## Objective

Finalize the upgraded DSCI441 repository with explicit integrity checks, deployment-entry verification, and commit hygiene checks before close-out.

## Planned Checks

1. Repository hygiene
   - Confirm clean git state after all pushes.
   - Confirm `info.md` is not tracked.

2. Deliverable completeness
   - Verify report contains extension diagnostics section and references new figures.
   - Verify at least 4 new extension figures exist under `results/advanced/`.
   - Verify GitHub Pages site files resolve (`docs/index.html`, `docs/results.html`, assets).
   - Verify poster artifacts exist (`presentation/poster_web_441/` HTML + PDF).

3. Functional sanity
   - Run lightweight script checks for advanced diagnostics CLI help.
   - Run docs link/path integrity check script.
   - Verify poster PDF metadata/page count.

4. Documentation trail
   - Write a dated check log under `project/` with pass/fail notes and quick evidence.

## Acceptance

- All required upgraded artifacts are present and linked.
- `info.md` remains local-only and untracked.
- Check log is committed and pushed with an English commit message.
