# Notes

## Dataset
Craigslist vehicles data contains many columns; this project starts with a conservative feature subset:
- numeric: `year`, `odometer`, derived `car_age`
- categorical: `manufacturer`, `condition`, `fuel`, `transmission`, `drive`, `type`, `paint_color`, `state`

## Cleaning assumptions (adjustable in configs)
- Drop rows with missing/invalid `price`
- Filter extreme prices and odometer values
- Filter year range to remove outliers (e.g., pre-1970)

