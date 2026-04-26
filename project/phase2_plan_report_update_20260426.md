# Phase 2 Plan — Report Integration for Advanced Diagnostics

Date: 2026-04-26

## Objective

Integrate the new `results/advanced/` findings into `results/REPORT.md` while preserving all existing sections and conclusions.

## Planned Updates

1. Add a dedicated section for advanced post-hoc diagnostics:
   - subgroup MAE (`condition`, `fuel`)
   - decile error profile
   - decile calibration view
   - segment heatmap and age-bucket behavior
2. Reference the new figures via relative paths (`advanced/*.png`).
3. Add interpretation focused on deployment implications and segment-aware monitoring.
4. Keep prior baseline/model-comparison narrative intact.

## Acceptance

- Existing content is preserved; only additive extension text/figures are added.
- Report references at least 4 new advanced figures.
- Report remains readable and consistent with existing numbering/style.

