# Decision log

- 2026-02-25: Use scikit-learn `Pipeline` + `ColumnTransformer` with OHE for categorical features.
- 2026-02-25: Default to `log1p(price)` via `TransformedTargetRegressor` to reduce heavy-tail effects.
- 2026-02-25: Compute VIF only on numeric signals (VIF on one-hot expanded, high-cardinality cats is not very interpretable).

