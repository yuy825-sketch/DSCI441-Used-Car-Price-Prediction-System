# Figures and Visualizations (Index)

This file documents each visualization in `results/`, what it shows, and the conclusion it supports.

## Project overview

### `pipeline_overview.png`
- **What**: A compact end-to-end pipeline diagram (data → cleaning → preprocessing → model → exports + demo).
- **How generated**: `python scripts/make_pipeline_figure.py --out results/pipeline_overview.png`
- **Conclusion**: Visual summary of the deliverables and how the repo components connect.

## Dataset visualizations (`results/dataset/`)

### `dataset/price_hist_logx.png`
- **What**: Histogram of price with a log-scaled x-axis.
- **How generated**: `python scripts/dataset_viz.py --csv data/craigslist/vehicles.csv --out-dir results/dataset`
- **Conclusion**: Price is heavy-tailed; using `log1p(price)` as the training target is reasonable.

### `dataset/odometer_hist.png`
- **What**: Odometer mileage histogram (after basic cleaning filters).
- **How generated**: `python scripts/dataset_viz_extended.py --csv data/craigslist/vehicles.csv --out-dir results/dataset`
- **Conclusion**: Mileage has wide spread with long tails; strong outlier filtering is required.

### `dataset/price_by_year.png`
- **What**: Median price over model year with an interquartile range band.
- **Conclusion**: Newer model years are substantially more expensive; `year` is a primary signal.

### `dataset/price_vs_odometer.png`
- **What**: Scatter plot of price vs odometer.
- **Conclusion**: Higher mileage generally correlates with lower prices, but the relationship is noisy and nonlinear.

### `dataset/price_vs_miles_per_year.png`
- **What**: Scatter plot of price vs miles/year (derived from `odometer / max(car_age, 1)`), on log y-axis.
- **Conclusion**: “Usage intensity” provides additional information beyond raw odometer.

### `dataset/missingness_top20.png`
- **What**: Bar chart of missingness (%) for the most-missing columns in the cleaned sample.
- **Conclusion**: Several categorical columns are missing frequently; robust imputation is required.

### `dataset/manufacturer_top25.png`
- **What**: Top 25 manufacturers by listing count.
- **Conclusion**: Manufacturer distribution is highly skewed; high-cardinality categories should be regularized or grouped.

### `dataset/corr_numeric.png`
- **What**: Correlation heatmap for numeric features (`year`, `odometer`, `car_age`, etc.).
- **How generated**: `python scripts/vif_analysis.py --csv data/craigslist/vehicles.csv --out-dir results/dataset`
- **Conclusion**: `year` and `car_age` are strongly correlated; multicollinearity motivates Ridge vs OLS.

### `dataset/vif_numeric.csv`
- **What**: Numeric VIF values (variance inflation factor) for multicollinearity.
- **Conclusion**: Confirms multicollinearity among numeric predictors (especially `year` vs `car_age`).

## Model comparison

### `model_comparison_r2.png`
- **What**: Bar chart of test R² across experiments.
- **How generated**: `python scripts/plot_model_comparison.py --results-dir results --out-dir results`
- **Conclusion**: Nonlinear `hgb_ordinal` meets the course target (R² > 0.80), while linear baselines are weaker.

### `model_comparison_rmse.png`
- **What**: Bar chart of test RMSE across experiments.
- **Conclusion**: The best model reduces error magnitude substantially compared to OLS/Ridge/Lasso baselines.

## Baseline model diagnostics

Each experiment exports:
- `summary_<tag>.md`
- `true_vs_pred_<tag>.png`
- `residuals_hist_<tag>.png`
- `residuals_scatter_<tag>.png`
- `top_coeffs_<tag>.png` (only for linear models with coefficients)

### `true_vs_pred_ols.png`, `residuals_*_ols.png`, `top_coeffs_ols.png`
- **Conclusion**: OLS underfits the nonlinear relationship between inputs and price (low R²), and coefficients can be unstable under multicollinearity.

### `true_vs_pred_ridge.png`, `residuals_*_ridge.png`, `top_coeffs_ridge.png`
- **Conclusion**: Ridge stabilizes coefficients but only modestly improves predictive performance in this setup.

### `true_vs_pred_lasso.png`, `residuals_*_lasso.png`, `top_coeffs_lasso.png`
- **Conclusion**: Lasso performs slightly worse than Ridge/OLS here; strong sparsity may discard useful correlated signals.

## Improved models

### `true_vs_pred_ridge_text_a20.png`, `summary_ridge_text_a20.md`
- **What**: Ridge regression augmented with TF-IDF features from `description`.
- **Conclusion**: Text features improve performance (R² increases), indicating that descriptions contain useful pricing cues.

### `true_vs_pred_hgb_ordinal.png`, `summary_hgb_ordinal.md`
- **What**: HistGradientBoostingRegressor with ordinal-encoded categoricals.
- **Conclusion**: Captures nonlinearities and interactions; achieves the best test R² in the tracked experiments.

## Feature importance (permutation)

### `perm_importance_hgb_ordinal.png`
- **What**: Permutation importance on the test split (R² decrease).
- **How generated**: `python scripts/permutation_importance.py --run-dir runs/<hgb_run> --tag hgb_ordinal`
- **Conclusion**: Confirms the strongest signals come from year/mileage and a small set of categorical attributes; the model uses multiple complementary signals.

### `perm_importance_ridge_text_a20.png`
- **What**: Permutation importance for the text-augmented Ridge model.
- **Conclusion**: The `description` column contributes measurable predictive value beyond structured features.

## Error analysis (distribution + price-dependent error)

Each experiment exports:
- `error_analysis_<tag>.md`
- `error_abs_hist_<tag>.png`
- `error_pct_hist_<tag>.png`
- `error_abs_by_true_<tag>.png`
- `error_by_true_bin_<tag>.png`

### `error_*_hgb_ordinal.*`
- **What**: Error distribution and “error vs price” plots for the best overall model.
- **How generated**: `python scripts/error_analysis.py --run-dir runs/<hgb_run> --out-dir results --tag hgb_ordinal`
- **Conclusion**: Absolute dollar error grows with vehicle price (heteroskedasticity), which helps explain why achieving a very low global RMSE is difficult on a heavy-tailed target.

### `error_*_ridge_text_a20.*`
- **What**: Same error analysis for the text-augmented Ridge model.
- **Conclusion**: Text features help, but the model still struggles more on the high-price tail than the tree-based model.
