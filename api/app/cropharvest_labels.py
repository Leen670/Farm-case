"""Compare a pin with CropHarvest labels. This does not download satellite arrays.

The labels file is locations, a crop name, and a date. Zenodo record
10251170, the version pinned by the CropHarvest library, lists that file
at about 86 MB. The satellite archive beside it is tens of gigabytes.
accept_download refuses anything that is not the labels file, or anything
over 100 MB, so a wrong URL cannot pull the imagery.
"""

from __future__ import annotations

LABELS_NAME = "labels.geojson"
MAX_LABEL_BYTES = 100_000_000
# A named label farther than this is a different landscape, not this farm.
SAME_LANDSCAPE_KM = 50.0


def accept_download(filename: str, size_bytes: int) -> None:
    """Raise unless this is the labels file and it is small enough to keep."""

    if filename != LABELS_NAME:
        raise ValueError(f"Refusing {filename}. Only {LABELS_NAME} is downloaded.")
    if size_bytes <= 0 or size_bytes > MAX_LABEL_BYTES:
        raise ValueError(
            f"Refusing {filename} at {size_bytes} bytes. The labels file is under 100 MB."
        )


def cropland_count(points: list[dict]) -> tuple[int, int]:
    """How many nearby points are marked cropland, and how many points there are."""

    return sum(1 for point in points if point.get("is_crop")), len(points)


def named_crop_is_here(nearest_named_km: float) -> bool:
    """True only when a crop name was collected inside the same landscape."""

    return nearest_named_km <= SAME_LANDSCAPE_KM
