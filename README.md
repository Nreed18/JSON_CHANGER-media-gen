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

