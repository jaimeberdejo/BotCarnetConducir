from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from botcarnet.importer import _parse_correct, _resolve_image_name


class ImporterTests(unittest.TestCase):
    def test_parse_correct_returns_selected_index(self) -> None:
        self.assertEqual(_parse_correct("0 1 0"), 1)
        self.assertEqual(_parse_correct("1 0 0"), 0)
        self.assertEqual(_parse_correct("0 0 1"), 2)

    def test_resolve_image_name_matches_existing_file_case_insensitive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            (base / "1234.JPG").write_text("x", encoding="utf-8")
            self.assertEqual(_resolve_image_name("1234.jpg", base), "1234.JPG")


if __name__ == "__main__":
    unittest.main()
