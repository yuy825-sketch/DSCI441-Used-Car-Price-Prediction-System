# Submission Readiness Check — 2026-04-26

Scope: final verification after DSCI441 upgrade phases (advanced diagnostics, report update, docs web app, poster workflow).

## 1) Repository hygiene

- `git ls-files info.md` -> no output (PASS, `info.md` is not tracked).
- Phase outputs are committed with English commit messages and pushed via SSH remote.

## 2) Advanced extension outputs

- New diagnostics figure count:
  - `find results/advanced -name '*.png' | wc -l` -> `6` (PASS, requirement >= 4).
- Advanced diagnostics CLI sanity:
  - `.venv/bin/python scripts/advanced_diagnostics.py --help` returns usage text (PASS).

## 3) Report integration

- `results/REPORT.md` contains extension section:
  - `## 10. Advanced post-hoc diagnostics (extension)` (PASS).
- Report key takeaways mention the extension findings (PASS).

## 4) GitHub Pages static web app

- Entry pages exist:
  - `docs/index.html`
  - `docs/results.html`
- Link/resource path check on local html references found no missing files (PASS).
- Docs asset count:
  - `find docs/assets -type f | wc -l` -> `14`.

## 5) Poster workflow

- Poster artifacts present:
  - `presentation/poster_web_441/UsedCarPricePoster441.html`
  - `presentation/poster_web_441/UsedCarPricePoster441.pdf`
- PDF check:
  - `pdfinfo .../UsedCarPricePoster441.pdf` -> `Pages: 1`, `Page size: A4` (PASS).

## 6) Residual notes

- Checks were focused on packaging integrity and deliverable readiness.
- Full retraining was not re-run in this final check because the extension figures are already generated and versioned.
