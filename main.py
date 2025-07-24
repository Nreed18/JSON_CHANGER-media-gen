import argparse
import os

from ingest import download_media, run_server, update_cache
from metadata_lookup import process_library


def main() -> None:
    """Ingest media, fetch metadata and start the review server."""
    parser = argparse.ArgumentParser(description="Ingest media and launch review server")
    parser.add_argument("--url", help="URL of media to download")
    parser.add_argument("--filename", help="Destination filename")
    parser.add_argument("--library", help="Path to station library file")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.url:
        path = download_media(args.url, args.filename)
        update_cache(args.url, path)

    library_path = args.library or os.environ.get("STATION_LIBRARY")
    if library_path:
        process_library(library_path)

    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
