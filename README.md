# JSON Changer Media Gen

This repository provides small tools for managing music metadata and the related media assets. The utilities let you ingest source data, review the collected items in a browser and download approved files.

## Installation

1. Clone this repository.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Workflow

### 1. Ingest
Use `main.py` to download a media URL and optionally look up metadata from a station library.

```bash
python main.py --url "https://example.com/file.mp3" --library station_library.xlsx
```

The file is stored under the `media` directory, metadata is cached and everything is recorded in `media_lookup_cache.json`.

### 2. Review
The same command launches the review server. You can also start it without ingesting anything:

```bash
python main.py
```

Open `http://localhost:8000` and mark each entry as approved. Approved files remain available in the `media` folder.

### 3. Download
After approval you can process the assets further or transfer them to their final destination. The status field (`auto` or `approved`) is stored alongside the file path in `media_lookup_cache.json`.

## Additional utilities

`notify_missing_media.py` scans a `tracks.json` list and emails a report for tracks missing artwork or preview MP3 files. Configure SMTP details via environment variables if you use this script.

## Configuration

Create a `.env` file for any required environment variables. A typical email configuration looks like:

```ini
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_username
SMTP_PASS=your_password
EMAIL_FROM=sender@example.com
EMAIL_TO=recipient@example.com
```

Adjust values as needed for your setup.

