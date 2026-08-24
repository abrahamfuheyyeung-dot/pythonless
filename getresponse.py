

#!/usr/bin/env python3

import argparse
import asyncio
import csv
import json
import random
import shutil
import sys
import tempfile
from pathlib import Path
from urllib import request

DEFAULT_MODEL = "llama3.2"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"

# How many requests can run at the same time.
DEFAULT_CONCURRENCY = 20

MAX_RETRIES = 6
INITIAL_RETRY_DELAY = 1.0
MAX_RETRY_DELAY = 60.0


'''
Ollama requires no API key when it is running locally.
Install Ollama, then run: ollama pull llama3.2
python getresponse.py input.csv output.csv


ollama pull llama3.2
ollama serve
cd to folder
python getresponse.py input.csv output.csv

python3 getresponse.py "./restrec/criteria_output.csv" "./restrec/AIresp_o.csv" --concurrency 2

If you just want to reformat the existing csv, use this:
python3 getresponse.py format "./restrec/AIresp_o.csv" "./restrec/AIresp_o.csv"

Longer with additional info like this:
python3 getresponse.py "./restrec/criteria_output.csv" "./restrec/AIresp_o.csv" --concurrency 2 --additional-info "Give me only restaurants that are open and explain why individually they are a good choice. If there isn't a good answer, explain why. Also, give me locations, too."


'''

# ============================================================
# ASK AI
# ============================================================

async def ask_ai(
    ollama_url,
    text,
    model,
    instructions,
    additional_info,
):
    """
    Send one value to the AI and return its complete text answer.
    """

    for attempt in range(MAX_RETRIES):

        try:

            prompt = f"{instructions}\n\n{additional_info}\n\n{text}"
            return await asyncio.to_thread(
                send_to_ollama,
                ollama_url,
                model,
                prompt,
            )

        except Exception as exc:

            if attempt == MAX_RETRIES - 1:
                raise exc

            delay = min(
                INITIAL_RETRY_DELAY * (2 ** attempt),
                MAX_RETRY_DELAY,
            )

            delay += random.uniform(0, 1)

            print(
                f"\nAPI error. Retrying in {delay:.1f}s..."
            )

            await asyncio.sleep(delay)


def send_to_ollama(ollama_url, model, prompt):
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
    }).encode("utf-8")

    request_object = request.Request(
        ollama_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with request.urlopen(request_object, timeout=300) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result.get("response", "").strip()


# ============================================================
# PROCESS ONE ROW
# ============================================================

async def process_row(
    ollama_url,
    semaphore,
    row_number,
    row,
    model,
    instructions,
    additional_info,
):

    # Third column = index 2
    if len(row) < 3:

        return {
            "row_number": row_number,
            "response": "",
            "error": "Row has fewer than 3 columns.",
        }

    text = row[2]

    if not text.strip():

        return {
            "row_number": row_number,
            "response": "",
            "error": "Third column is empty.",
        }

    async with semaphore:

        try:

            response = await ask_ai(
                ollama_url=ollama_url,
                text=text,
                model=model,
                instructions=instructions,
                additional_info=additional_info,
            )

            return {
                "row_number": row_number,
                "response": response,
                "error": "",
            }

        except Exception as exc:

            return {
                "row_number": row_number,
                "response": "",
                "error": f"{type(exc).__name__}: {exc}",
            }


# ============================================================
# READ INPUT CSV
# ============================================================

def load_csv(input_file):

    with input_file.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:

        reader = csv.reader(f)

        return list(reader)


def format_for_google_sheets(text):
    return " ".join(str(text).split())


def format_csv(input_file, output_file):
    rows = load_csv(input_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        delete=False,
        dir=output_file.parent,
        suffix=".tmp",
    ) as temp:
        writer = csv.writer(temp)
        writer.writerows(
            [format_for_google_sheets(cell) for cell in row]
            for row in rows
        )
        temp_path = Path(temp.name)

    shutil.move(str(temp_path), str(output_file))


# ============================================================
# SAVE OUTPUT
# ============================================================

def save_output(
    output_file,
    results,
):

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Write to a temporary file first.
    # This prevents a crash from corrupting the output.
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        delete=False,
        dir=output_file.parent,
        suffix=".tmp",
    ) as temp:

        writer = csv.writer(temp)

        writer.writerow([
            "ai_response"
        ])

        for result in results:

            writer.writerow([
                format_for_google_sheets(result)
            ])

        temp_path = Path(temp.name)

    shutil.move(
        str(temp_path),
        str(output_file),
    )


# ============================================================
# MAIN PROCESSOR
# ============================================================

async def process_csv(
    input_file,
    output_file,
    model,
    concurrency,
    instructions,
    ollama_url,
    additional_info,
):

    print(f"Reading: {input_file}")

    rows = load_csv(input_file)

    if not rows:
        raise ValueError("CSV is empty.")

    # --------------------------------------------------------
    # ASSUMPTION:
    # First row is a header.
    # --------------------------------------------------------

    data_rows = rows[1:]

    total = len(data_rows)

    print(f"Rows found: {total:,}")
    print(f"Using column: 3")
    print(f"Model: {model}")
    print(f"Concurrency: {concurrency}")
    print()

    # --------------------------------------------------------
    # Existing output = resume capability
    # --------------------------------------------------------

    existing_results = []

    if output_file.exists():

        print(
            f"Existing output found: {output_file}"
        )

        try:

            with output_file.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as f:

                reader = csv.reader(f)

                existing_rows = list(reader)

            # Skip header.
            existing_results = [
                format_for_google_sheets(row[0]) if row else ""
                for row in existing_rows[1:]
            ]

            print(
                f"Existing results: "
                f"{len(existing_results):,}"
            )

        except Exception as exc:

            print(
                f"Could not read existing output: {exc}"
            )

            existing_results = []

    # --------------------------------------------------------
    # Make result list exactly the same length as input.
    # --------------------------------------------------------

    results = [""] * total

    for i, value in enumerate(existing_results):

        if i < total:
            results[i] = value

    # --------------------------------------------------------
    # Find rows that still need processing.
    # --------------------------------------------------------

    pending = []

    for i in range(total):

        if results[i] == "":
            pending.append(i)

    completed = total - len(pending)

    print(f"Already completed: {completed:,}")
    print(f"Remaining: {len(pending):,}")
    print()

    # --------------------------------------------------------
    semaphore = asyncio.Semaphore(
        concurrency
    )

    # --------------------------------------------------------
    # Process in batches.
    #
    # We deliberately don't create 10,000 simultaneous
    # requests.
    # --------------------------------------------------------

    batch_size = concurrency * 4

    for batch_start in range(
        0,
        len(pending),
        batch_size,
    ):

        batch = pending[
            batch_start:
            batch_start + batch_size
        ]

        tasks = []

        for index in batch:

            task = asyncio.create_task(
                process_row(
                    ollama_url=ollama_url,
                    semaphore=semaphore,
                    row_number=index,
                    row=data_rows[index],
                    model=model,
                    instructions=instructions,
                    additional_info=additional_info,
                )
            )

            tasks.append(task)

        batch_results = await asyncio.gather(
            *tasks
        )

        # ----------------------------------------------------
        # Put each result back into its original position.
        # ----------------------------------------------------

        for result in batch_results:

            index = result["row_number"]

            if result["error"]:

                # Keep the error visible in the output.
                results[index] = (
                    f"ERROR: {result['error']}"
                )

            else:

                results[index] = (
                    result["response"]
                )

            completed += 1

            print(
                f"\rProcessed: "
                f"{completed:,}/{total:,}",
                end="",
                flush=True,
            )

        # ----------------------------------------------------
        # CHECKPOINT
        #
        # The output file is overwritten with the current
        # results after every batch.
        # ----------------------------------------------------

        save_output(
            output_file,
            results,
        )

    print()
    print()
    print("Finished!")
    print()
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")


# ============================================================
# COMMAND LINE
# ============================================================

def run_format_command():
    parser = argparse.ArgumentParser(
        prog="getresponse.py format",
        description="Format an existing CSV for Google Sheets without using Ollama.",
    )
    parser.add_argument("input_csv", type=Path, help="Existing CSV to format")
    parser.add_argument("output_csv", type=Path, help="New formatted CSV")
    args = parser.parse_args(sys.argv[2:])

    if not args.input_csv.exists():
        raise FileNotFoundError(f"Input CSV does not exist: {args.input_csv}")

    format_csv(args.input_csv, args.output_csv)
    print(f"Formatted CSV written to: {args.output_csv}")

def main():

    if len(sys.argv) > 1 and sys.argv[1].lower() == "format":
        run_format_command()
        return

    parser = argparse.ArgumentParser(
        description=(
            "Send the third column of a CSV to an "
            "Ollama model and create a separate CSV "
            "containing only the AI responses."
        )
    )

    parser.add_argument(
        "input_csv",
        type=Path,
        help="Input CSV",
    )

    parser.add_argument(
        "output_csv",
        type=Path,
        help="New output CSV",
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model to use. Default: {DEFAULT_MODEL}",
    )

    parser.add_argument(
        "--ollama-url",
        default=DEFAULT_OLLAMA_URL,
        help=f"Local Ollama API URL. Default: {DEFAULT_OLLAMA_URL}",
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=(
            "Number of simultaneous requests. "
            f"Default: {DEFAULT_CONCURRENCY}"
        ),
    )

    parser.add_argument(
        "--instructions",
        default=(
            "Process the user's input and provide "
            "the best possible answer. "
            "Return only the answer."
        ),
        help="Instructions given to the AI.",
    )

    parser.add_argument(
        "--additional-info",
        default="",
        help="Extra information to include in every prompt.",
    )

    args = parser.parse_args()

    if not args.input_csv.exists():

        raise FileNotFoundError(
            f"Input CSV does not exist: "
            f"{args.input_csv}"
        )

    if args.concurrency < 1:

        raise ValueError(
            "Concurrency must be at least 1."
        )

    asyncio.run(
        process_csv(
            input_file=args.input_csv,
            output_file=args.output_csv,
            model=args.model,
            concurrency=args.concurrency,
            instructions=args.instructions,
            ollama_url=args.ollama_url,
            additional_info=args.additional_info,
        )
    )


if __name__ == "__main__":
    main()