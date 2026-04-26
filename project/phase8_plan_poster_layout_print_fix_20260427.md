# Phase 8 Plan — Poster Layout and Print Fix

Date: 2026-04-27

## Objective

Fix the remaining DSCI441 poster issues reported after the previous content pass:

1. figure widths are too uniform,
2. layout should respond to original figure aspect ratios,
3. browser print/export should not crop the bottom of the poster,
4. right-column density should remain visually balanced after layout changes.

## Planned changes

1. Replace the current print-scale workaround with a print layout closer to the DSCI498 approach.
2. Keep fixed poster dimensions for both screen and print, but separate print sizing from screen centering behavior.
3. Re-layout figures:
   - square / near-square figures may appear side-by-side,
   - wide figures should remain full-width,
   - figure containers should be slightly wider overall.
4. Re-render:
   - poster HTML screenshot,
   - regenerated PDF,
   - rasterized check of the PDF if needed.

## Acceptance

- Browser print no longer cuts off the poster bottom.
- Figure widths better reflect original aspect ratios.
- Poster still exports as one page and remains visually balanced.
