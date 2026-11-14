"""Farm Case API.

From the api/ folder, with the repo-root virtual environment:

    ../.venv/Scripts/uvicorn app.main:app --reload

Render starts it with the command in render.yaml, on the port Render assigns.
"""

import os
from urllib.parse import quote

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.analysis import ClimateUnavailable, build_case, build_clues
from app.gibs import WORLD_HEIGHT, WORLD_WIDTH, world_map_url
from app.images import GibsUrlError, ImageFetchError, fetch_gibs_image
from app.models import CaseRequest, CaseResponse, CluesResponse, SimpleCase, WorldMap
from app.simple_case import as_simple_case

# Vite's dev server. Kept even when CORS_ORIGINS names a deployed site.
LOCAL_ORIGINS = (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)
# The WebGL build runs inside itch's embed host, not on the game's page.
ITCH_ORIGINS = (
    "https://html-classic.itch.zone",
    "https://html.itch.zone",
)
# Any Vercel preview, any itch.io page, and any itch.zone embed host.
VERCEL_ORIGIN_PATTERN = r"https://.*\.vercel\.app"
ITCH_ORIGIN_PATTERN = r"https://([a-z0-9-]+\.)*itch\.(io|zone)"
BROWSER_ORIGIN_PATTERN = f"{VERCEL_ORIGIN_PATTERN}|{ITCH_ORIGIN_PATTERN}"


def cors_settings() -> tuple[list[str], str | None]:
    """Who may call this API from a browser.

    Unset or * leaves the demo open. There is no login cookie to protect.
    A list, set on Render as CORS_ORIGINS, names extra sites and still
    allows localhost, the itch.io embed hosts, any *.itch.io page, and
    any *.vercel.app site.
    """

    raw = os.environ.get("CORS_ORIGINS", "*").strip()
    if raw in ("", "*"):
        return ["*"], None
    origins = [part.strip() for part in raw.split(",") if part.strip()]
    for origin in LOCAL_ORIGINS + ITCH_ORIGINS:
        if origin not in origins:
            origins.append(origin)
    return origins, BROWSER_ORIGIN_PATTERN


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


@app.post("/api/case/simple", response_model=SimpleCase)
async def post_case_simple(case: CaseRequest) -> SimpleCase:
    """The same case, flattened for Unity's JsonUtility.

    Four clues, one recommended plan, and two alternatives. Strings are
    empty rather than null. demo_data is true when the climate came from
    a saved POWER response.
    """

    try:
        full = await build_case(case)
    except ClimateUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return as_simple_case(full, case.farmer_name)


@app.get("/api/world-map", response_model=WorldMap)
def get_world_map() -> WorldMap:
    """The farm-picker picture and the size the lat/lon formula expects.

    GIBS already lets any site load this picture. proxy_path is the same
    JPEG through this API, for a WebGL build whose page blocks GIBS.
    """

    image_url = world_map_url()
    return WorldMap(
        image_url=image_url,
        width=WORLD_WIDTH,
        height=WORLD_HEIGHT,
        proxy_path="/api/image?url=" + quote(image_url, safe=""),
    )


@app.get("/api/image")
async def get_image(url: str) -> Response:
    """Pass through one NASA GIBS picture. Other hosts are refused."""

    try:
        body, content_type = await fetch_gibs_image(url)
    except GibsUrlError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ImageFetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return Response(
        content=body,
        media_type=content_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )


async def _clues(case: CaseRequest):
    try:
        return await build_clues(case)
    except ClimateUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
