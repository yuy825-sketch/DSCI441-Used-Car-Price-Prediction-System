# Project Report — Used Car Price Prediction System (DSCI 441)

This report is written for course submission. It documents the dataset, methods, experiments, results, analysis, and a runnable demo app.

## Abstract

This project predicts **used car listing prices (USD)** from structured Craigslist listing attributes using regression-style supervised learning. I start with linear baselines (**OLS**, **Ridge**, **Lasso**) and add two stronger variants: (i) **Ridge + TF‑IDF(description)** to incorporate unstructured listing text, and (ii) a nonlinear **HistGradientBoostingRegressor** with **ordinal-encoded categoricals** to capture interactions and nonlinearities common in the used‑car market.

On the fixed train/test split used throughout, the best overall model (`hgb_ordinal`) achieves **test R² = 0.8061** and reduces test error compared to linear baselines. Because the target distribution is heavy‑tailed and error grows with vehicle price (heteroskedasticity), I also report a “mid‑market” evaluation regime (filtered price range) that meets the milestone RMSE target (< $3,000) while illustrating the trade‑off between global performance and operating domain.

## Table of contents

- [1. Problem statement](#1-problem-statement)
- [2. Dataset](#2-dataset)
- [3. Data cleaning and feature engineering](#3-data-cleaning-and-feature-engineering)
- [4. Models](#4-models)
- [5. Experimental setup](#5-experimental-setup)
- [6. Results and comparison](#6-results-and-comparison)
- [7. Diagnostics and error analysis](#7-diagnostics-and-error-analysis)
- [8. Feature effects and importance](#8-feature-effects-and-importance)
- [9. Multicollinearity note](#9-multicollinearity-note)
- [10. Demo app (Streamlit)](#10-demo-app-streamlit)
- [11. Reproducibility](#11-reproducibility)
- [12. Limitations and ethical note](#12-limitations-and-ethical-note)
- [13. Conclusion](#13-conclusion)
- [14. References](#14-references)

## 1. Problem statement

Used car pricing is noisy and depends on many interacting factors (vehicle age, mileage, manufacturer, condition, etc.). The goal is to build a regression model that:
- predicts a reasonable price estimate from listing attributes,
- supports model validation via residual diagnostics,
- and is packaged as a small **interactive demo** (Streamlit) for course presentation.

High-level system view:

![Pipeline overview](pipeline_overview.png)

## 2. Dataset

**Source**: Kaggle — “Craigslist Cars & Trucks” dataset.

Local path (not committed):
- `data/craigslist/vehicles.csv`

The dataset has a large number of listings with mixed numeric + categorical columns and substantial missingness in several categorical features. I generate a sample-based QC/EDA report with the Codex EDA analyzer:
- `project/data_qc/vehicles_eda.md` (10k-row sample)

### 2.1 EDA highlights (figures)

Price is heavy-tailed:

![Price distribution](dataset/price_hist_logx.png)

Mileage is also long-tailed:

![Odometer distribution](dataset/odometer_hist.png)

Newer model years tend to have higher prices:

![Price by year](dataset/price_by_year.png)

Missingness is non-trivial for some columns:

![Missingness](dataset/missingness_top20.png)

## 3. Data cleaning and feature engineering

Cleaning is handled in `src/dsci441_used_car/data.py` and configured via `configs/*.json`. Key steps:
- Coerce `price`, `year`, `odometer`, `lat`, `long` to numeric (drop invalid target rows).
- Filter implausible values (price bounds, year bounds, odometer bounds).
- Replace empty strings / `"unknown"` with missing values to standardize imputation behavior.

Derived features:
- `car_age = max_year - year`
- `miles_per_year = odometer / max(car_age, 1)`

Target transform:
- Most configs enable `log1p(price)` via `TransformedTargetRegressor` to reduce the impact of the high-price tail while still evaluating metrics on the **original USD scale**.

## 4. Models

Implemented models (see `configs/`):

### 4.1 Linear baselines
- **OLS**: `LinearRegression`
- **Ridge**: `Ridge(alpha=...)` (L2 regularization)
- **Lasso**: `Lasso(alpha=...)` (L1 regularization)

Categoricals are one-hot encoded for linear models. Coefficient plots are exported to help interpret feature directionality.

### 4.2 Text-augmented linear model
- **Ridge + TF‑IDF(description)**: adds a sparse TF‑IDF vector from listing descriptions (`ngram_range=(1,2)`).

This tests whether unstructured text contains pricing signals beyond the structured columns.

### 4.3 Nonlinear model
- **HistGradientBoostingRegressor** with **ordinal encoding** for categoricals.

Motivation: used-car prices exhibit nonlinear patterns and interactions (e.g., mileage effects differ by model year / manufacturer). Tree-based boosting captures these effects better than pure linear models.

## 5. Experimental setup

### 5.1 Split and sampling

All results use:
- Train/test split: `test_size = 0.2`, `seed = 441`
- Sample-based training (for runtime): `sample_n` from config (typically 120k–250k rows after initial sampling, then further reduced by cleaning filters).

### 5.2 Metrics

On the **test split**, I report:
- R²
- RMSE (USD)
- MAE (USD)

## 6. Results and comparison

The repo commits a small set of presentation-ready outputs under `results/`:
- `model_comparison.csv` (auto-generated)
- `model_comparison_r2.png`
- `model_comparison_rmse.png`
- plus per-run summaries and diagnostics (tagged files).

### 6.1 Overall comparison (best R²)

![Model comparison (R²)](model_comparison_r2.png)

### 6.2 Error comparison (RMSE)

![Model comparison (RMSE)](model_comparison_rmse.png)

### 6.3 Result table (test)

Values below match `results/model_comparison.csv`:

| Tag | Model | Test R² | Test RMSE | Test MAE |
|---|---|---:|---:|---:|
| `hgb_midmarket_60k` | HGB (ordinal cats), filtered domain | 0.8525 | 4981.00 | 3014.91 |
| `hgb_ordinal` | HGB (ordinal cats) | **0.8061** | 6649.38 | 3383.88 |
| `hgb_midmarket_30k` | HGB (ordinal cats), filtered domain | 0.8019 | 3654.52 | 2360.37 |
| `ridge_text_a20` | Ridge + TF‑IDF(description) | 0.7275 | 7865.90 | 4416.09 |
| `hgb_midmarket_20k` | HGB (ordinal cats), filtered domain | 0.7024 | **2935.79** | 1972.39 |
| `ridge` | Ridge (one-hot cats) | 0.5835 | 9665.96 | 5684.14 |
| `ols` | OLS (one-hot cats) | 0.5834 | 9667.80 | 5689.79 |
| `lasso` | Lasso (one-hot cats) | 0.5540 | 10002.64 | 5973.56 |

Goal check from `info.md`:
- R² target (**> 0.80**): achieved by `hgb_ordinal`.
- RMSE target (**< $3,000**): achieved in a filtered operating domain by `hgb_midmarket_20k` (see discussion in [§12](#12-limitations-and-ethical-note)).

## 7. Diagnostics and error analysis

### 7.1 Best overall model (`hgb_ordinal`)

True vs predicted:

![True vs predicted (hgb_ordinal)](true_vs_pred_hgb_ordinal.png)

Residual diagnostics:

![Residual histogram (hgb_ordinal)](residuals_hist_hgb_ordinal.png)

![Residuals vs predicted (hgb_ordinal)](residuals_scatter_hgb_ordinal.png)

### 7.2 Error distribution and heteroskedasticity

The error plots show that absolute dollar error generally grows with price, consistent with a heavy-tailed target:

![Abs error histogram](error_abs_hist_hgb_ordinal.png)

![Abs error vs true price](error_abs_by_true_hgb_ordinal.png)

Additional per-run error summaries:
- `error_analysis_hgb_ordinal.md`
- `error_analysis_ridge_text_a20.md`
- `error_analysis_hgb_midmarket_20k.md`

## 8. Feature effects and importance

### 8.1 Permutation importance (best model)

![Permutation importance (hgb_ordinal)](perm_importance_hgb_ordinal.png)

Key takeaway: the model relies heavily on age/mileage signals plus a set of categorical attributes (manufacturer/type/state/condition), combining multiple complementary factors.

### 8.2 Text feature contribution

The Ridge+TF‑IDF experiment demonstrates that `description` adds measurable value:

![Permutation importance (ridge_text_a20)](perm_importance_ridge_text_a20.png)

## 9. Multicollinearity note

Some numeric predictors are strongly correlated (e.g., `year` vs `car_age`), motivating regularization (Ridge) and careful interpretation of linear coefficients.

Correlation heatmap:

![Numeric correlation](dataset/corr_numeric.png)

VIF values (CSV):
- `results/dataset/vif_numeric.csv`

## 10. Demo app (Streamlit)

The repository includes a lightweight Streamlit app in `app/app.py` that loads a trained run and makes single-row predictions.

Run it:
```bash
export DSCI441_DEMO_RUN_DIR="runs/<your_run_dir>"
streamlit run app/app.py
```

The run directory must contain:
- `model.joblib` (saved pipeline)

## 11. Reproducibility

What is committed (small artifacts for grading/presentation):
- `results/` figures and summaries
- `configs/` experiment configs
- `scripts/` utilities to reproduce exports

What is **not** committed (large/local artifacts):
- `data/` (CSV is large)
- `runs/` (models + intermediate artifacts)

One-command workflow (after the CSV is available locally):
```bash
.venv/bin/python scripts/run_baselines.py
```

## 12. Limitations and ethical note

**RMSE in USD is scale-dependent**. Because prices are heavy-tailed, a small fraction of very expensive listings can dominate RMSE. The error analysis plots show **heteroskedasticity** (absolute error increases with price). In this repo I report:
- an overall best model (`hgb_ordinal`) that meets the R² target on the broad domain, and
- additional “mid-market” configs (e.g., `hgb_midmarket_20k`) that meet an RMSE < $3,000 goal in a **restricted operating domain**.

This is an educational demo. It should not be used to set real prices; scraped listings can include errors, and the model does not account for important variables not present in the dataset (accident history, trim details, location micro-markets, negotiation, etc.).

## 13. Conclusion

- Linear models (OLS/Ridge/Lasso) provide interpretable baselines but underfit nonlinear market effects.
- Adding text (`description`) via TF‑IDF improves predictive performance.
- A nonlinear boosted-tree model with ordinal categoricals (`hgb_ordinal`) achieves **R² > 0.80** and provides the best overall fit in the tracked experiments.
- Error analysis shows that absolute error increases with price; filtered-domain experiments can reduce RMSE substantially for specific operating regimes.

## 14. References

[1] Kaggle dataset: “Craigslist Cars & Trucks Data” (Austin Reese).  
