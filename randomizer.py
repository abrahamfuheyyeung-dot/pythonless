import argparse
import csv
import itertools
import os
import random
from pathlib import Path
from typing import List, Optional, Sequence, Iterable, Tuple, Union

try:
    import openpyxl  # optional, tests may use .xlsx
except Exception:
    openpyxl = None

# Config
DEFAULT_ROW_COUNT = 1000
OUTPUT_CSV = "criteria_output.csv"

CRITERIA_HEADERS: List[str] = []
CRITERIA_HEADERS_NORM: List[str] = []


def _set_criteria_headers(headers: List[str]) -> None:
    global CRITERIA_HEADERS, CRITERIA_HEADERS_NORM
    CRITERIA_HEADERS = headers
    CRITERIA_HEADERS_NORM = [str(h).strip().lower() if h is not None else "" for h in headers]


def get_row_count() -> int:
    value = os.environ.get("ROW_COUNT")
    if value is None:
        return DEFAULT_ROW_COUNT
    try:
        return int(value)
    except ValueError:
        return DEFAULT_ROW_COUNT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate random criteria rows into a CSV file.")
    parser.add_argument(
        "--rows",
        "-r",
        type=int,
        help="Number of rows to generate. Overrides ROW_COUNT environment variable.",
    )
    return parser.parse_args()


def load_columns_from_csv(csv_path: str | Path) -> List[List[str]]:
    """Load a CSV or XLSX and return columns as lists of nth-cells.

    The header row is preserved in globals `CRITERIA_HEADERS` and
    `CRITERIA_HEADERS_NORM`. Empty cells are preserved as empty strings.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Criteria CSV not found: {path}")

    rows: List[List[str]] = []
    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xls") and openpyxl is not None:
        wb = openpyxl.load_workbook(path, read_only=True)
        ws = wb.active
        for r in ws.iter_rows(values_only=True):
            rows.append(["" if v is None else str(v) for v in r])
    else:
        with path.open("r", newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))

    if not rows:
        return []

    _set_criteria_headers(rows[0])

    data_rows = rows[1:]
    if not data_rows:
        return []

    max_columns = max((len(r) for r in data_rows), default=0)
    columns: List[List[str]] = []
    for ci in range(max_columns):
        col: List[str] = []
        for r in data_rows:
            item = r[ci] if ci < len(r) else ""
            col.append(item)
        columns.append(col)

    return columns


def load_criteria_from_csv(csv_path: str | Path) -> List[str]:
    """Compatibility wrapper that returns a flat list of criteria values.

    This is for tests and other modules that expect a flat list (including
    header names). It flattens `load_columns_from_csv` results.
    """
    columns = load_columns_from_csv(csv_path)
    return [item for column in columns for item in column]


def load_flat_criteria_from_csv(csv_path: str | Path) -> List[str]:
    """Backward-compatible alias for loading a flat criteria list."""
    return load_criteria_from_csv(csv_path)


def load_phrase_pairs(csv_path: str | Path) -> List[Tuple[str, str]]:
    path = Path(csv_path)
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    pairs: List[Tuple[str, str]] = []
    for r in rows[1:] if len(rows) > 1 else []:
        if not r:
            continue
        a = r[0].strip() if len(r) > 0 and r[0] else ""
        b = r[1].strip() if len(r) > 1 and r[1] else ""
        if a or b:
            pairs.append((a, b))
    return pairs


def generate_rows(columns: Sequence[Sequence[str]], row_count: int, criteria_per_row: int = 2) -> List[List[str]]:
    """Generate rows by sampling independently from distinct columns.

    Each element of `columns` must itself be a sequence of criteria values for a
    distinct column. For each row, this function selects `criteria_per_row`
    different columns and then picks one value from each selected column.
    """
    if criteria_per_row <= 0:
        raise ValueError("criteria_per_row must be greater than zero")
    if row_count <= 0:
        raise ValueError("row_count must be greater than zero")

    if not columns:
        return []

    if not all(isinstance(column, (list, tuple)) for column in columns):
        raise TypeError("generate_rows expects a sequence of columns, where each column is a list or tuple")

    pools: List[List[str]] = [
        [str(item).strip() for item in column if str(item).strip()]
        for column in columns
    ]

    if len(pools) < criteria_per_row:
        raise ValueError("Not enough columns to choose from")

    if sum(bool(col) for col in pools) < criteria_per_row:
        raise ValueError("Not enough non-empty columns to choose from")

    rows: List[List[str]] = []
    for _ in range(row_count):
        available_columns = [idx for idx, col in enumerate(pools) if col]
        if len(available_columns) < criteria_per_row:
            raise ValueError("Not enough non-empty columns to choose from")

        selected_columns = random.sample(available_columns, criteria_per_row)
        rows.append([random.choice(pools[ci]) for ci in selected_columns])

    return rows


def format_row_as_sentence(row: Sequence[str], phrase_pairs) -> str:
    """Format a row as a simple sentence.

    Defaults match the tests: intro `Find a place` and ending `.`.
    """
    criteria = [str(x).strip() for x in row if str(x).strip()]
    if not criteria:
        return "Find a place that fits my preferences."
    phrase_pair = random.choice(phrase_pairs) if phrase_pairs else ("Find a place", ".")
    intro, ending = phrase_pair
    # intro = random.choice(list(introductions)) if introductions else "Find a place"
    # ending = random.choice(list(endings)) if endings else "."

    if len(criteria) == 1:
        criteria_text = criteria[0]
    elif len(criteria) == 2:
        criteria_text = " and ".join(criteria)
    else:
        criteria_text = ", ".join(criteria[:-1]) + ", and " + criteria[-1]

    return f"{intro} {criteria_text}{ending}".strip()

'''
def _build_ai_rewrite_prompt(sentence: str, row: Optional[Sequence[str]] = None, phrase_pairs: Sequence[Tuple[str, str]] = ()) -> str:
    intro_phrases = [a for a, b in phrase_pairs if a]
    ending_phrases = [b for a, b in phrase_pairs if b]
    prompt = (
        "Rewrite the following sentence into clear, natural English while preserving the "
        "criteria and retaining the original intent from the preferred phrase templates. "
        "Fix grammar, punctuation, and any repeated words. Do not add or remove any facts.\n\n"
    )
    if row:
        criteria_values = [str(x).strip() for x in row if str(x).strip()]
        if criteria_values:
            prompt += "Criteria values: " + ", ".join(criteria_values) + ".\n"
    if intro_phrases:
        prompt += "Possible introduction phrases: " + "; ".join(intro_phrases) + ".\n"
    if ending_phrases:
        prompt += "Possible ending phrases: " + "; ".join(ending_phrases) + ".\n"
    prompt += f"\nSentence:\n\n{sentence}"
    return prompt


def ai_rewrite_sentences(
    sentences: List[str],
    rows: Optional[Sequence[Sequence[str]]] = None,
    phrase_pairs: Sequence[Tuple[str, str]] = (),
) -> List[str]:
    """Rewrite sentences using an external AI service when enabled.

    Controlled by `USE_AI_REWRITE` (truthy) and `HF_API_TOKEN` environment
    variables. Falls back to returning the original sentences on failure.
    """
    use_ai = os.environ.get("USE_AI_REWRITE", "0").lower() in ("1", "true", "yes")
    token = os.environ.get("HF_API_TOKEN")
    if not use_ai or not token:
        return sentences

    try:
        import requests
    except Exception as e:
        print(f"AI rewrite unavailable: requests import failed: {e}")
        return sentences

    url = "https://api-inference.huggingface.co/models/google/flan-t5-xl"
    headers = {"Authorization": f"Bearer {token}"}
    rewritten: List[str] = []

    # Batch size configurable via env; default 32
    try:
        chunk_size = int(os.environ.get("AI_BATCH_SIZE", "32"))
    except Exception:
        chunk_size = 32

    for i in range(0, len(sentences), chunk_size):
        batch = sentences[i : i + chunk_size]
        prompts = [
            _build_ai_rewrite_prompt(
                s,
                row=rows[i + idx] if rows is not None else None,
                phrase_pairs=phrase_pairs,
            )
            for idx, s in enumerate(batch)
        ]
        try:
            resp = requests.post(url, headers=headers, json={"inputs": prompts}, timeout=60)
        except Exception as e:
            print(f"AI rewrite exception when calling API: {e}")
            return sentences

        if resp.status_code != 200:
            body = resp.text[:1000]
            print(f"AI rewrite failed: status={resp.status_code} body={body}")
            return sentences

        try:
            data = resp.json()
        except Exception as e:
            print(f"AI rewrite failed to decode JSON response: {e}")
            return sentences

        # Expect data to be a list matching prompts
        if isinstance(data, list) and len(data) == len(prompts):
            for item in data:
                if isinstance(item, dict) and "generated_text" in item:
                    rewritten.append(item["generated_text"].strip())
                elif isinstance(item, str):
                    rewritten.append(item.strip())
                else:
                    rewritten.append(str(item).strip())
        else:
            # Unexpected shape
            print(f"AI rewrite unexpected response shape: {type(data)}; content truncated: {str(data)[:1000]}")
            return sentences

    return rewritten

'''
def ai_rewrite_sentences(
    sentences: List[str],
    rows: Optional[Sequence[Sequence[str]]] = None,
    phrase_pairs: Sequence[Tuple[str, str]] = (),
) -> List[str]:
    """AI rewrite stub disabled for current operation."""
    # AI rewrite is currently disabled. Return original sentences unchanged.
    return sentences


def write_output(rows: Iterable[Sequence[str]], phrase_pairs: Sequence[Tuple[str, str]], output_path: str | Path = OUTPUT_CSV) -> None:
    path = Path(output_path)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        rows_list = list(rows)
        sentences = [format_row_as_sentence(row, phrase_pairs) for row in rows_list]
        # AI rewrite disabled for now; keep the original formatted sentences.
        # sentences = ai_rewrite_sentences(sentences, rows=rows_list, phrase_pairs=phrase_pairs)
        for row, sentence in zip(rows_list, sentences):
            writer.writerow([*row, sentence])


def write_rows(rows: Iterable[Sequence[str]], output_path: str | Path, introductions: Sequence[str] = (), endings: Sequence[str] = ()) -> None:
    """Compatibility helper used by tests: write rows and append a sentence column."""
    path = Path(output_path)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        phrase_pairs = tuple(zip(introductions, endings)) if introductions or endings else ()
        for row in rows:
            sentence = format_row_as_sentence(row, phrase_pairs)
            writer.writerow([*row, sentence])


def count_first_two_columns_unordered(rows: Iterable[Sequence[str]]) -> Tuple[int, dict]:
    counts = {}
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
    base = Path(__file__).resolve().parent
    criteria_csv = base / "restrec" / "criteria.csv"
    phrases_csv = base / "restrec" / "phrases.csv"

    args = parse_args()
    cols = load_columns_from_csv(criteria_csv)
    phrase_pairs = load_phrase_pairs(phrases_csv)

    row_count = args.rows if args.rows is not None else get_row_count()
    rows = generate_rows(cols, row_count=row_count, criteria_per_row=2)
    write_output(rows, phrase_pairs, OUTPUT_CSV)

    dup_count, counts = count_first_two_columns_unordered(rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")
    print(f"Unordered first-two-columns duplicate count: {dup_count}")


if __name__ == "__main__":
    main()
