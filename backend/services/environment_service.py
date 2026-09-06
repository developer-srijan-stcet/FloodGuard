"""
Automatic environmental-data collection for a latitude/longitude.

Sources:
- Open-Meteo: elevation + soil moisture.
- Open-Meteo elevation grid: surrounding elevations used to calculate slope.
- National Water Data Portal / CWC: river water-level telemetry CSV resources.

No environmental value is accepted from the frontend.
"""

from __future__ import annotations

import io
import math
import time
from typing import Any

import pandas as pd
import requests


# ============================================================
# API URLs
# ============================================================

ELEVATION_URL = "https://api.open-meteo.com/v1/elevation"
SOIL_URL = "https://api.open-meteo.com/v1/ecmwf"


# ============================================================
# River datasets
# ============================================================

RIVER_DATASETS = [
    {
        "name": "CWC Subernarekha",
        "url": "https://nwdp.nwic.gov.in/dataset/68600163-c5a0-4327-aa1a-fa7157b86cce/resource/1e23cbb8-c1ce-4434-a635-8231535305f3/download/rwl_tel_hr_cwc_003_2026_2030.csv",
    },
    {
        "name": "CWC Brahmani and Baitarni",
        "url": "https://nwdp.nwic.gov.in/dataset/68600163-c5a0-4327-aa1a-fa7157b86cce/resource/178082a5-2a2b-445e-b059-97337f325cd7/download/rwl_tel_hr_cwc_004_2026_2030.csv",
    },
    {
        "name": "CWC Mahanadi",
        "url": "https://nwdp.nwic.gov.in/dataset/68600163-c5a0-4327-aa1a-fa7157b86cce/resource/0ab89c38-558f-47b5-818e-eda9f17cffc4/download/rwl_tel_hr_cwc_005_2026_2030.csv",
    },
    {
        "name": "CWC Godavari",
        "url": "https://nwdp.nwic.gov.in/dataset/68600163-c5a0-4327-aa1a-fa7157b86cce/resource/c6f31452-b416-4599-a6ae-07ad4217cdf4/download/rwl_tel_hr_cwc_006_2026_2030.csv",
    },
    {
        "name": "CWC Krishna",
        "url": "https://nwdp.nwic.gov.in/dataset/68600163-c5a0-4327-aa1a-fa7157b86cce/resource/d80798b9-4b11-4626-8b63-964202ba7216/download/rwl_tel_hr_cwc_007_2026_2030.csv",
    },
    {
        "name": "CWC Pennar",
        "url": "https://nwdp.nwic.gov.in/dataset/68600163-c5a0-4327-aa1a-fa7157b86cce/resource/2ef9e34a-4a1b-4fe9-a542-9f7623289f47/download/rwl_tel_hr_cwc_008_2026_2030.csv",
    },
    {
        "name": "CWC Cauvery",
        "url": "https://nwdp.nwic.gov.in/dataset/68600163-c5a0-432c-8ced-97b02b6edbc0/resource/d027c5ac-379d-4ac2-8ced-97b02b6edbc0/download/rwl_tel_hr_cwc_009_2026_2030.csv",
    },
    {
        "name": "CWC Tapi",
        "url": "https://nwdp.nwic.gov.in/dataset/68600163-c5a0-4327-aa1a-fa7157b86cce/resource/6c99c7f3-f8f2-4381-98aa-611d27921fde/download/rwl_tel_hr_cwc_010_2026_2030.csv",
    },
    {
        "name": "CWC Narmada",
        "url": "https://nwdp.nwic.gov.in/dataset/68600163-c5a0-4327-aa1a-fa7157b86cce/resource/a2e056f6-ed8a-45bf-9142-01dc1904405a/download/rwl_tel_hr_cwc_011_2026_2030.csv",
    },
    {
        "name": "CWC Mahi",
        "url": "https://nwdp.nwic.gov.in/dataset/68600163-c5a0-4327-aa1a-fa7157b86cce/resource/0b7cab7a-9ab7-4343-9316-fdbf17dde48b/download/rwl_tel_hr_cwc_012_2026_2030.csv",
    },
    {
        "name": "CWC Sabarmati",
        "url": "https://nwdp.nwic.gov.in/dataset/68600163-c5a0-4327-aa1a-fa7157b86cce/resource/7d180b02-f572-4d75-b8bd-18667e7c52ec/download/rwl_tel_hr_cwc_013_2026_2030.csv",
    },
    {
        "name": "CWC Kutch/Saurashtra/Luni",
        "url": "https://nwdp.nwic.gov.in/dataset/68600163-c5a0-4327-aa1a-fa7157b86cce/resource/6c357b24-d7cb-4725-afaa-36b0a08f5f06/download/rwl_tel_hr_cwc_014_2026_2030.csv",
    },
    {
        "name": "CWC West flowing Tapi-Tadri",
        "url": "https://nwdp.nwic.gov.in/dataset/68600163-c5a0-4327-aa1a-fa7157b86cce/resource/88d6f0d7-52a9-46cd-a030-a7b39076083e/download/rwl_tel_hr_cwc_015_2026_2030.csv",
    },
    {
        "name": "CWC East flowing Pennar-Kanyakumari",
        "url": "https://nwdp.nwic.gov.in/dataset/68600163-c5a0-4327-aa1a-fa7157b86cce/resource/dc45c606-eaed-4e9e-a4f0-84152ff13e10/download/rwl_tel_hr_cwc_27_2026_2030.csv",
    },
    {
        "name": "West Bengal Surface Water Subernarekha",
        "url": "https://nwdp.nwic.gov.in/dataset/e5ccd0c1-eec5-44ad-85e6-5482f643577c/resource/8f85a8d1-4fe7-454b-8350-0578f23ff71c/download/rwl_tel_hr_west_bengal-surface_water_bengal-sw_003_2026_2030.csv",
    },
]


# ============================================================
# Cache
# ============================================================

_CACHE: dict[str, tuple[float, pd.DataFrame]] = {}

CACHE_SECONDS = 3600

# Render Free has only 512 MB RAM.
# Do not allow extremely large files to be loaded.
MAX_DOWNLOAD_SIZE = 15 * 1024 * 1024  # 15 MB


# ============================================================
# HTTP JSON helper
# ============================================================

def _get_json(
    url: str,
    params: dict[str, Any],
    timeout: int | tuple[int, int] = 20,
) -> dict[str, Any]:

    response = requests.get(
        url,
        params=params,
        timeout=timeout,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# Haversine distance
# ============================================================

def _haversine_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:

    radius = 6371.0088

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = (
        math.sin(dp / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dl / 2) ** 2
    )

    return 2 * radius * math.asin(
        math.sqrt(a)
    )


# ============================================================
# Column helpers
# ============================================================

def _normalise(name: str) -> str:

    return "".join(
        ch.lower() if ch.isalnum() else "_"
        for ch in str(name)
    ).strip("_")


def _find_column(
    df: pd.DataFrame,
    candidates: list[str],
) -> str | None:

    mapping = {
        _normalise(col): col
        for col in df.columns
    }

    # Exact match first.
    for candidate in candidates:

        key = _normalise(candidate)

        if key in mapping:
            return mapping[key]

    # Partial match second.
    for col in df.columns:

        normalised_col = _normalise(col)

        for candidate in candidates:

            if _normalise(candidate) in normalised_col:
                return col

    return None


# ============================================================
# Download river dataset
# ============================================================

def _download_river_dataset(
    dataset: dict[str, str],
) -> pd.DataFrame:

    now = time.time()

    url = dataset["url"]

    cached = _CACHE.get(url)

    if cached:

        cached_time, cached_df = cached

        if now - cached_time < CACHE_SECONDS:
            return cached_df

    print(
        f"Downloading river dataset: "
        f"{dataset['name']}"
    )

    response = requests.get(
        url,
        timeout=(3, 8),
        stream=True,
    )

    response.raise_for_status()

    chunks: list[bytes] = []

    total_size = 0

    try:

        for chunk in response.iter_content(
            chunk_size=256 * 1024
        ):

            if not chunk:
                continue

            total_size += len(chunk)

            if total_size > MAX_DOWNLOAD_SIZE:

                raise RuntimeError(
                    f"River dataset is too large: "
                    f"{dataset['name']}"
                )

            chunks.append(chunk)

    finally:

        response.close()

    content = b"".join(chunks)

    if not content:

        raise RuntimeError(
            f"Empty river dataset: "
            f"{dataset['name']}"
        )

    try:

        df = pd.read_csv(
            io.BytesIO(content),
            low_memory=True,
        )

    finally:

        # Release downloaded bytes as soon as possible.
        del content
        del chunks

    print(
        f"Loaded {dataset['name']} "
        f"with {len(df)} rows"
    )

    _CACHE[url] = (
        now,
        df,
    )

    return df


# ============================================================
# Select river datasets according to state
# ============================================================

def _river_candidates_for_state(
    state: str | None,
) -> list[dict[str, str]]:

    state = (state or "").strip().lower()

    if "west bengal" in state:

        preferred = [
            "West Bengal Surface Water Subernarekha",
            "CWC Subernarekha",
        ]

    elif "odisha" in state:

        preferred = [
            "CWC Mahanadi",
            "CWC Brahmani and Baitarni",
            "CWC Subernarekha",
        ]

    elif "jharkhand" in state:

        preferred = [
            "CWC Subernarekha",
            "CWC Brahmani and Baitarni",
        ]

    else:

        preferred = []

    rank = {
        name: index
        for index, name in enumerate(preferred)
    }

    return sorted(
        RIVER_DATASETS,
        key=lambda x: rank.get(
            x["name"],
            999,
        ),
    )


# ============================================================
# Extract station information
# ============================================================

def _extract_station_frame(
    df: pd.DataFrame,
) -> pd.DataFrame | None:

    lat_col = _find_column(
        df,
        [
            "latitude",
            "lat",
            "station_latitude",
        ],
    )

    lon_col = _find_column(
        df,
        [
            "longitude",
            "lon",
            "lng",
            "station_longitude",
        ],
    )

    level_col = _find_column(
        df,
        [
            "river_water_level",
            "river water level",
            "water_level",
            "water level",
            "rwl",
        ],
    )

    station_col = _find_column(
        df,
        [
            "station_name",
            "station name",
            "station",
            "station_id",
            "station id",
        ],
    )

    river_col = _find_column(
        df,
        [
            "river_name",
            "river name",
            "river",
        ],
    )

    if not lat_col or not lon_col or not level_col:
        print(
            "Required river columns were not found."
        )
        return None

    # Only keep the columns we actually need.
    out = pd.DataFrame(
        {
            "latitude": pd.to_numeric(
                df[lat_col],
                errors="coerce",
            ),
            "longitude": pd.to_numeric(
                df[lon_col],
                errors="coerce",
            ),
            "river_level": pd.to_numeric(
                df[level_col],
                errors="coerce",
            ),
        }
    )

    if station_col:

        out["station"] = (
            df[station_col]
            .fillna("CWC station")
            .astype(str)
        )

    else:

        out["station"] = "CWC station"

    if river_col:

        out["river"] = (
            df[river_col]
            .fillna("Unknown river")
            .astype(str)
        )

    else:

        out["river"] = "Unknown river"

    out = out.dropna(
        subset=[
            "latitude",
            "longitude",
            "river_level",
        ]
    )

    if out.empty:
        return None

    return out


# ============================================================
# Find nearest river station
# ============================================================

def get_river_level(
    latitude: float,
    longitude: float,
    state: str | None = None,
) -> dict[str, Any]:

    best: dict[str, Any] | None = None

    datasets = _river_candidates_for_state(
        state
    )

    for dataset in datasets:

        try:

            print(
                f"Checking river dataset: "
                f"{dataset['name']}"
            )

            raw = _download_river_dataset(
                dataset
            )

            stations = _extract_station_frame(
                raw
            )

            if stations is None:
                continue

            if stations.empty:
                continue

            # =================================================
            # IMPORTANT FIX
            #
            # Do NOT parse date/datetime columns here.
            #
            # The previous implementation did:
            #
            # parsed = pd.to_datetime(...)
            # stations["_time"] = ...
            #
            # This caused:
            # "Length of values does not match length of index"
            #
            # It also consumed a large amount of RAM on Render.
            #
            # We only need the nearest station for location
            # environmental data, so timestamp processing is
            # unnecessary here.
            # =================================================

            # Calculate distance using the Haversine formula.
            distances = []

            for row in stations.itertuples(
                index=False
            ):

                distance = _haversine_km(
                    latitude,
                    longitude,
                    float(row.latitude),
                    float(row.longitude),
                )

                distances.append(distance)

            stations["distance_km"] = distances

            nearest_index = stations[
                "distance_km"
            ].idxmin()

            row = stations.loc[
                nearest_index
            ]

            distance = float(
                row["distance_km"]
            )

            candidate = {
                "river_level": float(
                    row["river_level"]
                ),
                "station_name": str(
                    row["station"]
                ),
                "river_name": str(
                    row["river"]
                ),
                "station_latitude": float(
                    row["latitude"]
                ),
                "station_longitude": float(
                    row["longitude"]
                ),
                "distance_km": round(
                    distance,
                    2,
                ),
                "source": dataset["url"],
                "dataset": dataset["name"],
            }

            if (
                best is None
                or candidate["distance_km"]
                < best["distance_km"]
            ):

                best = candidate

            print(
                f"Nearest station in "
                f"{dataset['name']}: "
                f"{candidate['station_name']} "
                f"({candidate['distance_km']} km)"
            )

            # For nearby locations, there is no reason
            # to download every other Indian river dataset.
            if distance <= 10:

                print(
                    "Very close river station found. "
                    "Stopping dataset search."
                )

                break

        except Exception as exc:

            print(
                f"River dataset unavailable: "
                f"{dataset['name']} - {exc}"
            )

            continue

    # ========================================================
    # No river station found
    # ========================================================

    if best is None:

        return {
            "river_level": None,
            "station_name": None,
            "river_name": None,
            "station_latitude": None,
            "station_longitude": None,
            "distance_km": None,
            "source": None,
            "dataset": None,
            "available": False,
        }

    best["available"] = True

    return best


# ============================================================
# Calculate slope
# ============================================================

def _calculate_slope(
    latitude: float,
    longitude: float,
    elevations: list[float],
) -> float:

    # Points:
    #
    # 0 = center
    # 1 = north
    # 2 = south
    # 3 = east
    # 4 = west

    center, north, south, east, west = elevations

    lat_m = 90.0

    lon_m = (
        90.0
        * max(
            math.cos(
                math.radians(latitude)
            ),
            0.01,
        )
    )

    dz_dy = (
        north - south
    ) / (2 * lat_m)

    dz_dx = (
        east - west
    ) / (2 * lon_m)

    gradient = math.sqrt(
        dz_dx ** 2
        + dz_dy ** 2
    )

    return round(
        math.degrees(
            math.atan(gradient)
        ),
        2,
    )


# ============================================================
# Fetch all environmental data
# ============================================================

def fetch_environment(
    latitude: float,
    longitude: float,
    state: str | None = None,
) -> dict[str, Any]:

    print(
        "Fetching weather, elevation, "
        "soil moisture, slope and river telemetry..."
    )

    # ========================================================
    # Elevation
    # ========================================================

    lat_offset = (
        90.0 / 111_320.0
    )

    lon_offset = (
        90.0
        / (
            111_320.0
            * max(
                math.cos(
                    math.radians(latitude)
                ),
                0.01,
            )
        )
    )

    points = [
        (latitude, longitude),

        (
            latitude + lat_offset,
            longitude,
        ),

        (
            latitude - lat_offset,
            longitude,
        ),

        (
            latitude,
            longitude + lon_offset,
        ),

        (
            latitude,
            longitude - lon_offset,
        ),
    ]

    elevation_data = _get_json(
        ELEVATION_URL,
        {
            "latitude": ",".join(
                str(point[0])
                for point in points
            ),
            "longitude": ",".join(
                str(point[1])
                for point in points
            ),
        },
        timeout=(3, 8),
    )

    elevations = [
        float(value)
        for value in elevation_data.get(
            "elevation",
            [],
        )
    ]

    if len(elevations) != 5:

        raise RuntimeError(
            "Elevation API returned "
            "incomplete terrain data"
        )

    # ========================================================
    # Soil moisture
    # ========================================================

    weather_data = _get_json(
        SOIL_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "soil_moisture_0_to_7cm",
            "forecast_hours": 1,
            "timezone": "auto",
        },
        timeout=(3, 8),
    )

    hourly = weather_data.get(
        "hourly",
        {},
    )

    values = hourly.get(
        "soil_moisture_0_to_7cm"
    ) or []

    soil_raw = (
        values[0]
        if values
        else None
    )

    if soil_raw is None:

        raise RuntimeError(
            "Soil moisture API did not "
            "return a value"
        )

    # ========================================================
    # River level
    # ========================================================

    river = get_river_level(
        latitude,
        longitude,
        state,
    )

    # ========================================================
    # Return environmental data
    # ========================================================

    return {
        "elevation": round(
            elevations[0],
            2,
        ),

        "slope": _calculate_slope(
            latitude,
            longitude,
            elevations,
        ),

        "soil_moisture": round(
            float(soil_raw) * 100.0,
            2,
        ),

        "river_level": river[
            "river_level"
        ],

        "river_station_name": river[
            "station_name"
        ],

        "river_name": river[
            "river_name"
        ],

        "river_station_latitude": river[
            "station_latitude"
        ],

        "river_station_longitude": river[
            "station_longitude"
        ],

        "river_distance_km": river[
            "distance_km"
        ],

        "river_level_source": river[
            "source"
        ],

        "river_dataset": river[
            "dataset"
        ],

        "river_available": river[
            "available"
        ],

        "sources": {
            "elevation": ELEVATION_URL,
            "soil_moisture": SOIL_URL,
            "slope": (
                "Calculated from "
                "Open-Meteo/Copernicus DEM elevations"
            ),
            "river_level": river[
                "source"
            ],
        },
    }
