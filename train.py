from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dsci441_used_car.data import CleanSpec, clean_dataset, load_vehicles_csv
from dsci441_used_car.paths import get_repo_root
from dsci441_used_car.runpack import RunMeta, copy_config, create_run_dir, git_head_sha, utc_now, write_meta
from dsci441_used_car.train_utils import fit_from_config, save_run


def _load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, default=None, help="Optional explicit output run directory")
    parser.add_argument("--run-name", type=str, default="baseline")
    args = parser.parse_args()

    cfg = _load_config(args.config)
    dataset_cfg = cfg["dataset"]

    csv_path = Path(str(dataset_cfg["path"]))
    target = str(dataset_cfg.get("target", "price"))
    features = list(dataset_cfg["features"])

    spec = CleanSpec(
        min_price=float(dataset_cfg.get("min_price", 100)),
        max_price=float(dataset_cfg.get("max_price", 200000)),
        min_year=int(dataset_cfg.get("min_year", 1970)),
        max_year=int(dataset_cfg.get("max_year", 2026)),
        max_odometer=float(dataset_cfg.get("max_odometer", 500000)),
    )

    df_raw = load_vehicles_csv(csv_path, sample_n=dataset_cfg.get("sample_n", None))
    df = clean_dataset(df_raw, target=target, features=features, spec=spec)

    fit = fit_from_config(df=df, cfg=cfg)

    repo_root = get_repo_root()
    cmd = " ".join([sys.executable, *sys.argv])
    if args.outdir is None:
        outdir = create_run_dir(runs_root=repo_root / "runs", name=args.run_name)
    else:
        outdir = Path(args.outdir)
        outdir.mkdir(parents=True, exist_ok=True)

    copied_cfg_path = copy_config(args.config, outdir)
    meta = RunMeta(
        created_utc=utc_now(),
        name=str(args.run_name),
        cmd=cmd,
        config_path=str(copied_cfg_path),
        git_head_sha=git_head_sha(repo_root),
        extra={"n_rows_clean": int(df.shape[0])},
    )
    write_meta(outdir / "meta.json", meta)

    save_run(outdir=outdir, fit=fit, config_path=copied_cfg_path)

    print("Wrote run dir:", outdir)
    print("Test metrics:", fit.metrics["test"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
