# DSCI441 Upgrade Plan (Aligned with DSCI498 Quality)

Date: 2026-04-26

Scope: Extend the existing DSCI441 project **without removing or rewriting existing core content**. Add new analysis outputs, expand report coverage, build a GitHub-deployable static web app, and produce a new poster workflow with a visual style distinct from DSCI498.

## Execution Policy

- Keep existing files and conclusions intact; append/extend only.
- `info.md` is local guidance and must not be committed.
- Execute in explicit phases. Each completed phase requires:
  - local validation/check,
  - quality pass,
  - English commit message,
  - SSH push to `origin/main`.

## Phase 1 — Advanced Analysis Extension

Goal: add post-hoc diagnostics and **at least 4 new figures**.

Planned outputs:
- New script(s) under `scripts/` for advanced diagnostics.
- New result directory `results/advanced/` with:
  - >=4 new figures,
  - one markdown summary for interpretation.
- Update figure index/documentation to include new assets.

Candidate diagnostics (final set may vary after implementation checks):
- Error by subgroup (`condition`, `fuel`, manufacturer buckets).
- Prediction bias by price decile.
- Error concentration heatmap for key segments.
- Coverage/threshold-style reliability for regression use-case.

Acceptance:
- New figures are generated reproducibly from current runs/data.
- Existing outputs remain untouched and valid.

## Phase 2 — Report Upgrade

Goal: update `results/REPORT.md` to include the new advanced findings.

Planned updates:
- Add a new section for post-hoc diagnostics (methods + visuals + interpretation).
- Add practical deployment implications for price-range/domain behavior.
- Update references inside report to new figures.

Acceptance:
- Report remains coherent and additive (no loss of previous content).
- New section explicitly references new figures and metrics.

## Phase 3 — GitHub Pages Web App (Static Deployment)

Goal: provide a GitHub-deployable static project site under `docs/`.

Planned outputs:
- `docs/index.html` and support assets/CSS/JS.
- Result galleries and interpreted findings.
- Static interactive components (precomputed examples) compatible with GitHub Pages constraints.
- README entry links to the docs site.

Acceptance:
- All local links/resources under `docs/` resolve.
- Site structure supports project overview + results + demo narrative.

## Phase 4 — Poster Build (DSCI498-style workflow, new visual identity)

Goal: produce a one-page poster via HTML-first workflow, with different style/color direction from DSCI498.

Planned outputs:
- New poster source in `presentation/poster_web_441/`.
- Poster includes required sections:
  - Problem Description/Motivation
  - Dataset Description
  - Experiments/Model Selection
  - Evaluation
- Design tuned for print/export consistency.

Acceptance:
- Poster content is complete and visually balanced.
- Visual theme differs from DSCI498 while maintaining quality.

## Phase 5 — Submission-Readiness and Repo Hygiene

Goal: verify deliverable consistency and finalize repository state.

Checklist:
- Confirm required entry files and links are present.
- Verify no accidental commit of local-only guidance (`info.md`) or restricted files.
- Run quick integrity checks for new scripts/pages.
- Final push after cleanup.

Acceptance:
- Repo is clean (`git status` clean) after final push.
- New extensions are traceable and documented.

## Commit Plan (minimum)

1. `docs(plan): add DSCI441 upgrade execution plan`
2. `feat(analysis): add advanced diagnostics and new figures`
3. `docs(report): integrate advanced findings into report`
4. `feat(docs): add github pages static web app`
5. `feat(poster): add new poster workflow and assets`
6. `chore(repo): final submission-readiness checks`

