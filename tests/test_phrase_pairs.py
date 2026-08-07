import csv
import tempfile
import unittest
from pathlib import Path

import randomizer


class PhrasePairTests(unittest.TestCase):
    def test_load_phrase_pairs_reads_complete_intro_conclusion_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            phrase_path = Path(tmpdir) / "phrases.csv"
            with phrase_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["Introduction", "Conclusion"])
                writer.writerow(["I'm looking for a restaurant", "that fits my taste."])
                writer.writerow(["Can you find me a place", "for dinner."])

            phrase_pairs = randomizer.load_phrase_pairs(phrase_path)

            self.assertEqual(
                phrase_pairs,
                [
                    ("I'm looking for a restaurant", "that fits my taste."),
                    ("Can you find me a place", "for dinner."),
                ],
            )

    def test_format_row_as_sentence_uses_one_complete_phrase_pair(self):
        phrase_pairs = [("Can you find me a restaurant", "for dinner.")]

        sentence = randomizer.format_row_as_sentence(["walkable", "quiet place"], phrase_pairs)

        self.assertEqual(
            sentence,
            "Can you find me a restaurant that is walkable and quiet place for dinner.",
        )


if __name__ == "__main__":
    unittest.main()
