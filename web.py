import json
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
