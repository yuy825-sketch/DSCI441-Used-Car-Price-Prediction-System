from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st

from dsci441_used_car.infer import load_run_model, predict_one


def _get_feature_schema(pipeline) -> tuple[list[str], list[str], dict[str, list[str]]]:
    inner = pipeline.regressor_ if hasattr(pipeline, "regressor_") else pipeline
    preprocess = inner.named_steps["preprocess"]
    num_features = list(preprocess.transformers_[0][2])
    cat_features = list(preprocess.transformers_[1][2])

    categories: dict[str, list[str]] = {}
    try:
        ohe = preprocess.named_transformers_["cat"].named_steps["onehot"]
        for feat, cats in zip(cat_features, ohe.categories_, strict=False):
            categories[feat] = [str(c) for c in cats[:200]]
    except Exception:
        pass

    return num_features, cat_features, categories


@st.cache_resource
def _load_model(run_dir: str):
    loaded = load_run_model(Path(run_dir))
    return loaded


def main() -> None:
    st.set_page_config(page_title="DSCI441 Used Car Price Predictor", layout="wide")

    st.markdown(
        """
        <style>
          .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
          .small-note { font-size: 0.92rem; color: rgba(49, 51, 63, 0.75); }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Used Car Price Prediction (DSCI 441)")
    st.markdown(
        "<div class='small-note'>Course demo only (educational). Not financial advice.</div>",
        unsafe_allow_html=True,
    )

    default_run_dir = os.getenv("DSCI441_DEMO_RUN_DIR", "runs/<your_run_dir>")

    with st.sidebar:
        st.header("Settings")
        st.caption("The run directory must contain `model.joblib`.")
        run_dir = st.text_input("Run directory", value=default_run_dir)

    if "runs/<your_run_dir>" in run_dir:
        st.info("Set a real run directory (e.g., `runs/2026...__ridge`) to enable predictions.")
        return

    try:
        loaded = _load_model(run_dir)
    except Exception as e:
        st.error(f"Failed to load model from {run_dir}: {e}")
        return

    num_features, cat_features, categories = _get_feature_schema(loaded.pipeline)

    st.subheader("1) Enter vehicle details")
    col_a, col_b = st.columns([1, 1], gap="large")

    features: dict[str, object] = {}
    with col_a:
        for feat in num_features:
            if feat == "year":
                features[feat] = st.number_input("Year", min_value=1950, max_value=2030, value=2016, step=1)
            elif feat == "odometer":
                features[feat] = st.number_input("Odometer (miles)", min_value=0, max_value=1000000, value=90000, step=1000)
            elif feat == "car_age":
                features[feat] = st.number_input("Car age (years)", min_value=0, max_value=100, value=10, step=1)
            else:
                features[feat] = st.number_input(feat, value=0.0)

    with col_b:
        for feat in cat_features:
            opts = categories.get(feat, [])
            if opts:
                features[feat] = st.selectbox(feat, options=opts, index=0)
            else:
                features[feat] = st.text_input(feat, value="")

    st.subheader("2) Predict")
    if st.button("Predict price"):
        try:
            pred = predict_one(loaded.pipeline, features)
        except Exception as e:
            st.error(f"Prediction failed: {e}")
            return
        st.success(f"Predicted price: ${pred:,.0f}")

    st.subheader("3) Debug view (input row)")
    st.dataframe(pd.DataFrame([features]), use_container_width=True)


if __name__ == "__main__":
    main()
