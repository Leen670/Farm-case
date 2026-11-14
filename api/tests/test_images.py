"""The picture proxy accepts GIBS map links and refuses everything else."""

from urllib.parse import quote

from fastapi.testclient import TestClient

from app.gibs import world_map_url
from app.images import require_gibs_url, GibsUrlError
from app.main import app


def test_only_gibs_map_links_are_allowed():
    allowed = world_map_url()
    assert require_gibs_url(allowed) == allowed
    assert require_gibs_url(quote(allowed, safe="")) == allowed

    refused = [
        "http://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi",
        "https://example.com/wms/epsg4326/best/wms.cgi",
        "https://user:pass@gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi",
        "https://gibs.earthdata.nasa.gov/other",
        "https://127.0.0.1/wms/epsg4326/best/wms.cgi",
        "file:///wms/epsg4326/best/wms.cgi",
    ]
    for url in refused:
        try:
            require_gibs_url(url)
        except GibsUrlError:
            continue
        raise AssertionError(url)


def test_image_route_refuses_another_host():
    response = TestClient(app).get(
        "/api/image",
        params={"url": "https://example.com/wms/epsg4326/best/wms.cgi"},
    )
    assert response.status_code == 400


def test_image_route_returns_a_gibs_picture(monkeypatch):
    async def fake(url: str):
        assert "gibs.earthdata.nasa.gov" in url
        return b"\x89PNG\r\n", "image/png"

    monkeypatch.setattr("app.main.fetch_gibs_image", fake)
    response = TestClient(app).get("/api/image", params={"url": world_map_url()})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/png")
    assert response.content.startswith(b"\x89PNG")


def test_world_map_offers_the_direct_picture_and_the_proxy():
    body = TestClient(app).get("/api/world-map").json()
    assert body["width"] == 2048
    assert body["height"] == 1024
    assert body["image_url"].startswith("https://gibs.earthdata.nasa.gov/")
    assert "BBOX=-90%2C-180%2C90%2C180" in body["image_url"] or "BBOX=-90,-180,90,180" in body["image_url"]
    assert body["proxy_path"].startswith("/api/image?url=")
    assert "gibs.earthdata.nasa.gov" in body["proxy_path"]
