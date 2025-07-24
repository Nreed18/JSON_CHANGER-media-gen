import json
from pathlib import Path

import requests
import uvicorn

from web import app

CACHE_FILE = Path("media_lookup_cache.json")
MEDIA_DIR = Path("media")


def download_media(url: str, filename: str | None = None) -> Path:
    """Download a file into the media directory."""
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
    """Record downloaded media in the cache."""
    data = {}
    if CACHE_FILE.exists():
        data = json.loads(CACHE_FILE.read_text())
    data[url] = {"path": str(path), "approved": False}
    CACHE_FILE.write_text(json.dumps(data, indent=2))


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Launch the FastAPI review server."""
    uvicorn.run(app, host=host, port=port)
