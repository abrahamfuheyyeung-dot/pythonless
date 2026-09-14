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

            columns = randomizer.load_columns_from_csv(csv_path)
            rows = randomizer.generate_rows(columns, row_count=4, criteria_per_row=2)

            self.assertEqual(len(rows), 4)
            for row in rows:
                self.assertEqual(len(row), 2)
                self.assertTrue(all(item in ["Alpha", "Delta"] + ["Beta", "Epsilon"] + ["Gamma", "Zeta"] for item in row))
                self.assertNotEqual(row[0], row[1])

    def test_generate_rows_samples_from_distinct_columns(self):
        columns = [["Alpha", "Delta"], ["Beta", "Epsilon"], ["Gamma", "Zeta"]]
        rows = randomizer.generate_rows(columns, row_count=100, criteria_per_row=2)

        self.assertEqual(len(rows), 100)
        for row in rows:
            self.assertEqual(len(row), 2)
            # All values in the same row should come from different columns
            self.assertFalse(
                any(row[0] in columns[i] and row[1] in columns[i] for i in range(len(columns)))
            )

    def test_generate_rows_all_rows_use_distinct_columns(self):
        columns = [["A1", "A2"], ["B1", "B2"], ["C1", "C2"]]
        rows = randomizer.generate_rows(columns, row_count=10, criteria_per_row=2)

        self.assertEqual(len(rows), 10)
        for row in rows:
            self.assertEqual(len(row), 2)
            self.assertFalse(
                any(row[0] in columns[i] and row[1] in columns[i] for i in range(len(columns)))
            )

    def test_generate_rows_refills_exhausted_columns(self):
        columns = [["A1", "A2"], ["B1", "B2"]]
        rows = randomizer.generate_rows(columns, row_count=10, criteria_per_row=2)

        self.assertEqual(len(rows), 10)
        for row in rows:
            self.assertEqual(len(row), 2)
            self.assertFalse(
                any(row[0] in columns[i] and row[1] in columns[i] for i in range(len(columns)))
            )

    def test_write_rows_preserves_two_criteria_and_adds_sentence_column(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "criteria_output.csv"
            rows = [["walkable", "quiet place"], ["budget", "pet friendly"]]

            randomizer.write_rows(rows, output_path)

            with output_path.open("r", newline="", encoding="utf-8") as handle:
                written_rows = list(csv.reader(handle))

            self.assertEqual(written_rows[0], ["walkable", "quiet place", "Find a place walkable and quiet place."])
            self.assertEqual(written_rows[1], ["budget", "pet friendly", "Find a place budget and pet friendly."])

    def test_load_criteria_from_excel_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            excel_path = Path(tmpdir) / "criteria.xlsx"
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.append(["Category A", "Category B", "Category C"])
            sheet.append(["Alpha", "Beta", "Gamma"])
            sheet.append(["Delta", "Epsilon", "Zeta"])
            workbook.save(excel_path)
            workbook.close()

            criteria = randomizer.load_flat_criteria_from_csv(excel_path)

            self.assertIn("Alpha", criteria)
            self.assertIn("Zeta", criteria)
            self.assertNotIn("Category A", criteria)


if __name__ == "__main__":
    unittest.main()
