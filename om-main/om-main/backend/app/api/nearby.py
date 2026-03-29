from math import atan2, cos, radians, sin, sqrt

import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/nearby", tags=["Nearby Shops"])

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
]
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
USER_AGENT = "AgenticPharmacy/1.0"


def _km_distance(lat1, lon1, lat2, lon2):
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c


def _extract_address(tags: dict) -> str:
    address_parts = [
        tags.get("addr:housenumber"),
        tags.get("addr:street"),
        tags.get("addr:suburb"),
        tags.get("addr:city"),
    ]
    return ", ".join([part for part in address_parts if part]) or tags.get("addr:full", "")


def _normalize_overpass_shop(el: dict, lat: float, lng: float) -> dict | None:
    tags = el.get("tags", {})
    center = el.get("center") or {}
    s_lat = el.get("lat", center.get("lat"))
    s_lng = el.get("lon", center.get("lon"))
    if s_lat is None or s_lng is None:
        return None
    distance_km = _km_distance(lat, lng, float(s_lat), float(s_lng))
    return {
        "id": el.get("id"),
        "name": tags.get("name") or "Pharmacy",
        "address": _extract_address(tags),
        "lat": float(s_lat),
        "lng": float(s_lng),
        "distance_km": distance_km,
        "source": "overpass",
    }


def _normalize_nominatim_shop(item: dict, lat: float, lng: float, idx: int) -> dict | None:
    try:
        s_lat = float(item.get("lat"))
        s_lng = float(item.get("lon"))
    except Exception:
        return None
    return {
        "id": item.get("place_id") or f"nominatim-{idx}",
        "name": item.get("display_name", "Pharmacy").split(",")[0],
        "address": item.get("display_name") or "",
        "lat": s_lat,
        "lng": s_lng,
        "distance_km": _km_distance(lat, lng, s_lat, s_lng),
        "source": "nominatim",
    }


async def _fetch_overpass_shops(lat: float, lng: float, radius: int) -> tuple[list[dict], list[str]]:
    query = f"""
    [out:json][timeout:20];
    (
      node["amenity"="pharmacy"](around:{radius},{lat},{lng});
      way["amenity"="pharmacy"](around:{radius},{lat},{lng});
      relation["amenity"="pharmacy"](around:{radius},{lat},{lng});
    );
    out center 30;
    """
    headers = {"User-Agent": USER_AGENT}
    errors: list[str] = []

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        for url in OVERPASS_URLS:
            try:
                resp = await client.post(url, data=query, headers=headers)
                if resp.status_code != 200:
                    errors.append(f"{url} returned HTTP {resp.status_code}")
                    continue
                data = resp.json()
                shops = []
                for el in data.get("elements", []):
                    shop = _normalize_overpass_shop(el, lat, lng)
                    if shop:
                        shops.append(shop)
                if shops:
                    return shops, errors
                return [], errors
            except Exception as exc:
                errors.append(f"{url} failed: {str(exc)}")

    return [], errors


async def _fetch_nominatim_shops(lat: float, lng: float, radius: int) -> tuple[list[dict], str | None]:
    # Approximate radius to bounding box degrees.
    lat_delta = radius / 111000
    lng_delta = radius / max(1, int(111000 * max(0.2, cos(radians(lat)))))
    params = {
        "q": "pharmacy",
        "format": "jsonv2",
        "limit": 30,
        "addressdetails": 1,
        "bounded": 1,
        "viewbox": f"{lng - lng_delta},{lat + lat_delta},{lng + lng_delta},{lat - lat_delta}",
    }
    headers = {"User-Agent": USER_AGENT}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(NOMINATIM_URL, params=params, headers=headers)
            if resp.status_code != 200:
                return [], f"Nominatim returned HTTP {resp.status_code}"
            data = resp.json()
    except Exception as exc:
        return [], str(exc)

    shops = []
    for idx, item in enumerate(data or []):
        shop = _normalize_nominatim_shop(item, lat, lng, idx)
        if shop:
            shops.append(shop)
    return shops, None


@router.get("/shops")
async def nearby_shops(lat: float, lng: float, radius: int = 3000):
    shops, overpass_errors = await _fetch_overpass_shops(lat, lng, radius)
    if not shops:
        shops, nominatim_error = await _fetch_nominatim_shops(lat, lng, radius)
        if not shops:
            details = "; ".join(overpass_errors[:2]) if overpass_errors else ""
            if nominatim_error:
                details = f"{details}; Nominatim fallback failed: {nominatim_error}".strip("; ")
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch nearby shops. {details}".strip(),
            )

    shops.sort(key=lambda x: x["distance_km"])
    return {"shops": shops[:30]}


@router.get("/geocode")
async def geocode(query: str, limit: int = 5):
    q = (query or "").strip()
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Please provide a longer location query.")

    if limit < 1:
        limit = 1
    if limit > 10:
        limit = 10

    params = {
        "q": q,
        "format": "jsonv2",
        "limit": limit,
        "addressdetails": 1,
    }
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(NOMINATIM_URL, params=params, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to geocode location")
        data = resp.json()

    places = []
    for item in data or []:
        try:
            lat = float(item.get("lat"))
            lng = float(item.get("lon"))
        except Exception:
            continue
        places.append(
            {
                "display_name": item.get("display_name") or "Unknown place",
                "lat": lat,
                "lng": lng,
            }
        )

    return {"places": places}


@router.get("/reverse")
async def reverse_geocode(lat: float, lng: float):
    params = {
        "lat": lat,
        "lon": lng,
        "format": "jsonv2",
        "addressdetails": 1,
    }
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(NOMINATIM_REVERSE_URL, params=params, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to reverse geocode location")
        data = resp.json()

    display_name = data.get("display_name") or f"{lat:.6f}, {lng:.6f}"
    return {
        "display_name": display_name,
        "lat": lat,
        "lng": lng,
    }


@router.get("/route")
async def route(lat: float, lng: float, shop_lat: float, shop_lng: float):
    url = f"{OSRM_URL}/{lng},{lat};{shop_lng},{shop_lat}"
    params = {"overview": "full", "geometries": "geojson"}
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to fetch route")
        data = resp.json()

    routes = data.get("routes") or []
    if not routes:
        raise HTTPException(status_code=404, detail="No route found")
    coords = routes[0]["geometry"]["coordinates"]
    latlng = [[c[1], c[0]] for c in coords]
    return {"route": latlng, "distance_m": routes[0].get("distance")}
