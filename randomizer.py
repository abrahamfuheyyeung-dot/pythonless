import csv
import os
import random
import re
from pathlib import Path
from typing import List, Sequence, Iterable, Tuple, Union

try:
    import openpyxl  # optional, tests may use .xlsx
except Exception:
    openpyxl = None

# Config
ROW_COUNT = int(os.environ.get("ROW_COUNT", "100"))
OUTPUT_CSV = "criteria_output.csv"


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

    global CRITERIA_HEADERS, CRITERIA_HEADERS_NORM
    CRITERIA_HEADERS = rows[0]
    CRITERIA_HEADERS_NORM = [str(h).strip().lower() if h is not None else "" for h in rows[0]]

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
    # Return columns (list of lists) as the user requested: each inner list is
    # the nth cell from each data row (empty strings preserved).
    return load_columns_from_csv(csv_path)


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
    """Generate rows from either a flat criteria list or a sequence of columns.

    If `columns` is a flat Sequence[str] (no nested lists), this behaves like the
    previous flat-pool sampler used in tests: it samples without replacement
    from the flat pool for each row, refilling when exhausted. If `columns` is
    a Sequence[Sequence[str]] (columns), it randomly selects distinct columns
    per row and samples one value from each column (preserving empty cells).
    """
    if criteria_per_row <= 0:
        raise ValueError("criteria_per_row must be greater than zero")
    if row_count <= 0:
        raise ValueError("row_count must be greater than zero")

    if not columns:
        return []

    # detect flat list: elements are not lists/tuples
    is_flat = all(not isinstance(x, (list, tuple)) for x in columns)
    if is_flat:
        pool = list(columns)
        if len(pool) < criteria_per_row:
            raise ValueError("Not enough criteria to form rows")

        rows: List[List[str]] = []
        for _ in range(row_count):
            if len(pool) < criteria_per_row:
                pool = list(columns)
            selected = random.sample(pool, criteria_per_row)
            rows.append(selected)
            for item in selected:
                pool.remove(item)
        return rows

    # treat as columns
    num_columns = len(columns)
    if num_columns < criteria_per_row:
        raise ValueError("Not enough columns to choose from")

    rows: List[List[str]] = []
    for _ in range(row_count):
        col_indices = random.sample(range(num_columns), criteria_per_row)
        selected: List[str] = []
        for ci in col_indices:
            col = columns[ci]
            if not col:
                selected.append("")
            else:
                selected.append(random.choice(col))
        rows.append(selected)
    return rows


def format_row_as_sentence(row: Sequence[str], introductions: Sequence[str] = (), endings: Sequence[str] = ()) -> str:
    """Format a row as a simple sentence.

    Defaults match the tests: intro `Find a place` and ending `.`.
    """
    criteria = [str(x).strip() for x in row if str(x).strip()]
    if not criteria:
        return "Find a place that fits my preferences."

    intro = random.choice(list(introductions)) if introductions else "Find a place"
    ending = random.choice(list(endings)) if endings else "."

    # Keep simple comma-separated list to match existing tests and expectations
    criteria_text = ", ".join(criteria)
    return f"{intro} that is {criteria_text}{ending}".strip()


def grammar_rewrite_text(text: str) -> str:
    s = text.strip()
    # NOTE: preserve duplicate adjacent words (user requested no deduping)

    s = re.sub(r"\s+([,;:.!?])", r"\1", s)
    s = re.sub(r"([,;:])([^\s])", r"\1 \2", s)
    s = re.sub(r"\s+", " ", s)

    s = re.sub(r"\bthat is (\d+)\s*minutes\b", r"that's within \1 minutes", s, flags=re.I)
    s = re.sub(r"\bin (about |around )?(\d+)\s*minutes\b", r"within \2 minutes", s, flags=re.I)
    s = re.sub(r"\baround\s+(\d+)\s*(bucks|dollars)?\b", r"around $\1", s, flags=re.I)

    # collapse numeric+unit lists (people)
    try:
        matches = list(re.finditer(r"(\d+)\s+(people|person|persons|guests)\b", s, flags=re.I))
        if len(matches) >= 2:
            units = [m.group(2).lower() for m in matches]
            if all(u == units[0] for u in units):
                first = matches[0].start()
                last = matches[-1].end()
                values = [m.group(1) for m in matches]
                if len(values) == 2:
                    joined = f"{values[0]} and {values[1]}"
                else:
                    joined = ", ".join(values[:-1]) + f", and {values[-1]}"
                replacement = f"groups of {joined} {units[0]}"
                s = s[:first] + replacement + s[last:]
    except Exception:
        pass

    return s


def ai_rewrite_sentences(sentences: List[str]) -> List[str]:
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

    url = "https://api-inference.huggingface.co/models/google/flan-t5-small"
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
            (
                "Rewrite the following sentence into clear, natural English while preserving "
                "the criteria exactly (do not add or remove information). Sentence:\n\n" + s
            )
            for s in batch
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


def write_output(rows: Iterable[Sequence[str]], phrase_pairs: Sequence[Tuple[str, str]], output_path: str | Path = OUTPUT_CSV) -> None:
    path = Path(output_path)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        introductions = [a for a, b in phrase_pairs if a] if phrase_pairs else []
        endings = [b for a, b in phrase_pairs if b] if phrase_pairs else []
        rows_list = list(rows)
        sentences = [format_row_as_sentence(row, introductions, endings) for row in rows_list]
        # Run optional AI rewrite step (external service) if enabled via env
        sentences = ai_rewrite_sentences(sentences)
        for row, sentence in zip(rows_list, sentences):
            writer.writerow([*row, sentence])


def write_rows(rows: Iterable[Sequence[str]], output_path: str | Path, introductions: Sequence[str] = (), endings: Sequence[str] = ()) -> None:
    """Compatibility helper used by tests: write rows and append a sentence column."""
    path = Path(output_path)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        for row in rows:
            sentence = format_row_as_sentence(row, introductions, endings)
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
    criteria_csv = base / "criteria.csv"
    phrases_csv = base / "phrases.csv"

    cols = load_columns_from_csv(criteria_csv)
    phrase_pairs = load_phrase_pairs(phrases_csv)

    rows = generate_rows(cols, row_count=ROW_COUNT, criteria_per_row=2)
    write_output(rows, phrase_pairs, OUTPUT_CSV)

    dup_count, counts = count_first_two_columns_unordered(rows)
    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")
    print(f"Unordered first-two-columns duplicate count: {dup_count}")


if __name__ == "__main__":
    main()
