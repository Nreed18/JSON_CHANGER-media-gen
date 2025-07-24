import argparse
import json
import os
import sys
from urllib.parse import urlparse

import re
from urllib.request import urlopen


def sanitize(name: str) -> str:
    """Sanitize a string for safe filesystem usage."""
    return ''.join(c for c in name if c.isalnum() or c in ' -_').strip()


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def download_file(url: str, dest_path: str) -> None:
    with urlopen(url) as response, open(dest_path, 'wb') as f:
        f.write(response.read())


def artwork_600(url100: str) -> str:
    """Convert a 100x100 artwork URL to 600x600."""
    return re.sub(r"100x100bb", "600x600bb", url100)


def handle_result(result: dict, base_dir: str) -> None:
    artist = sanitize(result.get('artistName', 'Unknown Artist'))
    album = sanitize(result.get('collectionName', 'Unknown Album'))
    artwork = result.get('artworkUrl100')
    preview = result.get('previewUrl')

    target_dir = os.path.join(base_dir, artist, album)
    ensure_dir(target_dir)

    approve = input(f"Download media for {artist} - {album}? [y/N]: ")
    if approve.lower() != 'y':
        return

    if artwork:
        artwork_path = os.path.join(target_dir, 'artwork.jpg')
        if not os.path.exists(artwork_path):
            art_url = artwork_600(artwork)
            try:
                download_file(art_url, artwork_path)
            except Exception as e:
                print(f"Failed to download artwork: {e}", file=sys.stderr)

    if preview:
        filename = os.path.basename(urlparse(preview).path) or 'preview.mp3'
        preview_path = os.path.join(target_dir, filename)
        if not os.path.exists(preview_path):
            try:
                download_file(preview, preview_path)
            except Exception as e:
                print(f"Failed to download preview: {e}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download iTunes media previews")
    parser.add_argument('json', help='Path to iTunes search results JSON')
    parser.add_argument('--dest', default='media/music', help='Destination directory')
    args = parser.parse_args()

    with open(args.json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = data.get('results', [])
    for result in results:
        handle_result(result, args.dest)


if __name__ == '__main__':
    main()
