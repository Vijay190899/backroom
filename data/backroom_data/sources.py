"""Open-data sources, each cached under data/raw/ and each with an offline fallback.

The demo must never depend on a third-party download working at deploy time
(docs/DATA.md): every fetch either reads its cache, downloads once and caches, or
returns None so the caller falls back to seeded synthetic data.
"""

import http.client
import json
import math
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from typing import Any

MAVEN_URL = "https://maven-datasets.s3.amazonaws.com/Coffee+Shop+Sales/Coffee+Shop+Sales.zip"
BONN = {"latitude": 50.73, "longitude": 7.10, "timezone": "Europe/Berlin"}
_DAILY = "precipitation_sum,temperature_2m_max,temperature_2m_min"
_TIMEOUT_S = 30


def _fetch(url: str) -> bytes | None:
    try:
        with urllib.request.urlopen(url, timeout=_TIMEOUT_S) as resp:
            return resp.read()
    except (urllib.error.URLError, http.client.HTTPException, TimeoutError, OSError):
        return None


def cached(path: Path, url: str, *, offline: bool) -> bytes | None:
    """The cached file, or a fresh download (then cached), or None."""
    if path.exists():
        return path.read_bytes()
    if offline:
        return None
    body = _fetch(url)
    if body is not None:
        # Write then rename, so an interrupted download never leaves a half file cached.
        path.parent.mkdir(parents=True, exist_ok=True)
        partial = path.with_suffix(path.suffix + ".part")
        partial.write_bytes(body)
        os.replace(partial, path)
    return body


def maven_zip(raw: Path, *, offline: bool) -> Path | None:
    path = raw / "coffee_shop_sales.zip"
    return path if cached(path, MAVEN_URL, offline=offline) is not None else None


# --- weather ------------------------------------------------------------------------------


def weather(
    raw: Path, start: date, end: date, today: date, *, offline: bool
) -> list[dict[str, Any]]:
    """Daily Bonn weather from start to end: archive where it exists, forecast after.

    Returns [] when nothing could be fetched (the caller then synthesises)."""
    out: dict[date, dict[str, Any]] = {}
    archive_end = min(end, today - timedelta(days=1))
    if start <= archive_end:
        query = urllib.parse.urlencode(
            {**BONN, "start_date": start, "end_date": archive_end, "daily": _DAILY}
        )
        name = f"weather_archive_{start}_{archive_end}.json"
        url = f"https://archive-api.open-meteo.com/v1/archive?{query}"
        out.update(_parse_daily(cached(raw / name, url, offline=offline), "archive"))
    # The archive lags a few days; the forecast API (it also serves recent past days)
    # fills the rest, by explicit date range so the cache file matches its contents.
    fc_start = max(start, today - timedelta(days=14))
    query = urllib.parse.urlencode(
        {**BONN, "daily": _DAILY, "start_date": fc_start, "end_date": end}
    )
    forecast = cached(
        raw / f"weather_forecast_{fc_start}_{end}.json",
        f"https://api.open-meteo.com/v1/forecast?{query}",
        offline=offline,
    )
    for day, row in _parse_daily(forecast, "forecast").items():
        if start <= day <= end and (day not in out or out[day]["precip_mm"] is None):
            out[day] = row
    return [out[d] for d in sorted(out) if out[d]["precip_mm"] is not None]


def _parse_daily(body: bytes | None, source: str) -> dict[date, dict[str, Any]]:
    if body is None:
        return {}
    try:
        daily = json.loads(body)["daily"]
        if not {"time", "precipitation_sum"} <= set(daily):
            return {}
    except (KeyError, ValueError, TypeError):
        return {}
    out: dict[date, dict[str, Any]] = {}
    for i, day in enumerate(daily["time"]):
        precip = daily["precipitation_sum"][i]
        out[date.fromisoformat(day)] = {
            "date": date.fromisoformat(day),
            "precip_mm": None if precip is None else float(precip),
            "tmax_c": daily["temperature_2m_max"][i],
            "tmin_c": daily["temperature_2m_min"][i],
            "source": source,
        }
    return out


# --- holidays ---------------------------------------------------------------------------------


def holidays(raw: Path, years: list[int], *, offline: bool) -> list[dict[str, Any]]:
    """NRW public holidays from Nager.Date, or the computed list when offline."""
    out: list[dict[str, Any]] = []
    for year in years:
        body = cached(
            raw / f"holidays_DE_{year}.json",
            f"https://date.nager.at/api/v3/PublicHolidays/{year}/DE",
            offline=offline,
        )
        try:
            entries = json.loads(body) if body is not None else None
            if entries is not None and not isinstance(entries, list):
                entries = None
        except ValueError:
            entries = None
        if entries is None:
            out += computed_nrw_holidays(year)
            continue
        for e in entries:
            counties = e.get("counties")
            if counties is None or "DE-NW" in counties:
                out.append(
                    {"date": date.fromisoformat(e["date"]), "name": e["name"], "source": "nager"}
                )
    return sorted(out, key=lambda h: h["date"])


def easter(year: int) -> date:
    """Gregorian Easter Sunday (anonymous Gregorian algorithm)."""
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7  # noqa: E741 (the algorithm's own name)
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = (h + l - 7 * m + 114) % 31 + 1
    return date(year, month, day)


def computed_nrw_holidays(year: int) -> list[dict[str, Any]]:
    e = easter(year)
    fixed = [
        (date(year, 1, 1), "New Year's Day"),
        (date(year, 5, 1), "Labour Day"),
        (date(year, 10, 3), "German Unity Day"),
        (date(year, 11, 1), "All Saints' Day"),
        (date(year, 12, 25), "Christmas Day"),
        (date(year, 12, 26), "St. Stephen's Day"),
    ]
    moving = [
        (e - timedelta(days=2), "Good Friday"),
        (e + timedelta(days=1), "Easter Monday"),
        (e + timedelta(days=39), "Ascension Day"),
        (e + timedelta(days=50), "Whit Monday"),
        (e + timedelta(days=60), "Corpus Christi"),
    ]
    return sorted(
        ({"date": d, "name": n, "source": "computed"} for d, n in fixed + moving),
        key=lambda h: h["date"],
    )


def synthetic_weather(start: date, end: date, seed: int) -> list[dict[str, Any]]:
    """Seeded stand-in when Open-Meteo is unreachable: plausible Bonn autumn/summer."""
    import random

    rng = random.Random(f"weather:{seed}")
    out: list[dict[str, Any]] = []
    day = start
    while day <= end:
        season = math.cos((day.timetuple().tm_yday - 200) / 365 * 2 * math.pi)
        rainy = rng.random() < 0.38
        out.append(
            {
                "date": day,
                "precip_mm": round(rng.uniform(1.0, 12.0), 1) if rainy else 0.0,
                "tmax_c": round(14 + 9 * season + rng.uniform(-3, 3), 1),
                "tmin_c": round(6 + 7 * season + rng.uniform(-3, 3), 1),
                "source": "synthetic",
            }
        )
        day += timedelta(days=1)
    return out
