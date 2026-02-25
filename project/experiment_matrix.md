# Experiment matrix

| ID | Model | Target transform | Notes |
|---|---|---|---|
| E1 | OLS | log1p(price) | Baseline linear regression |
| E2 | Ridge (alpha=5) | log1p(price) | Stabilize multicollinearity |
| E3 | Lasso (alpha=5e-4) | log1p(price) | Sparse coefficients / feature selection |
| E4 | Ridge + TF-IDF(description) | log1p(price) | Add text features from listing descriptions |
| E5 | HistGradientBoosting + ordinal cats | log1p(price) | Nonlinear baseline to hit target R² |

Suggested additions:
- RidgeCV / LassoCV over an alpha grid
- Compare `log_target=true` vs `false`
