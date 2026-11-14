"""NASA GIBS snapshot links for one farm pin. This module does not call NASA.

Layer ids and time ranges were read from the WMS and WMTS GetCapabilities
documents on 14 Nov 2026:

- SMAP_L3_Passive_Enhanced_Day_Soil_Moisture, daily, default date 2026-11-11.
  WMTS max zoom is GoogleMapsCompatible_Level6.
- MODIS_Terra_NDVI_8Day, daily timestamps of an 8-day composite, default
  2026-11-13. WMTS max zoom is Level9.
- IMERG_Precipitation_Rate, daily, default 2026-11-13. WMTS max zoom is Level6.

The WMS capabilities do not publish a max scale for these layers. A GetMap
of a small box still returns a PNG. At SMAP and IMERG resolution that PNG is
one blob, which is the pixel, not a missing tile.

WMS 1.3.0 with CRS EPSG:4326 takes the box as latitude, then longitude.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from urllib.parse import urlencode

WMS_ENDPOINT = "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi"

# A finished daylight photo of the whole Earth. A daily MODIS true-colour
# frame is one satellite pass, so half the globe is black. January 2004 is
# the Blue Marble month GIBS publishes as a complete mosaic.
WORLD_LAYER = "BlueMarble_NextGeneration"
WORLD_TIME = date(2004, 1, 1)
WORLD_WIDTH = 2048
WORLD_HEIGHT = 1024

# Half the width of the snapshot, in degrees. About 33 km north-south.
# SMAP pixels are 9 km, so this frame is one blob. MODIS is 250 m, so the
# same frame shows the fields around the pin.
BOX_HALF_DEGREES = 0.15
IMAGE_SIZE = 256

# The wetness number next to the SMAP picture is a POWER value, not a SMAP value.
POWER_WETNESS_LABEL = "NASA POWER GWETROOT"

# The challenge names these. They are not requested.
NAMED_ONLY = ("Landsat", "VIIRS")

# lag_days: how far behind "today" a finished image usually is.
# fallback_days: extra step if that image is blank (SMAP swath gap, or a
# composite that has not been published yet).
_LAYERS = (
    {
        "layer_id": "SMAP_L3_Passive_Enhanced_Day_Soil_Moisture",
        "source_label": "SMAP image (NASA GIBS)",
        "lag_days": 3,
        "fallback_days": 3,
        "max_zoom": 6,
    },
    {
        "layer_id": "MODIS_Terra_NDVI_8Day",
        "source_label": "MODIS NDVI image (NASA GIBS)",
        "lag_days": 16,
        "fallback_days": 16,
        "max_zoom": 9,
    },
    {
        "layer_id": "IMERG_Precipitation_Rate",
        "source_label": "GPM IMERG image (NASA GIBS)",
        "lag_days": 2,
        "fallback_days": 2,
        "max_zoom": 6,
    },
)


def snapshots(lat: float, lon: float, day: date | datetime) -> list[dict[str, str | int]]:
    """Build the water, crop, and rain picture links for this pin and day.

    The day argument is the day the player asked about. Each link uses an
    earlier day, because these layers are published late.
    """
    if isinstance(day, datetime):
        day = day.date()
    return [_snapshot(lat, lon, day, layer) for layer in _LAYERS]


def _snapshot(lat: float, lon: float, day: date, layer: dict) -> dict[str, str | int]:
    used = day - timedelta(days=layer["lag_days"])
    fallback = used - timedelta(days=layer["fallback_days"])
    return {
        "layer_id": layer["layer_id"],
        "date_used": used.isoformat(),
        "url": _getmap_url(layer["layer_id"], used, lat, lon),
        "source_label": layer["source_label"],
        "fallback_date": fallback.isoformat(),
        "fallback_url": _getmap_url(layer["layer_id"], fallback, lat, lon),
        "max_zoom": layer["max_zoom"],
    }


def _getmap_url(layer_id: str, day: date, lat: float, lon: float) -> str:
    query = urlencode(
        [
            ("SERVICE", "WMS"),
            ("VERSION", "1.3.0"),
            ("REQUEST", "GetMap"),
            ("LAYERS", layer_id),
            ("STYLES", ""),
            ("FORMAT", "image/png"),
            ("TRANSPARENT", "TRUE"),
            ("CRS", "EPSG:4326"),
            ("BBOX", _bbox(lat, lon)),
            ("WIDTH", str(IMAGE_SIZE)),
            ("HEIGHT", str(IMAGE_SIZE)),
            ("TIME", day.isoformat()),
        ],
        safe=",",
    )
    return f"{WMS_ENDPOINT}?{query}"


def world_map_url() -> str:
    """One north-up picture of the Earth, for the farm picker.

    WMS 1.3.0 wants the box as south, west, north, east. The longitude-first
    box -180,-90,180,90 is a strip along the equator, not the globe.
    """

    query = urlencode(
        [
            ("SERVICE", "WMS"),
            ("VERSION", "1.3.0"),
            ("REQUEST", "GetMap"),
            ("LAYERS", WORLD_LAYER),
            ("STYLES", ""),
            ("FORMAT", "image/jpeg"),
            ("CRS", "EPSG:4326"),
            ("BBOX", "-90,-180,90,180"),
            ("WIDTH", str(WORLD_WIDTH)),
            ("HEIGHT", str(WORLD_HEIGHT)),
            ("TIME", WORLD_TIME.isoformat()),
        ],
        safe=",",
    )
    return f"{WMS_ENDPOINT}?{query}"


def pixel_to_lon_lat(x: float, y: float, width: int, height: int) -> tuple[float, float]:
    """Map a click on the world picture to longitude and latitude.

    x and y are pixels from the left and from the top. The top-left pixel
    is 180°W, 90°N. The bottom-right pixel is 180°E, 90°S.
    """

    if width <= 0 or height <= 0:
        raise ValueError("The world picture needs a positive size.")
    lon = x / width * 360.0 - 180.0
    lat = 90.0 - y / height * 180.0
    return lon, lat


def _bbox(lat: float, lon: float) -> str:
    """WMS 1.3.0 EPSG:4326 order: south, west, north, east."""
    south = max(-90.0, lat - BOX_HALF_DEGREES)
    north = min(90.0, lat + BOX_HALF_DEGREES)
    west = max(-180.0, lon - BOX_HALF_DEGREES)
    east = min(180.0, lon + BOX_HALF_DEGREES)
    return f"{south:.4f},{west:.4f},{north:.4f},{east:.4f}"
