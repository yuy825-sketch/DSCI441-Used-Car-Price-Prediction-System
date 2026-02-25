# Results

This folder is intended for **presentation/report** outputs (figures + short markdown summaries).

Quick links:
- Report: [`REPORT.md`](REPORT.md)

## Snapshot figures

Dataset (sample-based):
- `dataset/price_hist_logx.png`
- `dataset/price_vs_odometer.png`
- `dataset/manufacturer_top25.png`
- `dataset/corr_numeric.png`

Typical workflow:
1) Train a model:
   - `python train.py --config configs/baseline_ols.json --run-name ols`
2) Export latest run to results:
   - `python scripts/export_latest.py`
