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
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.compose import TransformedTargetRegressor
from sklearn.feature_extraction.text import TfidfVectorizer


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(math.sqrt(mean_squared_error(y_true, y_pred)))


def _flatten_1d(x):
    # Must be a top-level function so the pipeline can be pickled/joblib-dumped.
    return np.asarray(x).ravel()


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
    text_features: list[str],
    standardize_numeric: bool,
    categorical_encoder: str,
    onehot_min_frequency: int | None,
    onehot_max_categories: int | None,
    text_cfg: dict[str, Any] | None,
) -> ColumnTransformer:
    num_steps: list[tuple[str, Any]] = [("impute", SimpleImputer(strategy="median"))]
    if standardize_numeric:
        num_steps.append(("scale", StandardScaler()))
    num_pipe = Pipeline(num_steps)

    categorical_encoder = str(categorical_encoder).lower()
    if categorical_encoder not in {"onehot", "ordinal"}:
        raise ValueError(f"Unknown categorical_encoder: {categorical_encoder}")

    if categorical_encoder == "onehot":
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
    else:
        cat_pipe = Pipeline(
            [
                ("impute", SimpleImputer(strategy="most_frequent")),
                ("ordinal", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
            ]
        )

    transformers: list[tuple[str, Any, list[str]]] = [
        ("num", num_pipe, numeric_features),
        ("cat", cat_pipe, categorical_features),
    ]

    if text_features:
        cfg = text_cfg or {}
        max_features = int(cfg.get("max_features", 5000))
        min_df = int(cfg.get("min_df", 3))
        max_df = float(cfg.get("max_df", 0.98))
        ngram_range = cfg.get("ngram_range", [1, 2])
        if isinstance(ngram_range, list) and len(ngram_range) == 2:
            ngram_range = (int(ngram_range[0]), int(ngram_range[1]))
        else:
            ngram_range = (1, 2)

        text_pipe = Pipeline(
            steps=[
                ("impute", SimpleImputer(strategy="constant", fill_value="")),
                ("flatten", FunctionTransformer(_flatten_1d, validate=False)),
                (
                    "tfidf",
                    TfidfVectorizer(
                        max_features=max_features,
                        min_df=min_df,
                        max_df=max_df,
                        ngram_range=ngram_range,
                        strip_accents="unicode",
                        lowercase=True,
                    ),
                ),
            ]
        )
        transformers.append(("text", text_pipe, text_features))

    return ColumnTransformer(
        transformers=transformers,
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
    if model_type in {"hgb", "histgb", "histgradientboosting"}:
        return HistGradientBoostingRegressor(
            max_iter=int(model_cfg.get("max_iter", 400)),
            learning_rate=float(model_cfg.get("learning_rate", 0.06)),
            max_depth=(None if model_cfg.get("max_depth", None) is None else int(model_cfg.get("max_depth"))),
            max_leaf_nodes=int(model_cfg.get("max_leaf_nodes", 63)),
            min_samples_leaf=int(model_cfg.get("min_samples_leaf", 20)),
            l2_regularization=float(model_cfg.get("l2_regularization", 0.0)),
            random_state=int(model_cfg.get("seed", 441)),
        )
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

    pre_cfg = cfg.get("preprocess", {}) or {}
    standardize_numeric = bool(pre_cfg.get("standardize_numeric", True))
    categorical_encoder = str(pre_cfg.get("categorical_encoder", "onehot"))
    onehot_min_frequency = pre_cfg.get("onehot_min_frequency", None)
    onehot_max_categories = pre_cfg.get("onehot_max_categories", None)
    if onehot_min_frequency is not None:
        onehot_min_frequency = int(onehot_min_frequency)
    if onehot_max_categories is not None:
        onehot_max_categories = int(onehot_max_categories)

    text_cfg = pre_cfg.get("text", None)
    text_features: list[str] = []
    if isinstance(text_cfg, dict):
        cols = text_cfg.get("columns", None)
        if isinstance(cols, str):
            text_features = [cols]
        elif isinstance(cols, list):
            text_features = [str(c) for c in cols]

    typed_features = [f for f in features if f not in set(text_features)]
    numeric_features, categorical_features = infer_feature_types(df, typed_features)
    preprocess = build_preprocess(
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        text_features=text_features,
        standardize_numeric=standardize_numeric,
        categorical_encoder=categorical_encoder,
        onehot_min_frequency=onehot_min_frequency,
        onehot_max_categories=onehot_max_categories,
        text_cfg=text_cfg if isinstance(text_cfg, dict) else None,
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
