from pathlib import Path
from typing import Dict, Optional

import json
from fastapi import FastAPI, Form, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from metadata_lookup import process_library

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Environment(loader=FileSystemLoader("templates"))
CACHE_FILE = Path("media_lookup_cache.json")


def load_cache() -> Dict[str, dict]:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}


def save_cache(data: Dict[str, dict]) -> None:
    CACHE_FILE.write_text(json.dumps(data, indent=2))


def render(template: str, **context: str) -> str:
    return templates.get_template(template).render(**context)


@app.get("/", response_class=HTMLResponse)
async def index() -> RedirectResponse:
    """Redirect to the review list."""
    return RedirectResponse(url="/review")


@app.get("/review", response_class=HTMLResponse)
async def review_list() -> HTMLResponse:
    cache = load_cache()
    items_html = ""
    for key, entry in cache.items():
        status = entry.get("status")
        if status not in {"approved", "denied"}:
            items_html += f'<li><a href="/review/{key}">{key}</a></li>'
    body = render("review_list.html", items=items_html)
    return HTMLResponse(body)


@app.get("/review/{key}", response_class=HTMLResponse)
async def review_item(key: str) -> HTMLResponse:
    cache = load_cache()
    entry = cache.get(key)
    if not entry:
        raise HTTPException(status_code=404)

    candidates_html = ""
    for idx, cand in enumerate(entry.get("candidates", [])):
        art = cand.get("artwork", "")
        prev = cand.get("preview", "")
        meta_html = "".join(
            f"<li>{k}: {v}</li>" for k, v in cand.items() if k not in {"artwork", "preview"}
        )
        candidates_html += (
            f"<div>"
            f'<img src="/static/{art}" alt="artwork" height="100"><br>'
            f'<audio controls src="/static/{prev}"></audio>'
            f"<ul>{meta_html}</ul>"
            f'<form method="post">'
            f'<input type="hidden" name="candidate" value="{idx}">' \
            f'<button type="submit" name="action" value="approve">Approve</button>' \
            f'<button type="submit" name="action" value="deny">Deny</button>' \
            f"</form>" \
            f"</div>\n"
        )
    body = render("review_item.html", key=key, candidates=candidates_html)
    return HTMLResponse(body)


@app.post("/review/{key}")
async def approve_item(
    key: str,
    candidate: int = Form(...),
    action: str = Form("approve"),
) -> RedirectResponse:
    cache = load_cache()
    entry = cache.get(key)
    if not entry:
        raise HTTPException(status_code=404)

    cand_list = entry.get("candidates", [])
    if candidate < 0 or candidate >= len(cand_list):
        raise HTTPException(status_code=400)
    if action == "approve":
        cand = cand_list[candidate]
        cand["status"] = "approved"
        cache[key] = cand
    else:
        cache[key] = {"status": "denied"}
    save_cache(cache)
    return RedirectResponse(url="/review", status_code=303)


@app.get("/library", response_class=HTMLResponse)
async def upload_library_form() -> HTMLResponse:
    """Return an upload form for the station library."""
    body = render("upload_library.html")
    return HTMLResponse(body)


@app.post("/library")
async def upload_library(
    file: UploadFile = File(...),
    background_tasks: Optional[BackgroundTasks] = None,
) -> RedirectResponse:
    """Save uploaded library and process it in the background."""
    dest = Path("station_library.xlsx")
    contents = await file.read()
    dest.write_bytes(contents)
    if background_tasks is not None:
        background_tasks.add_task(process_library, str(dest))
    else:
        process_library(str(dest))
    return RedirectResponse(url="/review", status_code=303)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
