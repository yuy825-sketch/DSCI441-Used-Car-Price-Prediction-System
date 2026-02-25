# DSCI441 Used Car Price Prediction — Report

This report summarizes:
- dataset QC/EDA (sample-based)
- regression baselines (OLS, Ridge, Lasso)
- evaluation metrics and residual diagnostics
- the Streamlit demo workflow

## 1) Dataset
Source: Craigslist vehicles dataset (Kaggle).

Local path (not committed):
`data/craigslist/vehicles.csv`

QC/EDA report:
- `project/data_qc/vehicles_eda.md` (generated on first 10k rows by `eda_analyzer.py`)

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

## 6) Demo app
Run:
```
export DSCI441_DEMO_RUN_DIR="runs/<your_run_dir>"
streamlit run app/app.py
```

