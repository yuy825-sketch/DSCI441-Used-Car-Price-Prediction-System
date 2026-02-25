# DSCI441 Used Car Price Prediction — Report

This report summarizes:
- dataset QC/EDA (sample-based)
- regression baselines (OLS, Ridge, Lasso) and stronger variants
- evaluation metrics and residual diagnostics
- the Streamlit demo workflow

## 1) Dataset
Source: Craigslist vehicles dataset (Kaggle).

Local path (not committed):
`data/craigslist/vehicles.csv`

QC/EDA report:
- `project/data_qc/vehicles_eda.md` (generated on first 10k rows by `eda_analyzer.py`)

Quick dataset figures:
- `results/dataset/price_hist_logx.png`
- `results/dataset/price_vs_odometer.png`
- `results/dataset/manufacturer_top25.png`
- `results/dataset/corr_numeric.png`

## 2) Cleaning and features
Base features (see configs):
- numeric: `year`, `odometer`, derived `car_age`
- categorical: `manufacturer`, `condition`, `fuel`, `transmission`, `drive`, `type`, `paint_color`, `state`

Cleaning rules are configured in:
- `configs/*.json`

## 3) Models
Implemented models:
- OLS (LinearRegression)
- Ridge (alpha configurable)
- Lasso (alpha configurable)
- Ridge + TF-IDF(description) (text feature engineering)
- HistGradientBoostingRegressor (nonlinear baseline with ordinal-encoded categoricals)

Target transform:
- optional `log1p(price)` using `TransformedTargetRegressor` (`train.log_target`)

## 4) Metrics
Primary (test split):
- R²
- RMSE
- MAE

Aggregated table (generated after running experiments):
- `project/results/results_table.md`

## 5) Key plots (exported)
Export script:
- `scripts/export_latest.py` / `scripts/export_results.py`

Typical outputs under `results/`:
- `summary_<tag>.md`
- `true_vs_pred_<tag>.png`
- `residuals_hist_<tag>.png`
- `residuals_scatter_<tag>.png`
- `top_coeffs_<tag>.png` (if available)

## 6) Results (test)

From the runs executed on 2026-02-25:

| Tag | Model | R² | RMSE | MAE |
|---|---|---:|---:|---:|
| `ols` | OLS (one-hot cats) | 0.5834 | 9667.80 | 5689.79 |
| `ridge` | Ridge (alpha=5, one-hot cats) | 0.5835 | 9665.96 | 5684.14 |
| `lasso` | Lasso (alpha=5e-4, one-hot cats) | 0.5540 | 10002.64 | 5973.56 |
| `ridge_text_a20` | Ridge + TF-IDF(description) | 0.7275 | 7865.90 | 4416.09 |
| `hgb_ordinal` | HistGradientBoosting + ordinal cats | **0.8061** | 6649.38 | 3383.88 |

Goal check:
- Target: **R² > 0.80**
- Achieved by: `hgb_ordinal` (R²=0.8061)

## 7) Demo app
Run:
```
export DSCI441_DEMO_RUN_DIR="runs/<your_run_dir>"
streamlit run app/app.py
```
