"""Unit tests for traditional almanac heuristics."""

import unittest

from app.logic import traditional_rules as tr


class TraditionalRulesTest(unittest.TestCase):
    def test_recommended_crop_waxing_water(self) -> None:
        self.assertEqual(tr.recommended_crop_category("waxing", "Water"), "Leaf")

    def test_phenology_mouse_ear_band(self) -> None:
        m, d = tr.phenology_flags(400.0)
        self.assertTrue(m)
        self.assertFalse(d)

    def test_wise_council_caution_when_dry_and_traditional_favors(self) -> None:
        r = tr.wise_council(True, True)
        self.assertEqual(r.modern_traditional_alignment, "caution")
        self.assertIsNotNone(r.wise_council_tip)

    def test_wise_council_aligned(self) -> None:
        r = tr.wise_council(True, False)
        self.assertEqual(r.modern_traditional_alignment, "aligned")
        self.assertIsNone(r.wise_council_tip)


if __name__ == "__main__":
    unittest.main()
