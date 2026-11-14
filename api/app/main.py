"""Farm Case API.

From the api/ folder, with the repo-root virtual environment:

    ../.venv/Scripts/uvicorn app.main:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.analysis import ClimateUnavailable, build_case, build_clues
from app.models import CaseRequest, CaseResponse, CluesResponse

app = FastAPI(title="Farm Case API", version="0.1.0")

# The site and this API live on different origins. Browsers block that read
# unless we opt in. There is no login cookie, so the public demo allows any origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
