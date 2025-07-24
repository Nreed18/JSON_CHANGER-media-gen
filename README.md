# JSON_CHANGER Media Generator

This project provides a simple script (`main.py`) for downloading album artwork
and preview MP3 files from iTunes search results. The media is stored in
`media/music/{Artist}/{Album}/`. The script uses only Python's standard
library, so no additional packages are required.

## Usage

1. Obtain an iTunes search results JSON file. The file should contain a `results` array where each item may include `artistName`, `collectionName`, `previewUrl` and `artworkUrl100` fields.
2. Run the script:

```bash
python3 main.py results.json
```

For each result the script will ask for confirmation before downloading. Album artwork is downloaded in 600x600 resolution. Existing artwork and preview files are reused.
