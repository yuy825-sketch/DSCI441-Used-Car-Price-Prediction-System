# Phase 1 Plan — Advanced Diagnostics Extension (DSCI441)

Date: 2026-04-26

## Objective

Add post-hoc diagnostics to the existing used-car price project **without removing prior outputs**, and generate at least 4 new result figures for report integration.

## Inputs

- Best broad-domain run:
  - `runs/20260225_155344__hgb-ordinal/`
- Dataset:
  - `data/craigslist/vehicles.csv`
- Existing report and figure index:
  - `results/REPORT.md`
  - `results/FIGURES.md`

## Planned Deliverables

1. New script:
   - `scripts/advanced_diagnostics.py`
2. New output folder:
   - `results/advanced/`
3. New figures (minimum 4, target 5):
   - `mae_by_condition_hgb_ordinal.png`
   - `mae_by_fuel_hgb_ordinal.png`
   - `bias_by_price_decile_hgb_ordinal.png`
   - `calibration_pred_vs_true_decile_hgb_ordinal.png`
   - `mae_heatmap_condition_fuel_hgb_ordinal.png`
4. New markdown summary:
   - `results/advanced/README.md`

## Execution Steps

1. Reconstruct the same cleaned dataset and train/test split from run config.
2. Load the trained model from run directory and regenerate test predictions.
3. Build subgroup/error diagnostics tables.
4. Render and save plots into `results/advanced/`.
5. Write concise interpretation notes in `results/advanced/README.md`.

## Validation

- Script executes without failure using local environment.
- All planned output files are generated.
- Existing report/results files remain intact before Phase 2.
- `git status` contains only additive extension changes for this phase.

