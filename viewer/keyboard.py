from __future__ import annotations

import streamlit as st

from viewer.constants import CATEGORY_LABELS, CATEGORY_ORDER


def button_label_map() -> dict[str, str]:
    labels = {
        "ArrowLeft": "Previous (←/A)",
        "ArrowRight": "Next (→/D)",
        "a": "Previous (←/A)",
        "A": "Previous (←/A)",
        "d": "Next (→/D)",
        "D": "Next (→/D)",
        "0": "0 All",
    }
    for index, category in enumerate(CATEGORY_ORDER, start=1):
        labels[str(index)] = f"{index} {CATEGORY_LABELS[category]}"
    return labels


def inject_keyboard_shortcuts() -> None:
    labels = button_label_map()
    st.html(
        f"""
        <script>
        if (!window.__xaigdViewerShortcutsInstalled) {{
          window.__xaigdViewerShortcutsInstalled = true;
          const buttonLabels = {labels!r};

          const normalize = (value) => value.replace(/\\s+/g, " ").trim();
          const clickButton = (label) => {{
            const buttons = Array.from(document.querySelectorAll("button"));
            const target = buttons.find((button) => !button.disabled && normalize(button.textContent || "") === label);
            if (target) {{
              target.click();
              return true;
            }}
            return false;
          }};

          window.addEventListener("keydown", (event) => {{
            const active = event.target;
            const tag = active && active.tagName ? active.tagName.toLowerCase() : "";
            const role = active && active.getAttribute ? active.getAttribute("role") : "";
            if (
              tag === "input" ||
              tag === "textarea" ||
              tag === "select" ||
              role === "combobox" ||
              (active && active.isContentEditable)
            ) {{
              return;
            }}

            const label = buttonLabels[event.key];
            if (!label) {{
              return;
            }}

            event.preventDefault();
            clickButton(label);
          }}, true);
        }}
        </script>
        """,
        width="content",
        unsafe_allow_javascript=True,
    )
