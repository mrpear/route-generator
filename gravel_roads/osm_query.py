"""Query OpenStreetMap for gravel roads using Overpass API."""

import overpy
from math import radians, cos, sin, asin, sqrt


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in km using Haversine formula."""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return c * 6371  # Earth radius in km


def calculate_length(coordinates: list[tuple[float, float]]) -> float:
    """Calculate total length of a path from coordinates in km."""
    total = 0.0
    for i in range(len(coordinates) - 1):
        lat1, lon1 = coordinates[i]
        lat2, lon2 = coordinates[i + 1]
        total += haversine_distance(lat1, lon1, lat2, lon2)
    return total


def get_gravel_roads(
    center: tuple[float, float],
    radius_km: float = 50,
    timeout: int = 180
) -> list[dict]:
    """
    Query Overpass API for gravel roads around a center point.

    Args:
        center: (latitude, longitude) tuple for search center
        radius_km: Search radius in kilometers
        timeout: Overpass API timeout in seconds

    Returns:
        List of road segment dictionaries with OSM data and calculated properties
    """
    lat, lon = center
    radius_m = radius_km * 1000

    # Overpass QL query for gravel roads
    # Focus on highway=track/path/service with gravel-like surfaces and good tracktype grades
    query = f"""
    [out:json][timeout:{timeout}];
    (
      // Tracks with explicit gravel surfaces
      way(around:{radius_m},{lat},{lon})
        ["highway"="track"]
        ["surface"~"^(gravel|fine_gravel|compacted|ground)$"];

      // Tracks with grade1/grade2 (well-maintained unpaved)
      way(around:{radius_m},{lat},{lon})
        ["highway"="track"]
        ["tracktype"~"^grade[12]$"]
        ["surface"!~"paved|asphalt|concrete|chipseal|metal"];

      // Paths with gravel surfaces (some forest paths are high quality)
      way(around:{radius_m},{lat},{lon})
        ["highway"="path"]
        ["surface"~"^(gravel|fine_gravel|compacted)$"]
        ["bicycle"!="no"];

      // Service roads with gravel surfaces (forest service roads, cycling paths)
      way(around:{radius_m},{lat},{lon})
        ["highway"="service"]
        ["surface"~"^(gravel|fine_gravel|compacted|ground)$"]
        ["bicycle"!="no"];

      // Service roads with grade1/grade2 (well-maintained unpaved)
      way(around:{radius_m},{lat},{lon})
        ["highway"="service"]
        ["tracktype"~"^grade[12]$"]
        ["surface"!~"paved|asphalt|concrete|chipseal|metal"]
        ["bicycle"!="no"];

      // Emergency access roads with good smoothness (assume unpaved unless explicitly paved)
      way(around:{radius_m},{lat},{lon})
        ["highway"="service"]
        ["service"="emergency_access"]
        ["smoothness"~"^(excellent|good|intermediate)$"]
        ["surface"!~"paved|asphalt|concrete|chipseal|metal"];

      // Gravel residential roads (rural gravel streets)
      way(around:{radius_m},{lat},{lon})
        ["highway"="residential"]
        ["surface"~"^(gravel|fine_gravel|compacted)$"];
    );
    out body;
    >;
    out skel qt;
    """

    api = overpy.Overpass()
    result = api.query(query)

    roads = []
    for way in result.ways:
        # Extract coordinates
        coordinates = [(float(node.lat), float(node.lon)) for node in way.nodes]

        if len(coordinates) < 2:
            continue  # Skip invalid ways

        # Calculate length
        length_km = calculate_length(coordinates)

        # Extract OSM tags
        tags = way.tags

        road = {
            'id': way.id,
            'name': tags.get('name'),
            'coordinates': coordinates,
            'length_km': round(length_km, 2),
            'surface': tags.get('surface', 'unknown'),
            'tracktype': tags.get('tracktype'),
            'smoothness': tags.get('smoothness'),
            'width': _parse_width(tags.get('width')),
            'access': tags.get('access', 'yes'),
            'bicycle': tags.get('bicycle', 'yes'),
            'highway': tags.get('highway'),
            'tags': dict(tags),
        }

        roads.append(road)

    return roads


def _parse_width(width_str: str | None) -> float | None:
    """Parse width tag to float (handles formats like '3', '3.5', '3 m')."""
    if not width_str:
        return None

    try:
        # Remove common suffixes
        width_str = width_str.lower().replace('m', '').replace('meters', '').strip()
        return float(width_str)
    except (ValueError, AttributeError):
        return None
