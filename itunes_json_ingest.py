import argparse
import json
import os
import re
import sys
from urllib.parse import urlparse
from urllib.request import urlopen


def sanitize(name: str) -> str:
    """Sanitize a string for safe filesystem usage."""
    return ''.join(c for c in name if c.isalnum() or c in ' -_').strip()


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def download_file(url: str, dest_path: str) -> None:
    with urlopen(url) as response, open(dest_path, 'wb') as f:
        f.write(response.read())


def download_artwork(url: str, artist: str, album: str, base_dir: str = "media/music") -> str | None:
    """Download artwork if needed and return local path."""
    if not url:
        return None
    artist_dir = sanitize(artist or "Unknown Artist")
    album_dir = sanitize(album or "Unknown Album")
    target_dir = os.path.join(base_dir, artist_dir, album_dir)
    ensure_dir(target_dir)
    dest = os.path.join(target_dir, "artwork.jpg")
    if os.path.exists(dest):
        return dest
    art_url = artwork_600(url)
    download_file(art_url, dest)
    return dest


def download_preview(url: str, artist: str, album: str, base_dir: str = "media/music") -> str | None:
    """Download preview if needed and return local path."""
    if not url:
        return None
    artist_dir = sanitize(artist or "Unknown Artist")
    album_dir = sanitize(album or "Unknown Album")
    target_dir = os.path.join(base_dir, artist_dir, album_dir)
    ensure_dir(target_dir)
    filename = os.path.basename(urlparse(url).path) or "preview.mp3"
    dest = os.path.join(target_dir, filename)
    if os.path.exists(dest):
        return dest
    download_file(url, dest)
    return dest


def artwork_600(url100: str) -> str:
    """Convert a 100x100 artwork URL to 600x600."""
    return re.sub(r"100x100bb", "600x600bb", url100)


def handle_result(result: dict, base_dir: str) -> None:
    artist = result.get('artistName', 'Unknown Artist')
    album = result.get('collectionName', 'Unknown Album')
    artwork = result.get('artworkUrl100')
    preview = result.get('previewUrl')

    target_dir = os.path.join(base_dir, sanitize(artist), sanitize(album))
    ensure_dir(target_dir)

    approve = input(f"Download media for {artist} - {album}? [y/N]: ")
    if approve.lower() != 'y':
        return

    if artwork:
        try:
            download_artwork(artwork, artist, album, base_dir)
        except Exception as e:
            print(f"Failed to download artwork: {e}", file=sys.stderr)

    if preview:
        try:
            download_preview(preview, artist, album, base_dir)
        except Exception as e:
            print(f"Failed to download preview: {e}", file=sys.stderr)


def ingest_from_file(json_path: str, dest: str = 'media/music') -> None:
    """Process an iTunes search results file and download assets."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    results = data.get('results', [])
    for result in results:
        handle_result(result, dest)


def main() -> None:
    parser = argparse.ArgumentParser(description='Download iTunes media previews')
    parser.add_argument('json', help='Path to iTunes search results JSON')
    parser.add_argument('--dest', default='media/music', help='Destination directory')
    args = parser.parse_args()
    ingest_from_file(args.json, args.dest)


if __name__ == '__main__':
    main()
