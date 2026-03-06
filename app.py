from __future__ import annotations

import html
from io import BytesIO
from typing import Dict, List, Set
import base64

import streamlit as st

from viewer.constants import ALL_CATEGORIES_OPTION, CATEGORY_COLORS, CATEGORY_LABELS, CATEGORY_ORDER
from viewer.data import fetch_records, filter_labels, matching_indices
from viewer.keyboard import inject_keyboard_shortcuts
from viewer.models import ImageRecord
from viewer.navigation import next_index
from viewer.render import draw_overlays


st.set_page_config(page_title="X-AIGD Label Viewer", layout="centered")

DATASET_OPTIONS = {
    "X-AIGD-demo": "Coxy7/X-AIGD-demo",
    "X-AIGD": "Coxy7/X-AIGD",
}


@st.cache_resource(show_spinner=False)
def load_records_cached(dataset_repo: str, split: str) -> List[ImageRecord]:
    return fetch_records(dataset_repo, split)


def init_state() -> None:
    state = st.session_state
    state.setdefault("dataset_name", "X-AIGD-demo")
    state.setdefault("dataset_repo", "Coxy7/X-AIGD-demo")
    state.setdefault("split", "labeled_train")
    state.setdefault("selected_category", ALL_CATEGORIES_OPTION)
    state.setdefault("current_index", 0)
    state.setdefault("source_key", "")
    state.setdefault("matching_indices_by_category", {})
    state.setdefault("overlay_selection_scope", "")
    state.setdefault("visible_overlay_categories", CATEGORY_ORDER.copy())
    state.setdefault("jump_input_scope", "")
    state.setdefault("jump_image_input", "1")
    state.setdefault("jump_match_input", "1")
    state.setdefault("total_records", 0)


def legend_style_key(category: str) -> str:
    return f"legend_{CATEGORY_ORDER.index(category)}"


def inject_compact_styles() -> None:
    legend_button_styles = []
    for category in CATEGORY_ORDER:
        style_key = legend_style_key(category)
        hex_color = CATEGORY_COLORS[category]["hex"]
        red, green, blue, _ = CATEGORY_COLORS[category]["rgba"]
        legend_button_styles.append(
            f"""
            .st-key-{style_key} button {{
              border: 2px solid {hex_color};
              background: rgba({red}, {green}, {blue}, 0.08);
              color: rgb(49, 51, 63);
              min-height: 2.35rem;
            }}

            .st-key-{style_key} button[kind="secondary"] {{
              opacity: 0.45;
              background: rgba({red}, {green}, {blue}, 0.03);
            }}

            .st-key-{style_key} button[kind="primary"] {{
              opacity: 1;
              box-shadow: 0 0 0 1px {hex_color} inset;
              font-weight: 600;
            }}

            .st-key-{style_key} button:disabled {{
              opacity: 0.22;
            }}
            """
        )

    st.html(
        f"""
        <style>
        .stApp .block-container {{
          padding-top: 0.4rem;
          padding-bottom: 0.4rem;
        }}

        .viewer-header {{
          margin-bottom: 0.2rem;
        }}

        .viewer-header h1 {{
          font-size: 1.2rem;
          line-height: 1.2;
          margin: 0;
        }}

        .viewer-info-grid {{
          margin: 0.08rem 0 0.2rem;
        }}

        .viewer-info-label {{
          display: block;
          font-size: 0.72rem;
          text-transform: uppercase;
          letter-spacing: 0.04em;
          color: rgba(49, 51, 63, 0.62);
          margin-bottom: 0.02rem;
        }}

        .viewer-info-value {{
          display: block;
          font-size: 0.9rem;
          line-height: 1.05;
          color: rgb(49, 51, 63);
          overflow-wrap: anywhere;
        }}

        .viewer-info-inline-value {{
          display: inline-flex;
          align-items: center;
          font-size: 0.9rem;
          line-height: 1.85rem;
          color: rgb(49, 51, 63);
          white-space: nowrap;
          height: 1.85rem;
        }}

        .viewer-info-suffix {{
          display: inline-flex;
          align-items: center;
          justify-content: flex-end;
          font-size: 0.9rem;
          line-height: 1.85rem;
          color: rgb(49, 51, 63);
          white-space: nowrap;
          text-align: right;
          height: 1.85rem;
        }}

        .st-key-info_grid [data-testid="stColumn"] {{
          align-self: stretch;
        }}

        [class*="st-key-info_card_"] [data-testid="stVerticalBlockBorderWrapper"] {{
          background: rgba(249, 250, 251, 0.9);
          padding: 0.04rem 0.18rem;
          display: flex;
          flex-direction: column;
          justify-content: center;
        }}

        [class*="st-key-info_card_"] [data-testid="stVerticalBlock"] {{
          gap: 0;
          justify-content: center;
        }}

        [class*="st-key-info_card_"] [data-testid="stMarkdownContainer"] p {{
          margin: 0;
        }}

        .st-key-info_grid > [data-testid="stVerticalBlock"] {{
          gap: 0.35rem;
        }}

        .st-key-info_grid div[data-baseweb="input"] input {{
          font-size: 0.9rem;
          padding-top: 0.08rem;
          padding-bottom: 0.08rem;
        }}

        .st-key-info_grid div[data-baseweb="input"] > div {{
          min-height: 1.85rem;
        }}

        .st-key-info_grid div[data-baseweb="input"] button {{
          min-height: 1.85rem;
          padding-top: 0.05rem;
          padding-bottom: 0.05rem;
        }}

        .st-key-legend_grid > [data-testid="stVerticalBlock"] {{
          gap: 0.12rem;
        }}

        @media (max-width: 900px) {{
          .viewer-info-grid {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
          }}

        }}
        {"".join(legend_button_styles)}
        </style>
        """,
        width="stretch",
    )


def build_matching_index_map(records: List[ImageRecord]) -> Dict[str, List[int]]:
    matching = {ALL_CATEGORIES_OPTION: list(range(len(records)))}
    for category in CATEGORY_ORDER:
        matching[category] = matching_indices(records, category)
    return matching


def set_category(category: str) -> None:
    st.session_state.selected_category = category


def set_overlay_categories(categories: List[str], scope: str) -> None:
    st.session_state.visible_overlay_categories = categories
    st.session_state.overlay_selection_scope = scope


def toggle_overlay_category(category: str) -> None:
    selected = list(st.session_state.visible_overlay_categories)
    if category in selected:
        selected.remove(category)
    else:
        selected.append(category)
    ordered_selected = [item for item in CATEGORY_ORDER if item in selected]
    st.session_state.visible_overlay_categories = ordered_selected


def step_image(direction: int) -> None:
    active_indices = st.session_state.matching_indices_by_category.get(
        st.session_state.selected_category,
        [],
    )
    st.session_state.current_index = next_index(
        st.session_state.current_index,
        direction,
        active_indices,
    )


def category_shortcut_buttons() -> None:
    st.sidebar.markdown("### Quick Filters")
    st.sidebar.button(
        "0 All",
        width="stretch",
        on_click=set_category,
        args=[ALL_CATEGORIES_OPTION],
    )
    for index, category in enumerate(CATEGORY_ORDER, start=1):
        st.sidebar.button(
            f"{index} {CATEGORY_LABELS[category]}",
            key=f"quick-{category}",
            width="stretch",
            on_click=set_category,
            args=[category],
        )


def navigation_buttons(active_indices: List[int]) -> None:
    previous_disabled = not active_indices
    next_disabled = not active_indices
    left_col, right_col = st.columns(2)
    left_col.button(
        "Previous",
        width="stretch",
        disabled=previous_disabled,
        on_click=step_image,
        args=[-1],
    )
    right_col.button(
        "Next",
        width="stretch",
        disabled=next_disabled,
        on_click=step_image,
        args=[1],
    )


def render_image(image) -> None:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    st.html(
        f"""
        <div style="display:flex;justify-content:center;width:100%;">
          <img
            src="data:image/png;base64,{encoded}"
            alt="X-AIGD sample"
            style="
              max-width:100%;
              max-height:66vh;
              width:auto;
              height:auto;
              object-fit:contain;
              border:1px solid rgba(128, 128, 128, 0.35);
              border-radius:0.5rem;
            "
          />
        </div>
        """,
        width="stretch",
    )


def matching_progress(active_indices: List[int], current_index: int) -> str:
    total_matches = len(active_indices)
    if total_matches == 0:
        return "0 / 0"
    if current_index not in active_indices:
        return f"0 / {total_matches}"
    return f"{active_indices.index(current_index) + 1} / {total_matches}"


def matching_position(active_indices: List[int], current_index: int) -> int | None:
    if current_index not in active_indices:
        return None
    return active_indices.index(current_index) + 1


def sync_jump_inputs(total_records: int, active_indices: List[int]) -> None:
    desired_image = max(1, min(st.session_state.current_index + 1, total_records))
    desired_match = matching_position(active_indices, st.session_state.current_index) or 1
    desired_scope = (
        f"{st.session_state.source_key}:{st.session_state.selected_category}:"
        f"{st.session_state.current_index}:{len(active_indices)}"
    )

    if st.session_state.jump_input_scope != desired_scope:
        st.session_state.jump_image_input = str(desired_image)
        st.session_state.jump_match_input = str(desired_match)
        st.session_state.jump_input_scope = desired_scope


def parse_jump_value(raw_value: str) -> int | None:
    try:
        return int(raw_value.strip())
    except (TypeError, ValueError):
        return None


def jump_to_image() -> None:
    target = parse_jump_value(st.session_state.jump_image_input)
    if target is None:
        st.session_state.jump_image_input = str(st.session_state.current_index + 1)
        return
    total_records = max(1, st.session_state.total_records)
    target = max(1, min(target, total_records))
    st.session_state.current_index = target - 1
    st.session_state.jump_image_input = str(target)


def jump_to_matching() -> None:
    active_indices = st.session_state.matching_indices_by_category.get(
        st.session_state.selected_category,
        [],
    )
    if not active_indices:
        return
    target = parse_jump_value(st.session_state.jump_match_input)
    if target is None:
        current_position = matching_position(active_indices, st.session_state.current_index) or 1
        st.session_state.jump_match_input = str(current_position)
        return
    position = max(1, min(target, len(active_indices)))
    st.session_state.current_index = active_indices[position - 1]
    st.session_state.jump_match_input = str(position)


def sync_overlay_selection(base_labels: List) -> None:
    current_scope = (
        f"{st.session_state.source_key}:{st.session_state.current_index}:{st.session_state.selected_category}"
    )
    available_categories = [category for category in CATEGORY_ORDER if any(label.category == category for label in base_labels)]

    if st.session_state.overlay_selection_scope != current_scope:
        set_overlay_categories(available_categories, current_scope)
        return

    preserved = [category for category in st.session_state.visible_overlay_categories if category in available_categories]
    if preserved != st.session_state.visible_overlay_categories:
        set_overlay_categories(preserved, current_scope)


def render_legend(available_categories: Set[str]) -> None:
    selected_categories = set(st.session_state.visible_overlay_categories)

    with st.container(key="legend_grid", gap="xsmall"):
        first_row = st.columns(4, gap="xsmall")
        second_row = st.columns(3, gap="xsmall")

        for index, category in enumerate(CATEGORY_ORDER):
            prefix = "☑" if category in selected_categories else "☐"
            label = f"{prefix} {CATEGORY_LABELS[category]}"
            target_column = first_row[index] if index < 4 else second_row[index - 4]
            target_column.button(
                label,
                key=legend_style_key(category),
                width="stretch",
                disabled=category not in available_categories,
                type="primary" if category in selected_categories else "secondary",
                on_click=toggle_overlay_category,
                args=[category],
            )


def render_info_panel(
    record: ImageRecord,
    active_indices: List[int],
    visible_labels: int,
    total_records: int,
) -> None:
    st.session_state.total_records = total_records
    sync_jump_inputs(total_records, active_indices)
    with st.container(key="info_grid", gap='xsmall'):
        first_row = st.columns(3, gap="xsmall")
        second_row = st.columns(3, gap="xsmall")

    with first_row[0]:
        with st.container(border=True, key="info_card_generator", height=64):
            st.markdown("<span class='viewer-info-label'>Generator</span>", unsafe_allow_html=True)
            st.markdown(f"<span class='viewer-info-value'>{html.escape(record.generator)}</span>", unsafe_allow_html=True)

    with first_row[1]:
        with st.container(border=True, key="info_card_uid", height=64):
            st.markdown("<span class='viewer-info-label'>UID</span>", unsafe_allow_html=True)
            st.markdown(f"<span class='viewer-info-value'>{html.escape(record.uid)}</span>", unsafe_allow_html=True)

    with first_row[2]:
        with st.container(border=True, key="info_card_resolution", height=64):
            st.markdown("<span class='viewer-info-label'>Resolution</span>", unsafe_allow_html=True)
            st.markdown(
                f"<span class='viewer-info-value'>{record.width} x {record.height}</span>",
                unsafe_allow_html=True,
            )

    with second_row[0]:
        with st.container(border=True, key="info_card_image", height=64, horizontal=True, gap="xsmall"):
            st.markdown("<span class='viewer-info-label'>Image</span>", unsafe_allow_html=True)
            with st.container(horizontal=True, vertical_alignment="center", gap="small"):
                st.text_input(
                    "Image",
                    key="jump_image_input",
                    label_visibility="collapsed",
                    on_change=jump_to_image,
                    width=80,
                )
                st.html(
                    f"<div class='viewer-info-suffix'>/ {total_records}</div>",
                    width="content",
                )

    with second_row[1]:
        with st.container(border=True, key="info_card_matching", height=64, horizontal=True, gap="xsmall"):
            st.markdown("<span class='viewer-info-label'>Filtered</span>", unsafe_allow_html=True)
            with st.container(horizontal=True, vertical_alignment="center", gap="small"):
                st.text_input(
                    "Filtered",
                    key="jump_match_input",
                    label_visibility="collapsed",
                    on_change=jump_to_matching,
                    width=80,
                    disabled=not active_indices,
                )
                st.html(
                    f"<div class='viewer-info-suffix'>/ {len(active_indices)}</div>",
                    width="content",
                )

    with second_row[2]:
        with st.container(border=True, key="info_card_visible", height=64, gap="xsmall"):
            st.markdown("<span class='viewer-info-label'>Visible Labels</span>", unsafe_allow_html=True)
            st.html(
                f"<div class='viewer-info-inline-value'>{visible_labels} / {len(record.labels)}</div>",
                width="content",
            )


@st.fragment
def render_viewer(records: List[ImageRecord]) -> None:
    active_indices = st.session_state.matching_indices_by_category[st.session_state.selected_category]
    filtered_count = len(active_indices)

    record = records[st.session_state.current_index]
    base_labels = filter_labels(record, st.session_state.selected_category)
    sync_overlay_selection(base_labels)
    selected_overlay_categories = set(st.session_state.visible_overlay_categories)
    visible_labels = [label for label in base_labels if label.category in selected_overlay_categories]
    rendered_image, skipped_count = draw_overlays(record.image, visible_labels)
    available_categories = {label.category for label in base_labels}

    render_legend(available_categories)
    render_image(rendered_image)
    render_info_panel(record, active_indices, len(visible_labels), len(records))

    if st.session_state.selected_category != ALL_CATEGORIES_OPTION and not base_labels:
        st.info("No matching artifacts on this image.")
    elif base_labels and not visible_labels:
        st.info("No categories selected in the legend for this image.")
    if st.session_state.selected_category != ALL_CATEGORIES_OPTION and filtered_count == 0:
        st.warning("No images in this split contain the selected category.")
    if skipped_count:
        st.warning(f"Skipped {skipped_count} malformed polygon(s) on this image.")

    navigation_buttons(active_indices)


def main() -> None:
    init_state()
    inject_compact_styles()
    inject_keyboard_shortcuts()

    st.html(
        """
        <div class="viewer-header">
          <h1>X-AIGD Label Viewer</h1>
        </div>
        """,
        width="stretch",
    )

    st.sidebar.selectbox(
        "Dataset",
        options=list(DATASET_OPTIONS.keys()),
        key="dataset_name",
    )
    st.session_state.dataset_repo = DATASET_OPTIONS[st.session_state.dataset_name]
    st.sidebar.selectbox(
        "Split",
        options=["labeled_train", "labeled_test"],
        key="split",
    )

    new_source_key = f"{st.session_state.dataset_repo}:{st.session_state.split}"
    if new_source_key != st.session_state.source_key:
        st.session_state.source_key = new_source_key
        st.session_state.current_index = 0

    try:
        records = load_records_cached(st.session_state.dataset_repo, st.session_state.split)
    except Exception as exc:  # pragma: no cover - UI error path
        st.error(f"Failed to load dataset: {exc}")
        return

    if not records:
        st.warning("The selected dataset split is empty.")
        return

    st.session_state.current_index = max(0, min(st.session_state.current_index, len(records) - 1))
    st.session_state.matching_indices_by_category = build_matching_index_map(records)

    st.sidebar.selectbox(
        "Category filter",
        options=[ALL_CATEGORIES_OPTION, *CATEGORY_ORDER],
        key="selected_category",
        format_func=lambda option: option if option == ALL_CATEGORIES_OPTION else CATEGORY_LABELS[option],
    )

    category_shortcut_buttons()
    render_viewer(records)


if __name__ == "__main__":
    main()
