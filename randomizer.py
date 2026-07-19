import csv
import random
from pathlib import Path
from typing import Iterable, List, Sequence


def load_criteria_from_csv(csv_path: str | Path) -> List[str]:
    path = Path(csv_path)
    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))

    if not rows:
        return []

    criteria: List[str] = []
    for row in rows:
        for item in row:
            if isinstance(item, str):
                value = item.strip()
            else:
                value = str(item).strip()
            if value:
                criteria.append(value)

    return criteria


def generate_rows(criteria: Sequence[str], row_count: int, criteria_per_row: int = 2) -> List[List[str]]:
    if criteria_per_row <= 0:
        raise ValueError("criteria_per_row must be greater than zero")
    if row_count <= 0:
        raise ValueError("row_count must be greater than zero")

    if len(criteria) < criteria_per_row:
        raise ValueError("Not enough criteria to form rows")

    rows: List[List[str]] = []
    pool = list(criteria)
    for _ in range(row_count):
        if len(pool) < criteria_per_row:
            pool = list(criteria)

        selected = random.sample(pool, criteria_per_row)
        rows.append(selected)
        for item in selected:
            pool.remove(item)

    return rows


def write_rows(rows: Iterable[Sequence[str]], output_path: str | Path) -> None:
    path = Path(output_path)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        for row in rows:
            writer.writerow(row)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    input_csv = base_dir / "criteria.csv"
    output_csv = base_dir / "criteria_output.csv"

    if not input_csv.exists():
        raise FileNotFoundError(
            f"Input CSV not found: {input_csv}. Put your CSV file there or change the path in the code."
        )

    criteria = load_criteria_from_csv(input_csv)
    rows = generate_rows(criteria, row_count=10000, criteria_per_row=2)
    write_rows(rows, output_csv)
    print(f"Wrote {len(rows)} rows to {output_csv}")


if __name__ == "__main__":
    main()
