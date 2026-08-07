import csv
import tempfile
import unittest
from pathlib import Path

import openpyxl

import randomizer


class RandomizerTests(unittest.TestCase):
    def test_generate_rows_creates_two_criteria_per_row(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "criteria.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["Category A", "Category B", "Category C"])
                writer.writerow(["Alpha", "Beta", "Gamma"])
                writer.writerow(["Delta", "Epsilon", "Zeta"])

            criteria = randomizer.load_flat_criteria_from_csv(csv_path)
            rows = randomizer.generate_rows(criteria, row_count=4, criteria_per_row=2)

            self.assertEqual(len(rows), 4)
            for row in rows:
                self.assertEqual(len(row), 2)
                self.assertTrue(all(item in criteria for item in row))

    def test_write_rows_preserves_two_criteria_and_adds_sentence_column(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "criteria_output.csv"
            rows = [["walkable", "quiet place"], ["budget", "pet friendly"]]

            randomizer.write_rows(rows, output_path)

            with output_path.open("r", newline="", encoding="utf-8") as handle:
                written_rows = list(csv.reader(handle))

            self.assertEqual(written_rows[0], ["walkable", "quiet place", "Find a place that is walkable, quiet place."])
            self.assertEqual(written_rows[1], ["budget", "pet friendly", "Find a place that is budget, pet friendly."])

    def test_load_criteria_from_excel_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            excel_path = Path(tmpdir) / "criteria.xlsx"
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.append(["Category A", "Category B", "Category C"])
            sheet.append(["Alpha", "Beta", "Gamma"])
            sheet.append(["Delta", "Epsilon", "Zeta"])
            workbook.save(excel_path)

            criteria = randomizer.load_flat_criteria_from_csv(excel_path)

            self.assertIn("Alpha", criteria)
            self.assertIn("Zeta", criteria)
            self.assertIn("Category A", criteria)


if __name__ == "__main__":
    unittest.main()
