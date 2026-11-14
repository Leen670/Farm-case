"""Farm Case API.

From the api/ folder, with the repo-root virtual environment:

    ../.venv/Scripts/uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
