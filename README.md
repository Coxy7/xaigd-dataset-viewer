# X-AIGD Label Viewer

Local Streamlit app for browsing X-AIGD images with artifact polygon overlays.

## Requirements

- Python 3.10+
- Access to a Python environment with `streamlit`, `datasets`, and `pillow`

## Run

```bash
streamlit run app.py
```

By default the app loads `Coxy7/X-AIGD-demo` and starts on the `labeled_train` split. You can switch between `Coxy7/X-AIGD-demo` and `Coxy7/X-AIGD` in the sidebar. The app loads only the labeled parquet split you select, so it does not fetch the unlabeled splits.

## Controls

- `Left` / `Right`: previous and next image
- `0`: clear category filter
- `1`-`7`: select categories in spec order
- Sidebar category selector and quick filter buttons
- Prev/Next buttons under the image

## Tests

```bash
python -m unittest discover -s tests -v
```

If you install the optional dev dependencies, `pytest` also works:

```bash
python -m pytest
```
