# DSCI441 Used Car Price Prediction System

This repository contains an end-to-end **regression** project for predicting **used car prices** from listing attributes, with a small **Streamlit demo app**.

Quick links:
- Full report: [`results/REPORT.md`](results/REPORT.md)
- Results index: [`results/README.md`](results/README.md)
- Figure index (what each image means): [`results/FIGURES.md`](results/FIGURES.md)

## Project goals (from `info.md`)
- Implement and compare multiple regression models (**OLS**, **Ridge**, **Lasso**)
- Perform feature engineering and (limited) multicollinearity analysis
- Evaluate with **R²**, **RMSE**, **MAE** on a held-out test split
- Deliver a simple **Streamlit** web app for real-time price prediction
- Visualize **coefficients/feature effects** and **residual diagnostics**

## Dataset + results (visual)

Pipeline overview:

![Pipeline overview](results/pipeline_overview.png)

Dataset highlights (heavy-tailed price + missingness):

![Price distribution](results/dataset/price_hist_logx.png)

![Missingness](results/dataset/missingness_top20.png)

Model comparison (test metrics):

![Model comparison (R²)](results/model_comparison_r2.png)

![Model comparison (RMSE)](results/model_comparison_rmse.png)

Best overall model diagnostics (`hgb_ordinal`):

![True vs predicted (hgb_ordinal)](results/true_vs_pred_hgb_ordinal.png)

![Permutation importance (hgb_ordinal)](results/perm_importance_hgb_ordinal.png)

## Disclaimer
This is a course project for educational purposes only. It is **not** financial advice.

## Dataset
I use the **Craigslist Cars & Trucks** dataset (Kaggle).

Recommended sources:
- https://www.kaggle.com/datasets/austinreese/craigslist-carstrucks-data

Expected local layout (not committed):
```
data/craigslist/
  vehicles.csv
```

Download helper (requires Kaggle API credentials):
```
.venv/bin/python scripts/download_kaggle_dataset.py
```
Credentials options:
- Preferred: `KAGGLE_API_TOKEN` (env) or `~/.kaggle/kaggle_api_token`
- Legacy: `~/.kaggle/kaggle.json` or `KAGGLE_USERNAME`/`KAGGLE_KEY`

## Setup
Create an environment (conda/venv) and install dependencies:
```
pip install -r requirements.txt
pip install -e .
```

Quick smoke test (no dataset required):
```
.venv/bin/python -m dsci441_used_car.smoke
```

## Train / Evaluate
Training produces a local run folder under `runs/` with:
- `model.joblib`, `metrics.json`, `test_outputs.npz`, `coefficients.json`

Example (after placing the CSV under `data/craigslist/vehicles.csv`):
```
.venv/bin/python train.py --config configs/baseline_ols.json --run-name ols
.venv/bin/python train.py --config configs/ridge.json --run-name ridge
.venv/bin/python train.py --config configs/lasso.json --run-name lasso
```

One-command baseline run (EDA + models + exports + results table):
```
.venv/bin/python scripts/run_baselines.py
```

### Current best (meets project target)
I can achieve **R² > 0.80** on the test split with a nonlinear model:
- `HistGradientBoostingRegressor` with ordinal-encoded categoricals (config: `configs/hgb_ordinal.json`)

## Export results (figures + summary)
```
.venv/bin/python scripts/export_latest.py
```
Outputs (written to `results/`):
- `summary.md`
- `true_vs_pred.png`
- `residuals_hist.png`
- `residuals_scatter.png`
- `top_coeffs.png` (if available)

## Dataset diagnostics (optional)
Generate quick EDA-style figures and multicollinearity checks:
```
.venv/bin/python scripts/check_dataset.py
.venv/bin/python scripts/dataset_viz.py
.venv/bin/python scripts/vif_analysis.py
```

## Error analysis (optional)

For additional visuals on error distribution and how error scales with price:
```
.venv/bin/python scripts/error_analysis.py --run-dir runs/<your_run_dir> --out-dir results --tag my_run
```

## Demo app (Streamlit)
Run:
```
streamlit run app/app.py
```

Set the environment variable to point to a trained run directory:
```
export DSCI441_DEMO_RUN_DIR="runs/<your_run_dir>"
```
