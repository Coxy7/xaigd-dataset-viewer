from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

from viewer.data import ImageLRUCache


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
APP_SPEC = importlib.util.spec_from_file_location("dataset_viewer_app", APP_PATH)
assert APP_SPEC is not None and APP_SPEC.loader is not None
app = importlib.util.module_from_spec(APP_SPEC)
APP_SPEC.loader.exec_module(app)


class AppStateTests(unittest.TestCase):
    def test_next_overlay_categories_hides_all_when_all_available_are_selected(self) -> None:
        next_categories = app.next_overlay_categories(
            ["low-level-edge_shape", "low-level-texture"],
            ["low-level-edge_shape", "low-level-texture"],
        )

        self.assertEqual(next_categories, [])

    def test_next_overlay_categories_shows_all_when_subset_is_selected(self) -> None:
        next_categories = app.next_overlay_categories(
            ["low-level-edge_shape"],
            ["low-level-edge_shape", "low-level-texture"],
        )

        self.assertEqual(
            next_categories,
            ["low-level-edge_shape", "low-level-texture"],
        )

    def test_apply_source_change_resets_navigation_and_image_cache(self) -> None:
        original_cache = ImageLRUCache(capacity=app.IMAGE_CACHE_CAPACITY)
        original_cache.put(("repo", "labeled_train", 0), object())
        state = {
            "source_key": "Coxy7/X-AIGD-demo:labeled_train",
            "current_index": 7,
            "image_cache": original_cache,
        }

        app.apply_source_change(state, "Coxy7/X-AIGD-demo:labeled_test")

        self.assertEqual(state["source_key"], "Coxy7/X-AIGD-demo:labeled_test")
        self.assertEqual(state["current_index"], 0)
        self.assertIsInstance(state["image_cache"], ImageLRUCache)
        self.assertIsNot(state["image_cache"], original_cache)
        self.assertEqual(len(state["image_cache"]), 0)

    def test_apply_source_change_keeps_existing_cache_when_source_unchanged(self) -> None:
        cache = ImageLRUCache(capacity=app.IMAGE_CACHE_CAPACITY)
        state = {
            "source_key": "Coxy7/X-AIGD-demo:labeled_train",
            "current_index": 4,
            "image_cache": cache,
        }

        app.apply_source_change(state, "Coxy7/X-AIGD-demo:labeled_train")

        self.assertEqual(state["current_index"], 4)
        self.assertIs(state["image_cache"], cache)


if __name__ == "__main__":
    unittest.main()
