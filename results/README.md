# Results

This folder is intended for **presentation/report** outputs (figures + short markdown summaries).

Quick links:
- Report: [`REPORT.md`](REPORT.md)

Typical workflow:
1) Train a model:
   - `python train.py --config configs/baseline_ols.json --run-name ols`
2) Export latest run to results:
   - `python scripts/export_latest.py`
