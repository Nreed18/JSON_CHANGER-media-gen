import os
import sys
import json
import smtplib


def load_tracks(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def compile_missing(tracks):
    missing_artwork = []
    missing_preview = []
    for track in tracks:
        title = track.get('title') or track.get('name') or '<unknown>'
        if not track.get('artwork'):
            missing_artwork.append(title)
        if not track.get('preview_mp3'):
            missing_preview.append(title)
    return missing_artwork, missing_preview


def format_email(from_addr, to_addrs, missing_artwork, missing_preview):
    lines = []
    if missing_artwork:
        lines.append('Tracks missing artwork:')
        lines.extend(f'- {title}' for title in missing_artwork)
        lines.append('')
    if missing_preview:
        lines.append('Tracks missing preview MP3:')
        lines.extend(f'- {title}' for title in missing_preview)
        lines.append('')
    if not lines:
        lines.append('All tracks have artwork and preview MP3.')
    body = '\n'.join(lines)
    header = (
        f'From: {from_addr}\n'
        f'To: {", ".join(to_addrs)}\n'
        'Subject: Missing track media\n'
    )
    return f'{header}\n{body}'


def send_email(message, host, port, user, password, from_addr, to_addrs):
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        if user or password:
            server.login(user, password)
        server.sendmail(from_addr, to_addrs, message)


def main():
    if len(sys.argv) < 2:
        print('Usage: python notify_missing_media.py <tracks.json>')
        sys.exit(1)

    tracks = load_tracks(sys.argv[1])
    missing_artwork, missing_preview = compile_missing(tracks)

    host = os.environ.get('SMTP_HOST')
    port = int(os.environ.get('SMTP_PORT', 587))
    user = os.environ.get('SMTP_USER')
    password = os.environ.get('SMTP_PASS')
    from_addr = os.environ.get('EMAIL_FROM')
    to_addrs_raw = os.environ.get('EMAIL_TO', '')
    to_addrs = [a.strip() for a in to_addrs_raw.split(',') if a.strip()]

    if not host or not from_addr or not to_addrs:
        print('SMTP credentials and email addresses must be provided via environment variables.')
        sys.exit(1)

    message = format_email(from_addr, to_addrs, missing_artwork, missing_preview)
    send_email(message, host, port, user, password, from_addr, to_addrs)


if __name__ == '__main__':
    main()
