import csv
import random
import os
from pathlib import Path
from typing import Iterable, List, Sequence


def load_criteria_from_csv(csv_path: str | Path) -> List[str]:
    path = Path(csv_path)
    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    # Skip header row if present
    data_rows = rows[1:] if len(rows) > 1 else []
    if not rows:
        return []

    criteria: List[str] = []
    for row in data_rows:
        for item in row:
            if isinstance(item, str):
                value = item.strip()
            else:
                value = str(item).strip()
            if value:
                criteria.append(value)

    return criteria


def load_phrase_lists(csv_path: str | Path) -> tuple[List[str], List[str]]:
    path = Path(csv_path)
    if not path.exists():
        return [], []

    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    # Skip header row if present
    data_rows = rows[1:] if len(rows) > 1 else []

    introductions: List[str] = []
    endings: List[str] = []
    for row in data_rows:
        if not row:
            continue
        if len(row) >= 2:
            intro = row[0].strip()
            ending = row[1].strip()
        else:
            intro = row[0].strip()
            ending = ""

        if intro:
            introductions.append(intro)
        if ending:
            endings.append(ending)

    return introductions, endings


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


def format_row_as_sentence(row: Sequence[str], introductions: Sequence[str], endings: Sequence[str]) -> str:
    criteria = [str(item).strip() for item in row if str(item).strip()]
    if not criteria:
        return "I'm looking for a restaurant that fits my preferences."

    if introductions:
        intro = random.choice(list(introductions))
    else:
        intro = "I'm looking for a restaurant"

    if endings:
        ending = random.choice(list(endings))
    else:
        ending = "for me."

    if len(criteria) == 1:
        return f"{intro} that is {criteria[0]} {ending}".strip()

    criteria_text = ", ".join(criteria[:-1]) + f" and {criteria[-1]}"
    return f"{intro} that is {criteria_text} {ending}".strip()


def write_rows(rows: Iterable[Sequence[str]], output_path: str | Path, introductions: Sequence[str] = (), endings: Sequence[str] = ()) -> None:
    path = Path(output_path)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        for row in rows:
            sentence = format_row_as_sentence(row, introductions, endings)
            writer.writerow([*row, sentence])


def count_first_two_columns_unordered(rows: Iterable[Sequence[str]]) -> tuple[int, dict[tuple[str, str], int]]:
    counts: dict[tuple[str, str], int] = {}
    duplicates = 0
    for row in rows:
        a = str(row[0]).strip() if len(row) > 0 else ""
        b = str(row[1]).strip() if len(row) > 1 else ""

        if not a and not b:
            continue

        key = tuple(sorted((a, b)))
        counts[key] = counts.get(key, 0) + 1
        if counts[key] > 1:
            duplicates += 1

    return duplicates, counts


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    input_csv = base_dir / "criteria.csv"
    output_csv = base_dir / "criteria_output.csv"

    if not input_csv.exists():
        raise FileNotFoundError(
            f"Input CSV not found: {input_csv}. Put your CSV file there or change the path in the code."
        )

    criteria = load_criteria_from_csv(input_csv)
    phrase_csv = base_dir / "phrases.csv"
    introductions, endings = load_phrase_lists(phrase_csv)
    row_count = int(os.environ.get("ROW_COUNT", "100"))
    rows = generate_rows(criteria, row_count=row_count, criteria_per_row=2)
    write_rows(rows, output_csv, introductions, endings)

    # Count unordered duplicates in the first two columns (criteria)
    unordered_duplicates, pair_counts = count_first_two_columns_unordered(rows)

    print(f"Wrote {len(rows)} rows to {output_csv}")
    print(f"Unordered first-two-columns duplicate count: {unordered_duplicates}", flush=True)


if __name__ == "__main__":
    main()
