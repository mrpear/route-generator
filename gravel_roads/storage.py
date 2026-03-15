"""Export gravel road catalog in multiple formats."""

import json
import csv
import geojson
from pathlib import Path


def save_geojson(roads: list[dict], filepath: str) -> None:
    """
    Export roads to GeoJSON format.

    Args:
        roads: List of roads with scoring data
        filepath: Output file path
    """
    features = []

    for road in roads:
        # Convert coordinates from (lat, lon) to (lon, lat) for GeoJSON
        coords_geojson = [[lon, lat] for lat, lon in road['coordinates']]

        feature = geojson.Feature(
            geometry=geojson.LineString(coords_geojson),
            properties={
                'osm_id': road['id'],
                'name': road['name'],
                'surface': road['surface'],
                'tracktype': road['tracktype'],
                'smoothness': road['smoothness'],
                'width': road['width'],
                'length_km': road['length_km'],
                'premium_score': road['premium_score'],
                'premium_tier': road['premium_tier'],
                'score_breakdown': road['score_breakdown'],
                'access': road['access'],
                'bicycle': road['bicycle'],
                'highway': road['highway'],
            }
        )
        features.append(feature)

    feature_collection = geojson.FeatureCollection(features)

    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        geojson.dump(feature_collection, f, indent=2)


def save_csv(roads: list[dict], filepath: str) -> None:
    """
    Export roads to CSV format.

    Args:
        roads: List of roads with scoring data
        filepath: Output file path
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', newline='') as f:
        fieldnames = [
            'osm_id', 'name', 'surface', 'tracktype', 'smoothness',
            'width', 'length_km', 'premium_score', 'premium_tier',
            'access', 'bicycle', 'highway',
            'start_lat', 'start_lon', 'end_lat', 'end_lon',
            'score_surface', 'score_tracktype', 'score_smoothness',
            'score_traffic', 'score_width', 'score_access',
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for road in roads:
            # Get start and end coordinates
            start_lat, start_lon = road['coordinates'][0]
            end_lat, end_lon = road['coordinates'][-1]

            row = {
                'osm_id': road['id'],
                'name': road['name'] or '',
                'surface': road['surface'],
                'tracktype': road['tracktype'] or '',
                'smoothness': road['smoothness'] or '',
                'width': road['width'] or '',
                'length_km': road['length_km'],
                'premium_score': road['premium_score'],
                'premium_tier': road['premium_tier'],
                'access': road['access'],
                'bicycle': road['bicycle'],
                'highway': road['highway'],
                'start_lat': round(start_lat, 6),
                'start_lon': round(start_lon, 6),
                'end_lat': round(end_lat, 6),
                'end_lon': round(end_lon, 6),
                'score_surface': road['score_breakdown']['surface'],
                'score_tracktype': road['score_breakdown']['tracktype'],
                'score_smoothness': road['score_breakdown']['smoothness'],
                'score_traffic': road['score_breakdown']['traffic'],
                'score_width': road['score_breakdown']['width'],
                'score_access': road['score_breakdown']['access'],
            }
            writer.writerow(row)
