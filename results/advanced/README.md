# Advanced Diagnostics (DSCI441 Extension)

- Source run: `runs/20260225_155344__hgb-ordinal`
- Test samples analyzed: **44,900**

## New figures
- `mae_by_condition_hgb_ordinal.png`
- `mae_by_fuel_hgb_ordinal.png`
- `bias_by_price_decile_hgb_ordinal.png`
- `calibration_pred_vs_true_decile_hgb_ordinal.png`
- `mae_heatmap_condition_fuel_hgb_ordinal.png`
- `error_by_age_bucket_hgb_ordinal.png`

## Condition subgroup note
- Highest MAE subgroup in plotted condition set: `like new` with MAE **4726.3 USD**.
## Fuel subgroup note
- Highest MAE subgroup in plotted fuel set: `diesel` with MAE **6200.6 USD**.
## Price-scale behavior
- MAE increases from **1778.3 USD** (lowest decile) to **10089.4 USD** (highest decile).
## Decile calibration gap
- Mean absolute gap between decile-level predicted and true mean prices: **1225.2 USD**.

## Interpretation
- The best broad-domain model remains strong, but absolute-dollar error is not uniform across market segments.
- Segment-aware monitoring (condition/fuel/age) helps explain where residual risk is concentrated.
- Decile calibration and bias-by-price plots provide deployment-facing diagnostics beyond global RMSE/R².
