import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

import pandas as pd
import requests

CACHE_FILE = Path('media_lookup_cache.json')
MANUAL_REVIEW_FILE = Path('manual_review_queue.json')

CACHE_LOCK = threading.Lock()
REVIEW_LOCK = threading.Lock()

ITUNES_LOOKUP_URL = 'https://itunes.apple.com/lookup'
ITUNES_SEARCH_URL = 'https://itunes.apple.com/search'


def load_station_library(file_path: str) -> pd.DataFrame:
    """Load station library from an Excel file."""
    return pd.read_excel(file_path)


def generate_key(record: pd.Series) -> str:
    """Generate a unique key for a track using ISRC if available."""
    isrc = str(record.get('ISRC', '')).strip()
    if isrc:
        return isrc.upper()
    artist = str(record.get('Artist', '')).strip().lower()
    title = str(record.get('Title', '')).strip().lower()
    return f"{artist}:{title}"


def load_cache() -> dict:
    """Load cache from JSON file."""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_cache(cache: dict) -> None:
    """Save cache to JSON file."""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def queue_for_manual_review(key: str, record: dict, results: list) -> None:
    """Add ambiguous record to manual review queue."""
    with REVIEW_LOCK:
        queue = []
        if MANUAL_REVIEW_FILE.exists():
            with open(MANUAL_REVIEW_FILE, 'r', encoding='utf-8') as f:
                queue = json.load(f)
        queue.append({'key': key, 'record': record, 'results': results})
        with open(MANUAL_REVIEW_FILE, 'w', encoding='utf-8') as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)


def lookup_itunes_by_isrc(isrc: str) -> dict | None:
    """Query iTunes API using ISRC."""
    params = {'isrc': isrc}
    try:
        resp = requests.get(ITUNES_LOOKUP_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get('resultCount') == 1:
            return data['results'][0]
    except Exception:
        pass
    return None


def search_itunes(artist: str, title: str) -> list:
    """Search iTunes API using artist and title."""
    term = f"{artist} {title}"
    params = {'term': term, 'media': 'music', 'limit': 5}
    try:
        resp = requests.get(ITUNES_SEARCH_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get('results', [])
    except Exception:
        return []


def process_library(library_path: str, max_workers: int = 10) -> None:
    """Process an Excel library file and cache iTunes metadata."""
    df = load_station_library(library_path)
    cache = load_cache()
    updated = False

    def handle_row(row: pd.Series):
        key = generate_key(row)
        if key in cache:
            return None

        isrc = str(row.get('ISRC', '')).strip()
        result = None
        if isrc:
            result = lookup_itunes_by_isrc(isrc)

        if not result:
            results = search_itunes(str(row.get('Artist', '')), str(row.get('Title', '')))
            if len(results) == 1:
                result = results[0]
            else:
                queue_for_manual_review(key, row.to_dict(), results)
                return None

        if result:
            return key, {"status": "auto", **result}
        return None

    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for _, row in df.iterrows():
            futures.append(executor.submit(handle_row, row))

        for future in as_completed(futures):
            res = future.result()
            if res:
                key, data = res
                cache[key] = data
                updated = True

    if updated:
        with CACHE_LOCK:
            save_cache(cache)


if __name__ == '__main__':
    library_file = os.environ.get('STATION_LIBRARY', 'station_library.xlsx')
    process_library(library_file)
