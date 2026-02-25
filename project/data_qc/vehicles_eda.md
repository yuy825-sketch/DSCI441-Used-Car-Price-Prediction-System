# Exploratory Data Analysis Report

Generated: 2026-02-25T23:39:44.266921

## File Information

- **Filename**: vehicles.csv
- **Path**: `/data/private/user2/workspace/backup/303/DSCI441-Used-Car-Price-Prediction-System/data/craigslist/vehicles.csv`
- **Size**: 1.35 GB (1447955215 bytes)
- **Modified**: 2026-02-25T23:29:28.828465

## Detected File Type

- **Extension**: `.csv`
- **Category**: general_scientific
- **Description**: Comma-Separated Values

## Data Analysis

### Tabular QC Summary (sampled)

| column | dtype | missing | missing_pct | nunique | outliers_iqr |
| --- | --- | ---: | ---: | ---: | ---: |
| id | int64 | 0 | 0.0 | 10000 | 27 |
| url | object | 0 | 0.0 | 10000 |  |
| region | object | 0 | 0.0 | 28 |  |
| region_url | object | 0 | 0.0 | 28 |  |
| price | int64 | 0 | 0.0 | 1790 | 138 |
| year | float64 | 113 | 0.0113 | 90 | 517 |
| manufacturer | object | 483 | 0.0483 | 39 |  |
| model | object | 129 | 0.0129 | 2468 |  |
| condition | object | 4653 | 0.4653 | 7 |  |
| cylinders | object | 3287 | 0.3287 | 9 |  |
| fuel | object | 122 | 0.0122 | 6 |  |
| odometer | float64 | 58 | 0.0058 | 4916 | 157 |
| title_status | object | 247 | 0.0247 | 7 |  |
| transmission | object | 83 | 0.0083 | 4 |  |
| VIN | object | 3119 | 0.3119 | 3782 |  |
| drive | object | 2899 | 0.2899 | 4 |  |
| size | object | 7400 | 0.74 | 5 |  |
| type | object | 1851 | 0.1851 | 14 |  |
| paint_color | object | 2016 | 0.2016 | 13 |  |
| image_url | object | 27 | 0.0027 | 6456 |  |
| description | object | 27 | 0.0027 | 8441 |  |
| county | float64 | 10000 | 1.0 | 1 | 0 |
| state | object | 0 | 0.0 | 13 |  |
| lat | float64 | 72 | 0.0072 | 1388 | 2 |
| long | float64 | 72 | 0.0072 | 1391 | 1 |
| posting_date | object | 27 | 0.0027 | 9795 |  |

```json
{
  "shape_sampled": [
    10000,
    26
  ],
  "columns": [
    "id",
    "url",
    "region",
    "region_url",
    "price",
    "year",
    "manufacturer",
    "model",
    "condition",
    "cylinders",
    "fuel",
    "odometer",
    "title_status",
    "transmission",
    "VIN",
    "drive",
    "size",
    "type",
    "paint_color",
    "image_url",
    "description",
    "county",
    "state",
    "lat",
    "long",
    "posting_date"
  ],
  "dtypes": {
    "id": "int64",
    "url": "object",
    "region": "object",
    "region_url": "object",
    "price": "int64",
    "year": "float64",
    "manufacturer": "object",
    "model": "object",
    "condition": "object",
    "cylinders": "object",
    "fuel": "object",
    "odometer": "float64",
    "title_status": "object",
    "transmission": "object",
    "VIN": "object",
    "drive": "object",
    "size": "object",
    "type": "object",
    "paint_color": "object",
    "image_url": "object",
    "description": "object",
    "county": "float64",
    "state": "object",
    "lat": "float64",
    "long": "float64",
    "posting_date": "object"
  },
  "missing_values_sampled": {
    "id": 0,
    "url": 0,
    "region": 0,
    "region_url": 0,
    "price": 0,
    "year": 113,
    "manufacturer": 483,
    "model": 129,
    "condition": 4653,
    "cylinders": 3287,
    "fuel": 122,
    "odometer": 58,
    "title_status": 247,
    "transmission": 83,
    "VIN": 3119,
    "drive": 2899,
    "size": 7400,
    "type": 1851,
    "paint_color": 2016,
    "image_url": 27,
    "description": 27,
    "county": 10000,
    "state": 0,
    "lat": 72,
    "long": 72,
    "posting_date": 27
  },
  "missing_pct_sampled": {
    "id": 0.0,
    "url": 0.0,
    "region": 0.0,
    "region_url": 0.0,
    "price": 0.0,
    "year": 0.0113,
    "manufacturer": 0.0483,
    "model": 0.0129,
    "condition": 0.4653,
    "cylinders": 0.3287,
    "fuel": 0.0122,
    "odometer": 0.0058,
    "title_status": 0.0247,
    "transmission": 0.0083,
    "VIN": 0.3119,
    "drive": 0.2899,
    "size": 0.74,
    "type": 0.1851,
    "paint_color": 0.2016,
    "image_url": 0.0027,
    "description": 0.0027,
    "county": 1.0,
    "state": 0.0,
    "lat": 0.0072,
    "long": 0.0072,
    "posting_date": 0.0027
  },
  "duplicate_rows_sampled": 0,
  "nunique_sampled": {
    "id": 10000,
    "url": 10000,
    "region": 28,
    "region_url": 28,
    "price": 1790,
    "year": 90,
    "manufacturer": 39,
    "model": 2468,
    "condition": 7,
    "cylinders": 9,
    "fuel": 6,
    "odometer": 4916,
    "title_status": 7,
    "transmission": 4,
    "VIN": 3782,
    "drive": 4,
    "size": 5,
    "type": 14,
    "paint_color": 13,
    "image_url": 6456,
    "description": 8441,
    "county": 1,
    "state": 13,
    "lat": 1388,
    "long": 1391,
    "posting_date": 9795
  },
  "summary_statistics_sampled": {
    "id": {
      "count": 10000.0,
      "mean": 7309865075.8615,
      "std": 6548737.610692342,
      "min": 7208549803.0,
      "25%": 7306470514.75,
      "50%": 7310598603.0,
      "75%": 7314113311.5,
      "max": 7316893890.0
    },
    "price": {
      "count": 10000.0,
      "mean": 130303.0093,
      "std": 9926714.83203497,
      "min": 0.0,
      "25%": 9995.0,
      "50%": 20000.0,
      "75%": 29995.0,
      "max": 987654321.0
    },
    "year": {
      "count": 9887.0,
      "mean": 2011.938909679377,
      "std": 9.978193406743806,
      "min": 1903.0,
      "25%": 2010.0,
      "50%": 2015.0,
      "75%": 2018.0,
      "max": 2022.0
    },
    "odometer": {
      "count": 9942.0,
      "mean": 105944.4612753973,
      "std": 459717.97471693926,
      "min": 0.0,
      "25%": 27715.75,
      "50%": 67500.0,
      "75%": 123456.0,
      "max": 10000000.0
    },
    "county": {
      "count": 0.0,
      "mean": NaN,
      "std": NaN,
      "min": NaN,
      "25%": NaN,
      "50%": NaN,
      "75%": NaN,
      "max": NaN
    },
    "lat": {
      "count": 9928.0,
      "mean": 43.3323210099718,
      "std": 13.354179095401168,
      "min": -81.838232,
      "25%": 33.4653,
      "50%": 34.768443,
      "75%": 61.16167,
      "max": 64.993698
    },
    "long": {
      "count": 9928.0,
      "mean": -111.36701411986301,
      "std": 29.04180409710664,
      "min": -158.5996,
      "25%": -149.847206,
      "50%": -88.105874,
      "75%": -86.653907,
      "max": 173.885502
    }
  },
  "outliers_iqr_sampled": {
    "id": {
      "outliers_iqr": 27,
      "q1": 7306470514.75,
      "q3": 7314113311.5
    },
    "price": {
      "outliers_iqr": 138,
      "q1": 9995.0,
      "q3": 29995.0
    },
    "year": {
      "outliers_iqr": 517,
      "q1": 2010.0,
      "q3": 2018.0
    },
    "odometer": {
      "outliers_iqr": 157,
      "q1": 27715.75,
      "q3": 123456.0
    },
    "county": {
      "outliers_iqr": 0,
      "q1": NaN,
      "q3": NaN
    },
    "lat": {
      "outliers_iqr": 2,
      "q1": 33.4653,
      "q3": 61.16167
    },
    "long": {
      "outliers_iqr": 1,
      "q1": -149.847206,
      "q3": -86.653907
    }
  },
  "sampling_note": "Computed on first 10k rows (pandas)."
}
```

## Recommendations for Further Analysis

Based on the file type (`.csv`), consider the following analyses:

- Statistical distribution analysis
- Missing value imputation strategies
- Correlation analysis between variables
- Outlier detection and handling
- Dimensionality reduction (PCA, t-SNE)

---
*This report was generated by the data-quality-eda-results skill.*