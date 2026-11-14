"""Farm Case API.

From the api/ folder, with the repo-root virtual environment:

    ../.venv/Scripts/uvicorn app.main:app --reload

Render starts it with the command in render.yaml, on the port Render assigns.
"""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.analysis import ClimateUnavailable, build_case, build_clues
from app.models import CaseRequest, CaseResponse, CluesResponse

# Vite's dev server. Kept even when CORS_ORIGINS names a deployed site.
LOCAL_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)
# Any Vercel production or preview URL. The project name is not chosen yet.
VERCEL_ORIGIN_PATTERN = r"https://.*\.vercel\.app"


def cors_settings() -> tuple[list[str], str | None]:
    """Who may call this API from a browser.

    Unset or * leaves the demo open. There is no login cookie to protect.
    A list, set on Render as CORS_ORIGINS, names extra sites and still
    allows localhost plus any *.vercel.app site.
    """

    raw = os.environ.get("CORS_ORIGINS", "*").strip()
    if raw in ("", "*"):
        return ["*"], None
    origins = [part.strip() for part in raw.split(",") if part.strip()]
    for local in LOCAL_ORIGINS:
        if local not in origins:
            origins.append(local)
    return origins, VERCEL_ORIGIN_PATTERN


_origins, _origin_regex = cors_settings()

app = FastAPI(title="Farm Case API", version="0.1.0")

# The site and this API live on different hosts. The browser will only
# show the response if we name the site's origin here.
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_origin_regex=_origin_regex,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, bool]:
    """Lets us confirm the API is up and wake a sleeping host before a demo."""
    return {"ok": True}


@app.post("/api/clues", response_model=CluesResponse)
async def post_clues(case: CaseRequest) -> CluesResponse:
    """Four evidence cards for this pin: climate, soil, water, and crop.

    The numbers come from NASA POWER. Soil is whatever the farmer entered.
    The crop card's image is a MODIS NDVI picture from NASA GIBS.
    """

    clues, _used_fallback = await _clues(case)
    return CluesResponse(clues=clues)


@app.post("/api/case", response_model=CaseResponse)
async def post_case(case: CaseRequest) -> CaseResponse:
    """The ranked rotation for this farm, plus the four clues behind it.

    The scorer picks the crops. The explanation only describes that result.
    used_fallback is true when the climate numbers came from a saved response.
    """

    try:
        return await build_case(case)
    except ClimateUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


async def _clues(case: CaseRequest):
    try:
        return await build_clues(case)
    except ClimateUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
