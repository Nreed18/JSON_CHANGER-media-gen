import json
import os
import mimetypes
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from jinja2 import Environment, FileSystemLoader

CACHE_FILE = 'media_lookup_cache.json'
TEMPLATES = Environment(loader=FileSystemLoader('templates'))


def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_cache(data):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def render(template_name, **context):
    tpl = TEMPLATES.get_template(template_name)
    return tpl.render(**context).encode('utf-8')


def review_list(environ, start_response):
    cache = load_cache()
    items_html = ''
    for key, entry in cache.items():
        if entry.get('status') != 'approved':
            items_html += f'<li><a href="/review/{key}">{key}</a></li>'
    body = render('review_list.html', items=items_html)
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
                              ('Content-Length', str(len(body)))])
    return [body]


def review_item(environ, start_response, key):
    cache = load_cache()
    entry = cache.get(key)
    if not entry:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'Not found']

    if environ['REQUEST_METHOD'] == 'POST':
        size = int(environ.get('CONTENT_LENGTH', 0))
        data = parse_qs(environ['wsgi.input'].read(size).decode())
        idx = int(data.get('candidate', ['0'])[0])
        candidate = entry.get('candidates', [])[idx]
        candidate['status'] = 'approved'
        cache[key] = candidate
        save_cache(cache)
        start_response('302 Found', [('Location', '/review')])
        return [b'']

    candidates_html = ''
    for idx, cand in enumerate(entry.get('candidates', [])):
        art = cand.get('artwork', '')
        prev = cand.get('preview', '')
        meta_html = ''.join(
            f'<li>{k}: {v}</li>' for k, v in cand.items()
            if k not in {'artwork', 'preview'}
        )
        candidates_html += f'''<div>
  <img src="/static/{art}" alt="artwork" height="100"><br>
  <audio controls src="/static/{prev}"></audio>
  <ul>{meta_html}</ul>
  <form method="post">
    <input type="hidden" name="candidate" value="{idx}">
    <button type="submit">Approve</button>
  </form>
</div>\n'''
    body = render('review_item.html', key=key, candidates=candidates_html)
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
                              ('Content-Length', str(len(body)))])
    return [body]


def static_file(environ, start_response):
    path = environ['PATH_INFO'][len('/static/'):]  # remove prefix
    file_path = os.path.join('static', path)
    if not os.path.isfile(file_path):
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'Not found']
    ctype = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    with open(file_path, 'rb') as f:
        data = f.read()
    start_response('200 OK', [('Content-Type', ctype),
                              ('Content-Length', str(len(data)))])
    return [data]


def app(environ, start_response):
    path = environ.get('PATH_INFO', '')
    if path == '/review':
        return review_list(environ, start_response)
    if path.startswith('/review/'):
        key = path[len('/review/'):]
        return review_item(environ, start_response, key)
    if path.startswith('/static/'):
        return static_file(environ, start_response)

    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'Not found']


if __name__ == '__main__':
    port = 8000
    with make_server('', port, app) as httpd:
        print(f'Serving on port {port}...')
        httpd.serve_forever()
=======
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

CACHE_FILE = Path("media_lookup_cache.json")


def load_cache() -> Dict[str, dict]:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}


def save_cache(data: Dict[str, dict]) -> None:
    CACHE_FILE.write_text(json.dumps(data, indent=2))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    data = load_cache()
    return templates.TemplateResponse("index.html", {"request": request, "media": data})


@app.post("/approve")
async def approve(url: str = Form(...)):
    data = load_cache()
    if url in data:
        item = data[url]
        item["approved"] = True
        data[url] = item
        save_cache(data)
    return RedirectResponse(url="/", status_code=303)

