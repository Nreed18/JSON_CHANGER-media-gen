# JSON_CHANGER-media-gen

This repository contains a small utility to scan a JSON file with track
metadata and send an email report for tracks missing artwork or preview
MP3 files.

## Usage

1. Prepare a `tracks.json` file containing an array of track objects with
   at least the fields `title`, `artwork` and `preview_mp3`.
2. Export the following environment variables with your SMTP
   configuration:

   - `SMTP_HOST`
   - `SMTP_PORT`
   - `SMTP_USER`
   - `SMTP_PASS`
   - `EMAIL_FROM`
   - `EMAIL_TO` (comma-separated list)

3. Run the script:

```bash
python notify_missing_media.py tracks.json
```

The script will compile a list of tracks that lack artwork or a preview
MP3 and send a plaintext email using the provided SMTP credentials.
=======
=======
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
=======
# JSON Changer Media Gen

This repository contains a simple tool to ingest metadata from an Excel spreadsheet and enrich it with downloaded media. After manual approval through a web interface, the tool emails a notification to confirm that the assets are ready for further processing.

## Installation

1. Clone this repository.
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Workflow Overview

1. **Ingest Excel** – The script reads an `.xlsx` file, parsing each row into a JSON record. Media URLs or references are extracted as part of this process.
2. **Review via Web UI** – The records are loaded into a small Flask application that lets you confirm or modify the metadata before continuing.
3. **Download Media** – Once approved, the tool downloads all referenced files (images, videos, etc.) to the local machine.
4. **Email Notification** – After the downloads finish, an email is sent letting you know that the assets are ready. The example configuration uses environment variables to store email credentials and destination addresses.

## Configuration

Environment variables are loaded from a `.env` file using `python-dotenv`. Create a `.env` file in the project root and define at least the following variables:

```ini
EXCEL_PATH=path/to/input.xlsx
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USER=your_username
EMAIL_PASS=your_password
EMAIL_TO=recipient@example.com
```

Adjust the values to match your local setup. You can add additional variables as needed for the web server configuration or media download directories.

