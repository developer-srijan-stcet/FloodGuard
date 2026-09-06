"""Automatic environmental-data collection for a latitude/longitude.

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

ELEVATION_URL = "https://api.open-meteo.com/v1/elevation"
SOIL_URL = "https://api.open-meteo.com/v1/ecmwf"

# Current 2026-2030 telemetry resources published by NWDP/CWC.
# The service downloads these only when it needs to find a nearby station and
# keeps a short in-process cache to avoid repeatedly downloading the files.
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
        "url": "https://nwdp.nwic.gov.in/dataset/68600163-c5a0-4327-aa1a-fa7157b86cce/resource/d027c5ac-379d-4ac2-8ced-97b02b6edbc0/download/rwl_tel_hr_cwc_009_2026_2030.csv",
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

_CACHE: dict[str, tuple[float, pd.DataFrame]] = {}
CACHE_SECONDS = 3600


def _get_json(url: str, params: dict[str, Any], timeout: int = 20) -> dict[str, Any]:
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def _normalise(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(name)).strip("_")


def _find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    mapping = {_normalise(col): col for col in df.columns}
    for candidate in candidates:
        if _normalise(candidate) in mapping:
            return mapping[_normalise(candidate)]
    for col in df.columns:
        n = _normalise(col)
        if any(_normalise(c) in n for c in candidates):
            return col
    return None


def _download_river_dataset(dataset: dict[str, str]) -> pd.DataFrame:
    now = time.time()

    cached = _CACHE.get(dataset["url"])
    if cached and now - cached[0] < CACHE_SECONDS:
        return cached[1]

    response = requests.get(
    dataset["url"],
    timeout=(3, 5),
    stream=True,
)
    response.raise_for_status()

    # Limit the amount of data downloaded into memory.
    max_size = 50 * 1024 * 1024  # 50 MB

    chunks = []
    total_size = 0

    for chunk in response.iter_content(chunk_size=1024 * 1024):
        if not chunk:
            continue

        total_size += len(chunk)

        if total_size > max_size:
            response.close()
            raise RuntimeError(
                f"River dataset is too large: {dataset['name']}"
            )

        chunks.append(chunk)

    content = b"".join(chunks)

    df = pd.read_csv(
        io.BytesIO(content),
        low_memory=True,
    )

    _CACHE[dataset["url"]] = (now, df)

    return df


def _river_candidates_for_state(state: str | None) -> list[dict[str, str]]:
    state = (state or "").strip().lower()
    if "west bengal" in state:
        preferred = ["West Bengal Surface Water Subernarekha", "CWC Subernarekha"]
    elif "odisha" in state:
        preferred = ["CWC Mahanadi", "CWC Brahmani and Baitarni", "CWC Subernarekha"]
    elif "jharkhand" in state:
        preferred = ["CWC Subernarekha", "CWC Brahmani and Baitarni"]
    else:
        preferred = []
    rank = {name: i for i, name in enumerate(preferred)}
    return sorted(RIVER_DATASETS, key=lambda x: rank.get(x["name"], 999))


def _extract_station_frame(df: pd.DataFrame) -> pd.DataFrame | None:
    lat_col = _find_column(df, ["latitude", "lat", "station_latitude"])
    lon_col = _find_column(df, ["longitude", "lon", "lng", "station_longitude"])
    level_col = _find_column(df, ["river_water_level", "river water level", "water_level", "water level", "rwl"])
    station_col = _find_column(df, ["station_name", "station name", "station", "station_id", "station id"])
    river_col = _find_column(df, ["river_name", "river name", "river"])

    if not lat_col or not lon_col or not level_col:
        return None

    out = pd.DataFrame({
        "latitude": pd.to_numeric(df[lat_col], errors="coerce"),
        "longitude": pd.to_numeric(df[lon_col], errors="coerce"),
        "river_level": pd.to_numeric(df[level_col], errors="coerce"),
    })
    out["station"] = df[station_col].astype(str) if station_col else "CWC station"
    out["river"] = df[river_col].astype(str) if river_col else "Unknown river"
    out = out.dropna(subset=["latitude", "longitude", "river_level"])
    return out


def get_river_level(
    latitude: float,
    longitude: float,
    state: str | None = None,
) -> dict[str, Any]:
    best: dict[str, Any] | None = None
    datasets = _river_candidates_for_state(state)

    for dataset in datasets:
        try:
            raw = _download_river_dataset(dataset)

            stations = _extract_station_frame(raw)

            if stations is None or stations.empty:
                continue

            date_col = _find_column(
                raw,
                ["date", "datetime", "timestamp", "time", "observation_date"],
            )

            if date_col:
                parsed = pd.to_datetime(
                    raw[date_col],
                    errors="coerce",
                    utc=True,
                    dayfirst=True,
                )

                stations["_time"] = parsed.iloc[:len(stations)].to_numpy()

                stations = (
                    stations
                    .sort_values("_time")
                    .drop_duplicates(
                        subset=["latitude", "longitude", "station"],
                        keep="last",
                    )
                )

            stations["distance_km"] = stations.apply(
                lambda row: _haversine_km(
                    latitude,
                    longitude,
                    row.latitude,
                    row.longitude,
                ),
                axis=1,
            )

            row = stations.sort_values("distance_km").iloc[0]

            candidate = {
                "river_level": float(row["river_level"]),
                "station_name": str(row["station"]),
                "river_name": str(row["river"]),
                "station_latitude": float(row["latitude"]),
                "station_longitude": float(row["longitude"]),
                "distance_km": round(float(row["distance_km"]), 2),
                "source": dataset["url"],
                "dataset": dataset["name"],
            }

            if best is None or candidate["distance_km"] < best["distance_km"]:
                best = candidate

        except Exception as exc:
            print(
                f"River dataset unavailable: "
                f"{dataset['name']} - {exc}"
            )
            continue

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

def _calculate_slope(latitude: float, longitude: float, elevations: list[float]) -> float:
    # Points are [center, north, south, east, west]. Use ~90 m offsets.
    center, north, south, east, west = elevations
    lat_m = 90.0
    lon_m = 90.0 * max(math.cos(math.radians(latitude)), 0.01)
    dz_dy = (north - south) / (2 * lat_m)
    dz_dx = (east - west) / (2 * lon_m)
    gradient = math.sqrt(dz_dx ** 2 + dz_dy ** 2)
    return round(math.degrees(math.atan(gradient)), 2)


def fetch_environment(latitude: float, longitude: float, state: str | None = None) -> dict[str, Any]:
    # Fetch center + four neighbours in one elevation request.
    lat_offset = 90.0 / 111_320.0
    lon_offset = 90.0 / (111_320.0 * max(math.cos(math.radians(latitude)), 0.01))
    points = [
        (latitude, longitude),
        (latitude + lat_offset, longitude),
        (latitude - lat_offset, longitude),
        (latitude, longitude + lon_offset),
        (latitude, longitude - lon_offset),
    ]

    elevation_data = _get_json(
        ELEVATION_URL,
        {
            "latitude": ",".join(str(p[0]) for p in points),
            "longitude": ",".join(str(p[1]) for p in points),
        },
    )
    elevations = [float(x) for x in elevation_data.get("elevation", [])]
    if len(elevations) != 5:
        raise RuntimeError("Elevation API returned incomplete terrain data")

    weather_data = _get_json(
        SOIL_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "soil_moisture_0_to_7cm",
            "forecast_hours": 1,
            "timezone": "auto",
        },
    )
    hourly = weather_data.get("hourly", {})
    values = hourly.get("soil_moisture_0_to_7cm") or []
    soil_raw = values[0] if values else None
    if soil_raw is None:
        raise RuntimeError("Soil moisture API did not return a value")

    river = get_river_level(latitude, longitude, state)

    return {
        "elevation": round(elevations[0], 2),
        "slope": _calculate_slope(latitude, longitude, elevations),
        "soil_moisture": round(float(soil_raw) * 100.0, 2),
        "river_level": river["river_level"],
        "river_station_name": river["station_name"],
        "river_name": river["river_name"],
        "river_station_latitude": river["station_latitude"],
        "river_station_longitude": river["station_longitude"],
        "river_distance_km": river["distance_km"],
        "river_level_source": river["source"],
        "river_dataset": river["dataset"],
        "river_available": river["available"],
        "sources": {
            "elevation": ELEVATION_URL,
            "soil_moisture": SOIL_URL,
            "slope": "Calculated from Open-Meteo/Copernicus DEM elevations",
            "river_level": river["source"],
        },
    }
