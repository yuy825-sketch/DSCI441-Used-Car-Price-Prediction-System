# Data (local, not committed)

This project expects the Craigslist dataset CSV at:

```
data/craigslist/vehicles.csv
```

Recommended source (Kaggle):
- `austinreese/craigslist-carstrucks-data`

Download helper:
```
python scripts/download_kaggle_dataset.py
```

Notes:
- The `data/` folder is ignored by git.
- Kaggle downloads require API credentials:
  - Preferred: `KAGGLE_API_TOKEN` (env) or `~/.kaggle/kaggle_api_token`
  - Legacy: `~/.kaggle/kaggle.json` or `KAGGLE_USERNAME`/`KAGGLE_KEY`
