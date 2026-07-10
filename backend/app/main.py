import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from .schemas import GenerateRequest, GenerateResponse  # noqa: E402
from .services.analyst import AnalystError, build_dossier  # noqa: E402
from .services.scraper import ScrapeError, scrape_site  # noqa: E402

app = FastAPI(title="ColdOpen", version="0.1.0")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


# Sync endpoint on purpose: FastAPI runs it in a threadpool, and both the
# scrape and the Claude call are blocking.
@app.post("/api/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    started = time.monotonic()
    try:
        site = scrape_site(req.url)
    except ScrapeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        dossier = build_dossier(site)
    except AnalystError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return GenerateResponse(
        dossier=dossier,
        scraped_title=site.title or None,
        generated_in_seconds=round(time.monotonic() - started, 1),
    )
