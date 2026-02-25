from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import TransformedTargetRegressor


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(math.sqrt(mean_squared_error(y_true, y_pred)))


@dataclass(frozen=True)
class FitOutputs:
    pipeline: Any
    numeric_features: list[str]
    categorical_features: list[str]
    feature_names_out: list[str]
    metrics: dict[str, Any]
    y_test: np.ndarray
    y_pred: np.ndarray


def infer_feature_types(df: pd.DataFrame, features: list[str]) -> tuple[list[str], list[str]]:
    numeric: list[str] = []
    categorical: list[str] = []
    for f in features:
        s = df[f]
        if pd.api.types.is_numeric_dtype(s):
            numeric.append(f)
        else:
            categorical.append(f)
    return numeric, categorical


def build_preprocess(
    *,
    numeric_features: list[str],
    categorical_features: list[str],
    standardize_numeric: bool,
    onehot_min_frequency: int | None,
    onehot_max_categories: int | None,
) -> ColumnTransformer:
    num_steps: list[tuple[str, Any]] = [("impute", SimpleImputer(strategy="median"))]
    if standardize_numeric:
        num_steps.append(("scale", StandardScaler()))
    num_pipe = Pipeline(num_steps)

    use_infrequent = onehot_min_frequency is not None or onehot_max_categories is not None
    handle_unknown = "infrequent_if_exist" if use_infrequent else "ignore"
    cat_pipe = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown=handle_unknown,
                    sparse_output=True,
                    min_frequency=onehot_min_frequency,
                    max_categories=onehot_max_categories,
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", num_pipe, numeric_features),
            ("cat", cat_pipe, categorical_features),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def build_model(model_cfg: dict[str, Any]):
    model_type = str(model_cfg["type"]).lower()
    if model_type in {"ols", "linear", "linearregression"}:
        return LinearRegression()
    if model_type == "ridge":
        return Ridge(alpha=float(model_cfg.get("alpha", 1.0)))
    if model_type == "lasso":
        return Lasso(alpha=float(model_cfg.get("alpha", 0.001)), max_iter=int(model_cfg.get("max_iter", 5000)))
    raise ValueError(f"Unknown model type: {model_type}")


def _maybe_wrap_log_target(estimator, *, enabled: bool):
    if not enabled:
        return estimator
    return TransformedTargetRegressor(
        regressor=estimator,
        func=np.log1p,
        inverse_func=np.expm1,
        check_inverse=False,
    )


def fit_from_config(*, df: pd.DataFrame, cfg: dict[str, Any]) -> FitOutputs:
    dataset_cfg = cfg["dataset"]
    target = str(dataset_cfg.get("target", "price"))
    features = list(dataset_cfg["features"])
    if "car_age" in df.columns and "car_age" not in features:
        features = [*features, "car_age"]
    if "miles_per_year" in df.columns and "miles_per_year" not in features:
        features = [*features, "miles_per_year"]

    numeric_features, categorical_features = infer_feature_types(df, features)
    pre_cfg = cfg.get("preprocess", {}) or {}
    standardize_numeric = bool(pre_cfg.get("standardize_numeric", True))
    onehot_min_frequency = pre_cfg.get("onehot_min_frequency", None)
    onehot_max_categories = pre_cfg.get("onehot_max_categories", None)
    if onehot_min_frequency is not None:
        onehot_min_frequency = int(onehot_min_frequency)
    if onehot_max_categories is not None:
        onehot_max_categories = int(onehot_max_categories)
    preprocess = build_preprocess(
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        standardize_numeric=standardize_numeric,
        onehot_min_frequency=onehot_min_frequency,
        onehot_max_categories=onehot_max_categories,
    )
    model = build_model(cfg["model"])
    pipe = Pipeline([("preprocess", preprocess), ("model", model)])

    log_target = bool(cfg.get("train", {}).get("log_target", False))
    estimator = _maybe_wrap_log_target(pipe, enabled=log_target)

    split_cfg = cfg.get("split", {})
    test_size = float(split_cfg.get("test_size", 0.2))
    seed = int(split_cfg.get("seed", 441))
    seed_everything(seed)

    X = df[features]
    y = df[target].to_numpy(dtype=np.float64)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=seed)
    estimator.fit(X_train, y_train)

    y_pred_train = estimator.predict(X_train)
    y_pred = estimator.predict(X_test)

    metrics = {
        "config": {
            "model_type": str(cfg["model"]["type"]),
            "log_target": log_target,
            "n_rows": int(df.shape[0]),
            "n_features_input": int(len(features)),
            "n_numeric": int(len(numeric_features)),
            "n_categorical": int(len(categorical_features)),
        },
        "train": {
            "r2": float(r2_score(y_train, y_pred_train)),
            "rmse": _rmse(y_train, y_pred_train),
            "mae": float(mean_absolute_error(y_train, y_pred_train)),
        },
        "test": {
            "r2": float(r2_score(y_test, y_pred)),
            "rmse": _rmse(y_test, y_pred),
            "mae": float(mean_absolute_error(y_test, y_pred)),
        },
    }

    # Feature names after preprocessing (for coefficient plots)
    feature_names_out: list[str] = []
    try:
        inner = estimator.regressor_ if hasattr(estimator, "regressor_") else estimator
        preprocess_fitted = inner.named_steps["preprocess"]
        feature_names_out = list(preprocess_fitted.get_feature_names_out())
    except Exception:
        feature_names_out = []

    return FitOutputs(
        pipeline=estimator,
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        feature_names_out=feature_names_out,
        metrics=metrics,
        y_test=np.asarray(y_test, dtype=np.float64),
        y_pred=np.asarray(y_pred, dtype=np.float64),
    )


def _extract_linear_coefs(estimator) -> tuple[np.ndarray | None, float | None]:
    inner = estimator.regressor_ if hasattr(estimator, "regressor_") else estimator
    model = inner.named_steps.get("model", None) if hasattr(inner, "named_steps") else None
    if model is None or not hasattr(model, "coef_"):
        return None, None
    coef = np.asarray(model.coef_, dtype=np.float64).ravel()
    intercept = float(getattr(model, "intercept_", 0.0))
    return coef, intercept


def save_run(
    *,
    outdir: Path,
    fit: FitOutputs,
    config_path: Path,
    extra_files: dict[str, Any] | None = None,
) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    joblib.dump(fit.pipeline, outdir / "model.joblib")

    (outdir / "metrics.json").write_text(json.dumps(fit.metrics, indent=2) + "\n", encoding="utf-8")
    np.savez(outdir / "test_outputs.npz", y_true=fit.y_test, y_pred=fit.y_pred)

    (outdir / "features.json").write_text(
        json.dumps(
            {
                "numeric": fit.numeric_features,
                "categorical": fit.categorical_features,
                "feature_names_out": fit.feature_names_out,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    coef, intercept = _extract_linear_coefs(fit.pipeline)
    if coef is not None:
        (outdir / "coefficients.json").write_text(
            json.dumps(
                {
                    "intercept": intercept,
                    "coef": coef.tolist(),
                    "feature_names_out": fit.feature_names_out,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    # Keep a copy of the config for reproducibility (same pattern as DSCI498).
    (outdir / "config.json").write_text(config_path.read_text(encoding="utf-8"), encoding="utf-8")

    if extra_files:
        for name, obj in extra_files.items():
            (outdir / name).write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
