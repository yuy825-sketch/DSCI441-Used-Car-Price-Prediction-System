# Project Report — Used Car Price Prediction System (DSCI 441)

## Abstract

This project builds an end-to-end regression system to predict **used car listing prices (USD)** from Craigslist listing attributes. The used-car market is inherently noisy: prices are **heavy‑tailed**, listings contain missing values, and key effects are nonlinear (e.g., the impact of mileage depends on vehicle age and category). To address this, I evaluate a progression of models: linear baselines (**OLS**, **Ridge**, **Lasso**), a feature-engineered linear model (**Ridge + TF‑IDF(description)**), and a nonlinear boosted tree model (**HistGradientBoostingRegressor**) with ordinal-encoded categoricals.

Using a fixed 80/20 train/test split (seed = 441) and sample-based training for runtime, the best overall model on the broad domain achieves **test R² = 0.8061** (`hgb_ordinal`). Detailed diagnostics show clear heteroskedasticity (absolute dollar error increases with price), which explains why a global “one-number” RMSE target is difficult on a heavy‑tailed target. To complement the broad-domain model, I also evaluate a **mid‑market operating domain** (filtered max price) that achieves **RMSE < $3,000** while illustrating the practical trade-off between broad coverage and low absolute error.

## Table of contents

- [1. Problem statement and deliverables](#1-problem-statement-and-deliverables)
- [2. Dataset](#2-dataset)
- [3. Data cleaning and feature engineering](#3-data-cleaning-and-feature-engineering)
- [4. Methods](#4-methods)
- [5. Experimental protocol](#5-experimental-protocol)
- [6. Results](#6-results)
- [7. Diagnostics and error analysis](#7-diagnostics-and-error-analysis)
- [8. Feature importance and interpretation](#8-feature-importance-and-interpretation)
- [9. Demo app (Streamlit)](#9-demo-app-streamlit)
- [10. Reproducibility](#10-reproducibility)
- [11. Limitations and future work](#11-limitations-and-future-work)
- [12. Conclusion](#12-conclusion)
- [13. Reference](#13-reference)

## 1. Problem statement and deliverables

**Goal**: predict a reasonable price estimate from listing attributes and present the work as a complete course project with:
- multiple regression baselines and comparisons,
- clear diagnostics (true-vs-predicted, residual plots, error analysis),
- feature-importance/interpretation,
- and a runnable **interactive demo**.

<img src="pipeline_overview.png" width="760" />

## 2. Dataset

**Dataset**: Craigslist Cars & Trucks (Kaggle).  
**Local file** (not committed): `data/craigslist/vehicles.csv`  
**Row count**: 426,880 listings (CSV has 426,881 lines including header).

The dataset combines numeric features (e.g., `year`, `odometer`, latitude/longitude) with many categorical attributes (`manufacturer`, `condition`, `fuel`, `transmission`, `drive`, etc.) and free‑text `description`. A major modeling challenge is that the **target distribution is heavy‑tailed**: most listings are relatively inexpensive, but a smaller number of very expensive vehicles exist and can dominate squared-error metrics.

### 2.1 Visual EDA highlights

**Heavy‑tailed price** (log-scaled x-axis):

<img src="dataset/price_hist_logx.png" width="620" />

**Mileage distribution**:

<img src="dataset/odometer_hist.png" width="620" />

**Year effect** (newer cars are typically more expensive):

<img src="dataset/price_by_year.png" width="680" />

**Missingness is substantial** for several categorical columns:

<img src="dataset/missingness_top20.png" width="720" />

### 2.2 Missingness and data quality notes (sample-based)

A quick sample-based scan shows high missingness in several columns (examples from a 10k-row sample):
- `size` ~ 74%
- `condition` ~ 46%
- `cylinders` ~ 33%
- `VIN` ~ 31%
- `drive` ~ 29%

This motivates robust preprocessing (imputation + appropriate categorical encoding) and careful interpretation of coefficients for linear models.

## 3. Data cleaning and feature engineering

Cleaning and filtering are implemented in `src/dsci441_used_car/data.py` and parameterized per experiment via `configs/*.json`. The main steps are:

### 3.1 Numeric coercion and validity filters

- Coerce `price` to numeric and drop rows where the target is missing/invalid.
- Coerce `year` and `odometer` to numeric where present.
- Filter by configured bounds:
  - `min_price` ≤ `price` ≤ `max_price`
  - `min_year` ≤ `year` ≤ `max_year`
  - `0` ≤ `odometer` ≤ `max_odometer`
- Enforce basic validity for coordinates if present:
  - `lat` in [-90, 90], `long` in [-180, 180]

These filters reduce obvious noise/outliers without aggressively hand-curating the dataset.

### 3.2 Derived features

To make “age” and “usage intensity” explicit, I add:
- `car_age = max_year - year`
- `miles_per_year = odometer / max(car_age, 1)`

These derived features help both linear and nonlinear models by exposing meaningful quantities directly.

### 3.3 Standardizing missing/unknown strings

Some columns contain empty strings or `"unknown"`-like tokens. I convert these to missing values so that imputation behaves consistently across runs.

## 4. Methods

All models are trained within a scikit-learn pipeline:
1) preprocessing (impute + encode + optional TF-IDF),
2) estimator,
3) optional target transform.

### 4.1 Target transform (log pricing)

Prices span orders of magnitude. Many configs therefore train on:

`y' = log(1 + y)` and invert with `y = exp(y') - 1`

This reduces the influence of the high-price tail during fitting while still evaluating metrics on the original dollar scale.

### 4.2 Linear baselines: OLS, Ridge, Lasso

Let `X` be the design matrix and `y` the target price.

- **OLS** solves: `min_w ||y - Xw||²`
- **Ridge** solves: `min_w ||y - Xw||² + α||w||²`
- **Lasso** solves: `min_w ||y - Xw||² + α||w||₁`

Categoricals are one-hot encoded for the linear models. Ridge helps stabilize coefficients under multicollinearity; Lasso performs feature selection but can drop useful correlated signals.

### 4.3 Ridge + TF-IDF(description)

This variant augments structured features with a sparse TF‑IDF vector extracted from the text `description`:
- n-grams: (1, 2)
- max features: 8000 (configurable)

This tests whether unstructured descriptions contain additional pricing signals (trim level, features, condition details, etc.).

### 4.4 Nonlinear boosted trees: HistGradientBoostingRegressor

Used-car pricing contains nonlinearities and interactions. A boosted-tree regressor is a strong classical baseline for tabular data. I use:
- **HistGradientBoostingRegressor**
- categoricals encoded as ordinals (with unknown categories mapped to a sentinel)

This model typically outperforms linear baselines on heterogeneous tabular datasets.

## 5. Experimental protocol

### 5.1 Split, seed, and sampling

All reported results use:
- train/test split: 80/20
- seed: 441

For runtime, training is sample-based (`sample_n` is set per config), then cleaning filters are applied. This gives repeatable experiments while keeping training feasible on CPU.

### 5.2 Metrics

On the **test split**, I report:
- **R²**: goodness of fit
- **RMSE**: `sqrt(mean((y - ŷ)²))`
- **MAE**: `mean(|y - ŷ|)`

Additionally, I report several “practical error” summaries (median absolute error, percentile errors, and percent-within thresholds) to better communicate real-world usefulness than RMSE alone.

## 6. Results

### 6.1 Model comparison plots

<img src="model_comparison_r2.png" width="760" />

<img src="model_comparison_rmse.png" width="760" />

### 6.2 Summary table (test metrics)

| Tag | Model | Domain | Test R² | Test RMSE | Test MAE |
|---|---|---|---:|---:|---:|
| `hgb_ordinal` | HGB (ordinal cats) | broad | **0.8061** | 6649.38 | 3383.88 |
| `ridge_text_a20` | Ridge + TF‑IDF | broad | 0.7275 | 7865.90 | 4416.09 |
| `ridge` | Ridge (one-hot) | broad | 0.5835 | 9665.96 | 5684.14 |
| `ols` | OLS (one-hot) | broad | 0.5834 | 9667.80 | 5689.79 |
| `lasso` | Lasso (one-hot) | broad | 0.5540 | 10002.64 | 5973.56 |
| `hgb_midmarket_60k` | HGB (ordinal cats) | max_price=60k | 0.8525 | 4981.00 | 3014.91 |
| `hgb_midmarket_30k` | HGB (ordinal cats) | max_price=30k | 0.8019 | 3654.52 | 2360.37 |
| `hgb_midmarket_20k` | HGB (ordinal cats) | max_price=20k | 0.7024 | **2935.79** | 1972.39 |

### 6.3 Discussion of results

Key observations:

1) **Linear baselines plateau** around R² ≈ 0.55–0.58. This is expected because used-car pricing has nonlinear relationships and many interactions between categorical and numeric attributes.

2) **Text helps**: adding TF‑IDF(description) increases R² to 0.7275. This suggests the free-text description contains real pricing cues (features, trim, condition notes) not captured by structured columns.

3) **Boosted trees perform best on the broad domain**: `hgb_ordinal` reaches R² > 0.80 and improves all error metrics. This supports the hypothesis that nonlinear structure dominates performance in this dataset.

4) **RMSE depends strongly on operating domain**. On a broad, heavy‑tailed target, a global RMSE threshold can be dominated by expensive outliers. When restricting to a mid-market range (`max_price=20k`), RMSE falls below $3,000, but R² decreases because the domain is narrower and the remaining variance is smaller in absolute dollars.

## 7. Diagnostics and error analysis

### 7.1 Broad-domain best model (`hgb_ordinal`)

True vs predicted (test):

<img src="true_vs_pred_hgb_ordinal.png" width="640" />

Residual diagnostics:

<img src="residuals_hist_hgb_ordinal.png" width="620" />

<img src="residuals_scatter_hgb_ordinal.png" width="720" />

Interpretation:
- The true-vs-predicted plot shows a strong overall trend but increasing spread at higher prices.
- Residual plots suggest clear **heteroskedasticity**: the variance of residuals increases with predicted price.

### 7.2 Practical error summaries (broad domain)

For `hgb_ordinal` on the broad domain test split:
- Median absolute error: **$1,829**
- 90th percentile absolute error: **$7,602**
- 95th percentile absolute error: **$11,191**
- % within $1,000: **31.53%**
- % within $3,000: **66.79%**
- % within 10%: **38.73%**
- % within 20%: **64.19%**

Error distribution visuals:

<img src="error_abs_hist_hgb_ordinal.png" width="620" />

<img src="error_abs_by_true_hgb_ordinal.png" width="720" />

These plots show that absolute error increases with price, which is typical for marketplace data: a $2,000 error is “big” for a $6,000 car but relatively small for a $60,000 car.

### 7.3 Mid-market operating domains (RMSE-focused)

To understand the RMSE target in a more controlled setting, I evaluate filtered domains:
- `hgb_midmarket_60k`: max_price = 60,000 (RMSE ≈ 4,981)
- `hgb_midmarket_30k`: max_price = 30,000 (RMSE ≈ 3,655)
- `hgb_midmarket_20k`: max_price = 20,000 (RMSE ≈ 2,936)

This demonstrates a key practical point: **RMSE in dollars is strongly tied to the price range**. A single global RMSE target can be misleading unless the operating domain is specified.

## 8. Feature importance and interpretation

### 8.1 Permutation importance (broad-domain best)

<img src="perm_importance_hgb_ordinal.png" width="740" />

Interpretation:
- The dominant signals come from **age/mileage** (year, odometer, derived usage) plus a small set of categoricals.
- The importance distribution suggests the model uses multiple complementary signals rather than relying on a single feature.

### 8.2 Text importance signal

The text-augmented Ridge model also shows `description` contributes measurable predictive value:

<img src="perm_importance_ridge_text_a20.png" width="740" />

## 9. Demo app (Streamlit)

The project includes a Streamlit demo app that loads a trained run directory and performs single-row predictions.

Demo screenshot:

<img src="streamlit_demo.png" width="720" />

Run locally:
```bash
export DSCI441_DEMO_RUN_DIR="runs/<your_run_dir>"
streamlit run app/app.py
```

## 10. Reproducibility

After placing the CSV at `data/craigslist/vehicles.csv`:

Run the baseline suite (EDA + multiple models + exports):
```bash
.venv/bin/python scripts/run_baselines.py
```

Run a single experiment:
```bash
.venv/bin/python train.py --config configs/hgb_ordinal.json --run-name hgb_ordinal
.venv/bin/python scripts/export_results.py --run-dir runs/<run_dir> --out-dir results --tag hgb_ordinal
```

Optional: error analysis exports:
```bash
.venv/bin/python scripts/error_analysis.py --run-dir runs/<run_dir> --out-dir results --tag hgb_ordinal
```

Optional: capture demo screenshot (requires local Firefox):
```bash
bash scripts/capture_streamlit_screenshot.sh results/streamlit_demo.png
```

## 11. Limitations and future work

Limitations:
- The dataset is scraped listing data; prices can be noisy, missing, or inconsistent across regions/time.
- Important real-world variables are absent (accident history, trim/package details, maintenance records, negotiation effects).
- Heavy-tailed targets and heteroskedasticity mean RMSE can be dominated by rare expensive listings.

Future work ideas (course-appropriate):
- Add explicit time features (posting date) to handle temporal drift.
- Calibrate errors by price band (train separate models per segment or use quantile loss).
- Explore richer tabular models (e.g., CatBoost with native categoricals) and robust loss functions (Huber).
- Add uncertainty estimates (prediction intervals) to communicate confidence.

## 12. Conclusion

- Linear models provide interpretable baselines but underfit nonlinear market effects.
- Adding text features improves performance, confirming that descriptions contain useful pricing cues.
- A boosted-tree regressor with ordinal categoricals achieves the best broad-domain performance (R² > 0.80).
- Error analysis shows heteroskedasticity and the importance of specifying operating domain when interpreting RMSE.

## 13. Reference

Kaggle: “Craigslist Cars & Trucks Data” (Austin Reese).  
