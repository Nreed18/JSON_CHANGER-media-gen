import json
import os
from pathlib import Path

import pandas as pd
import requests

CACHE_FILE = Path('media_lookup_cache.json')
MANUAL_REVIEW_FILE = Path('manual_review_queue.json')

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


def process_library(library_path: str) -> None:
    df = load_station_library(library_path)
    cache = load_cache()
    updated = False

    for _, row in df.iterrows():
        key = generate_key(row)
        if key in cache:
            continue

        isrc = str(row.get('ISRC', '')).strip()
        result = None
        if isrc:
            result = lookup_itunes_by_isrc(isrc)

        if not result:
            results = search_itunes(str(row.get('Artist', '')), str(row.get('Title', '')))
            if len(results) == 1:
                result = results[0]
            else:
                # ambiguous results, queue for manual review
                queue_for_manual_review(key, row.to_dict(), results)
                continue

        if result:
            cache[key] = result
            updated = True

    if updated:
        save_cache(cache)


if __name__ == "__main__":
    library_file = os.environ.get('STATION_LIBRARY', 'station_library.xlsx')
    process_library(library_file)
=======
import argparse
import json
from pathlib import Path

import requests
import uvicorn

from web import app

CACHE_FILE = Path("media_lookup_cache.json")
MEDIA_DIR = Path("media")


def download_media(url: str, filename: str | None = None) -> Path:
    MEDIA_DIR.mkdir(exist_ok=True)
    if filename is None:
        filename = url.split("/")[-1]
    dest = MEDIA_DIR / filename
    resp = requests.get(url)
    resp.raise_for_status()
    with open(dest, "wb") as fh:
        fh.write(resp.content)
    return dest


def update_cache(url: str, path: Path) -> None:
    data = {}
    if CACHE_FILE.exists():
        data = json.loads(CACHE_FILE.read_text())
    data[url] = {"path": str(path), "approved": False}
    CACHE_FILE.write_text(json.dumps(data, indent=2))


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    uvicorn.run(app, host=host, port=port)


def main(url: str | None = None, filename: str | None = None) -> None:
    if url:
        path = download_media(url, filename)
        update_cache(url, path)
    run_server()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest media and run approval server")
    parser.add_argument("--url", help="URL of media to download", required=False)
    parser.add_argument("--filename", help="Destination filename", required=False)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if args.url:
        path = download_media(args.url, args.filename)
        update_cache(args.url, path)
    run_server(args.host, args.port)
