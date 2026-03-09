# X-AIGD Label Viewer

Local Streamlit app for browsing labeled X-AIGD images with artifact polygon overlays.

## Requirements

- Python 3.10+
- Access to a Python environment with `streamlit`, `datasets`, and `pillow`

## Run

```bash
streamlit run app.py
```

By default the app loads `Coxy7/X-AIGD-demo` and starts on the `labeled_train` split.

## Data Sources

- Sidebar dataset switcher:
  - `X-AIGD-demo` -> `Coxy7/X-AIGD-demo`
  - `X-AIGD` -> `Coxy7/X-AIGD`
- Sidebar split switcher:
  - `labeled_train`
  - `labeled_test`
- The app loads only the selected labeled parquet split. Unlabeled splits are not downloaded.

## Viewer Features

- Single-image viewer with artifact polygon overlays.
- Polygons are rendered as colored outlines only.
- Generator, UID, resolution, image index, filtered-match index, and visible-label count are shown in the info panel below the image.
- Jump directly to an absolute image index or to a filtered matching-image index from the info panel.
- Category legend above the image:
  - click a legend item to toggle that category on the current image only
  - selected categories are highlighted
  - unavailable categories are dimmed and disabled
- Global dataset filtering from the sidebar:
  - `All` or one of the seven artifact categories
  - changing the sidebar filter does not force a jump away from the current image

## Controls

- `Left` / `Right` or `A` / `D`: previous and next image
- `0`: clear category filter
- `1`-`7`: select categories in spec order
- Sidebar dataset selector, split selector, category selector, and quick filter buttons
- Prev/Next buttons under the image
