#!/usr/bin/env python3
"""
csv_to_ai.py

Read rows from a CSV, send each row (or a column) to a local Ollama model,
and write responses to a new CSV column.

Install dependencies:
    pip install pandas tqdm

Ollama requires no API key when it is running locally. First download a model:
    ollama pull llama3.2

Usage example:
    python csv_to_ai.py --input my_prompts.csv --prompt-column prompt --output responses.csv --model llama3.2
"""
from __future__ import annotations

import argparse
import json
import time
from urllib import request

import pandas as pd
from tqdm import tqdm


def get_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Batch prompts from CSV to a local Ollama model")
    p.add_argument("--input", "-i", required=True, help="Input CSV file path")
    p.add_argument("--output", "-o", required=True, help="Output CSV file path")
    p.add_argument(
        "--prompt-column",
        "-c",
        default="prompt",
        help="Name of the column containing the prompts (default: 'prompt')",
    )
    p.add_argument(
        "--response-column",
        "-r",
        default="ai_response",
        help="Name of the column to write AI responses into",
    )
    p.add_argument(
        "--template",
        "-t",
        default="{text}",
        help="Optional template for prompts; use '{text}' where the column value should be inserted",
    )
    p.add_argument("--model", default="llama3.2", help="Ollama model to use (default: llama3.2)")
    p.add_argument("--ollama-url", default="http://localhost:11434/api/generate", help="Local Ollama API URL")
    p.add_argument("--sleep", type=float, default=0.0, help="Seconds to sleep between calls (default: 0)")
    p.add_argument("--max-retries", type=int, default=5, help="Max retries on error")
    return p.parse_args()


def send_to_ollama(ollama_url: str, model: str, prompt: str) -> str:
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    }).encode("utf-8")
    req = request.Request(
        ollama_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=300) as response:
        result = json.loads(response.read().decode("utf-8"))
    return result.get("response", "").strip()


def call_ollama(model: str, prompt: str, ollama_url: str, max_retries: int = 5) -> str:
    backoff = 1.0
    for attempt in range(1, max_retries + 1):
        try:
            return send_to_ollama(ollama_url, model, prompt)
        except Exception as e:  # intentionally broad: retry network/api errors
            if attempt == max_retries:
                raise
            time.sleep(backoff)
            backoff *= 2


def main() -> None:
    args = get_args()

    df = pd.read_csv(args.input)
    if args.prompt_column not in df.columns:
        raise ValueError(f"Prompt column '{args.prompt_column}' not found in input CSV")

    # Ensure response column exists
    if args.response_column not in df.columns:
        df[args.response_column] = ""

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
        # Skip existing responses unless empty
        existing = str(row.get(args.response_column, ""))
        if existing.strip():
            continue

        text = "" if pd.isna(row[args.prompt_column]) else str(row[args.prompt_column])
        prompt = args.template.replace("{text}", text)

        try:
            response = call_ollama(
                args.model,
                prompt,
                args.ollama_url,
                max_retries=args.max_retries,
            )
        except Exception as e:
            response = f"__ERROR__ {type(e).__name__}: {e}"

        df.at[idx, args.response_column] = response
        if args.sleep and args.sleep > 0:
            time.sleep(args.sleep)

    df.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
