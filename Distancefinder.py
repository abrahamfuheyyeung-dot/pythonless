"""Annotate locations in an input CSV with their straight-line (haversine) distance
from an epicenter, writing the result to an output CSV with the same shape.

Each cell can hold one or more comma-separated locations (coordinates like
"40.7128, -74.0060" or addresses like "631 Kearny St, San Francisco, CA 94108").
Every location found in a cell is returned as
"<location> -> <matched place> (<lat>, <lon>) - <distance><unit>",
e.g. "1234 Elm St, X, CA 90001 -> 1234, Elm Street, X, California, USA (34.0001, -118.0001) - 12.30mi".
Locations are geocoded with OpenStreetMap Nominatim.

Usage:
    python Distancefinder.py --input input.csv --output out.csv --epicenter "40.0,-75.0"
    python Distancefinder.py --input input.csv --output out.csv --epicenter "Washington, DC" --unit mi
"""

import argparse
import csv
import logging
import math
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Tuple

import requests

from distance_calculator import parse_coordinates

logger = logging.getLogger("geocoder")

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
matched_names: Dict[str, str] = {}
EARTH_RADIUS_KM = 6371.0088

ADDRESS_PATTERN = re.compile(
    r"\b\d{1,6}\s+[A-Za-z0-9&.'-]+(?:\s+[A-Za-z0-9&.'-]+){0,5},\s*"
    r"[A-Za-z .'-]+,\s*(?:[A-Z]{2}(?:\s+\d{5}(?:-\d{4})?)?|USA|United States)\b"
)
LABELED_COORDINATE_PATTERN = re.compile(
    r"Latitude:\s*(?P<lat>\d+(?:\.\d+)?)\s*°?\s*(?P<lat_dir>[NS])\s+"
    r"Longitude:\s*(?P<lon>\d+(?:\.\d+)?)\s*°?\s*(?P<lon_dir>[EW])",
    re.IGNORECASE,
)


class LocationMatch(NamedTuple):
    start: int
    end: int
    text: str
    point: Optional[Tuple[float, float]]
    error: Optional[str]


def resolve_epicenter(text: str) -> Optional[Tuple[float, float]]:
    """Resolve the --epicenter argument as coordinates or, failing that, an address."""
    coords = parse_coordinates(text)
    if coords is not None:
        return coords
    return geocode_with_error(text)[0]


def geocode_with_error(text: str) -> Tuple[Optional[Tuple[float, float]], Optional[str]]:
    """Geocode with Nominatim, recording the matched place name in matched_names."""
    try:
        response = requests.get(
            NOMINATIM_URL,
            params={"q": text, "format": "json", "limit": 1},
            headers={"User-Agent": "distance-calculator/1.0"},
            timeout=10,
        )
        response.raise_for_status()
        results = response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        return None, f"Error geocoding '{text}': {e}"
    finally:
        time.sleep(1)  # Nominatim usage policy: max 1 request/second
    if not results:
        return None, f"Error: Could not find location '{text}'"
    name = results[0].get("display_name", "")
    matched_names[text.lower()] = name
    logger.info("Nominatim: %r -> %r", text, name)
    return (float(results[0]["lat"]), float(results[0]["lon"])), None


def describe(text: str, point: Tuple[float, float]) -> str:
    """Format a location with the place it resolved to and its coordinates."""
    name = matched_names.get(text.lower())
    coords = f"({point[0]:.5f}, {point[1]:.5f})"
    return f"{text} -> {name} {coords}" if name else f"{text} {coords}"


def resolve_location(
    text: str,
    geocode_cache: Dict[str, Optional[Tuple[float, float]]],
    error_cache: Dict[str, str],
) -> Optional[Tuple[float, float]]:
    """Resolve a single location string to (lat, lon), geocoding (and caching) if needed."""
    coords = parse_coordinates(text)
    if coords is not None:
        return coords
    key = text.lower()
    if key not in geocode_cache:
        geocode_cache[key], error = geocode_with_error(text)
        if error:
            error_cache[key] = error
    return geocode_cache[key]


def haversine_km(point_a: Tuple[float, float], point_b: Tuple[float, float]) -> float:
    """Straight-line great-circle distance between two (lat, lon) points, in km."""
    lat1, lon1 = map(math.radians, point_a)
    lat2, lon2 = map(math.radians, point_b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))


def convert(distance_km: float, unit: str) -> float:
    return distance_km * 0.621371 if unit == "mi" else distance_km


def find_embedded_locations(
    text: str,
    geocode_cache: Dict[str, Optional[Tuple[float, float]]],
    error_cache: Dict[str, str],
) -> List[LocationMatch]:
    """Find complete street addresses and labeled coordinates inside prose."""
    matches: List[LocationMatch] = []

    for match in ADDRESS_PATTERN.finditer(text):
        location = match.group(0)
        point = resolve_location(location, geocode_cache, error_cache)
        error = error_cache.get(location.lower()) if point is None else None
        matches.append(LocationMatch(match.start(), match.end(), location, point, error))

    for match in LABELED_COORDINATE_PATTERN.finditer(text):
        lat = float(match.group("lat"))
        lon = float(match.group("lon"))
        if match.group("lat_dir").upper() == "S":
            lat = -lat
        if match.group("lon_dir").upper() == "W":
            lon = -lon
        if not any(match.start() < item.end and match.end() > item.start for item in matches):
            matches.append(LocationMatch(match.start(), match.end(), match.group(0), (lat, lon), None))

    return sorted(matches, key=lambda item: item.start)


def annotate_cell(
    cell: str,
    epicenter: Tuple[float, float],
    unit: str,
    geocode_cache: Dict[str, Optional[Tuple[float, float]]],
    error_cache: Dict[str, str],
) -> str:
    """Return only the extracted locations and their distances or errors."""
    matches = find_embedded_locations(cell, geocode_cache, error_cache)
    if not matches:
        if len(cell.strip()) > 120:
            return "Error: No locations found"
        location = cell.strip()
        point = resolve_location(location, geocode_cache, error_cache)
        if point is None:
            return error_cache.get(location.lower(), f"Error: Could not find location '{location}'")
        distance = convert(haversine_km(epicenter, point), unit)
        return f"{describe(location, point)} - {distance:.2f}{unit}"

    results = []
    for match in matches:
        if match.point is None:
            replacement = match.error or f"Error: Could not find location '{match.text}'"
        else:
            distance = convert(haversine_km(epicenter, match.point), unit)
            display_text = describe(match.text.replace("°", ""), match.point)
            replacement = f"{display_text} - {distance:.2f}{unit}"
        results.append(replacement)
    return " | ".join(results)


def process_csv(input_path: Path, epicenter: Tuple[float, float], unit: str) -> List[List[str]]:
    """Read a CSV and annotate every location in every cell, keeping the same shape."""
    geocode_cache: Dict[str, Optional[Tuple[float, float]]] = {}
    error_cache: Dict[str, str] = {}
    with input_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    return [[annotate_cell(cell, epicenter, unit, geocode_cache, error_cache) for cell in row] for row in rows]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Annotate locations in a CSV with their distance from an epicenter."
    )
    parser.add_argument("--input", required=True, help="Path to the input CSV file.")
    parser.add_argument("--output", required=True, help="Path to write the output CSV file.")
    parser.add_argument("--epicenter", required=True, help="Epicenter location, as 'lat,lon' or an address.")
    parser.add_argument("--unit", choices=["km", "mi"], default="km", help="Distance unit (default: km).")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    epicenter = parse_coordinates(args.epicenter)
    epicenter_error = None
    if epicenter is None:
        epicenter, epicenter_error = geocode_with_error(args.epicenter)
    if epicenter is None:
        with Path(args.output).open("w", newline="", encoding="utf-8") as handle:
            csv.writer(handle).writerow([epicenter_error or "Error: could not resolve epicenter"])
        print(f"Wrote epicenter error to {args.output}")
        return

    out_rows = process_csv(Path(args.input), epicenter, args.unit)
    with Path(args.output).open("w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(out_rows)
    print(f"Wrote {len(out_rows)} rows to {args.output}")


if __name__ == "__main__":
    main()

