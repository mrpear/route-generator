#!/usr/bin/env python3
"""
Find premium gravel roads for cycling around a given location.

Uses OpenStreetMap data to identify and rate unpaved roads suitable for gravel cycling.
"""

import argparse
import sys
from pathlib import Path

from gravel_roads.osm_query import get_gravel_roads
from gravel_roads.scoring import calculate_premium_score
from gravel_roads.storage import save_geojson, save_csv
from gravel_roads.visualization import create_interactive_map


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Find premium gravel cycling roads using OpenStreetMap data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search around Wroclaw (default 25km radius)
  python find_gravel_roads.py --center 51.1079,17.0385

  # Custom area with larger radius
  python find_gravel_roads.py --center 51.1079,17.0385 --radius 50

  # Filter for premium roads only
  python find_gravel_roads.py --min-score 80 --tier Premium

  # Filter by minimum length (roads >= 2km)
  python find_gravel_roads.py --min-length 2.0

  # Named output directory
  python find_gravel_roads.py --name wroclaw --formats geojson,csv,html
        """
    )

    parser.add_argument(
        '--center',
        type=str,
        default='51.1079,17.0385',
        help='Search center as "latitude,longitude" (default: Wroclaw)'
    )

    parser.add_argument(
        '--radius',
        type=float,
        default=25.0,
        help='Search radius in kilometers (default: 25)'
    )

    parser.add_argument(
        '--min-score',
        type=int,
        default=0,
        help='Minimum premium score (0-100, default: 0)'
    )

    parser.add_argument(
        '--tier',
        type=str,
        help='Filter by tier (comma-separated): Premium,Good,Acceptable,Poor'
    )

    parser.add_argument(
        '--min-length',
        type=float,
        default=0.1,
        help='Minimum road length in kilometers (default: 0.1)'
    )

    parser.add_argument(
        '--name',
        type=str,
        default=None,
        help='Name for output directory (e.g., "wroclaw"). If not specified, uses lat_lon_rRadius format'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Full output directory path (overrides --name, default: output/[name or lat_lon_rRadius])'
    )

    parser.add_argument(
        '--formats',
        type=str,
        default='geojson,csv,html',
        help='Output formats (comma-separated): geojson,csv,html (default: all)'
    )

    parser.add_argument(
        '--timeout',
        type=int,
        default=180,
        help='Overpass API timeout in seconds (default: 180)'
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Parse center coordinates
    try:
        lat, lon = map(float, args.center.split(','))
        center = (lat, lon)
    except ValueError:
        print(f"Error: Invalid center format '{args.center}'. Use 'latitude,longitude'")
        sys.exit(1)

    # Parse tier filter
    tier_filter = None
    if args.tier:
        tier_filter = [t.strip() for t in args.tier.split(',')]

    # Parse output formats
    formats = [f.strip().lower() for f in args.formats.split(',')]

    # Generate output directory
    if args.output_dir is not None:
        # Full path explicitly provided
        output_dir = args.output_dir
    elif args.name is not None:
        # Name provided, use output/name/
        output_dir = f"output/{args.name}"
    else:
        # Auto-generate from location: output/lat_lon_rRadius/
        output_dir = f"output/{center[0]:.4f}_{center[1]:.4f}_r{int(args.radius)}"

    print(f"Searching for gravel roads...")
    print(f"  Center: {center[0]:.4f}, {center[1]:.4f}")
    print(f"  Radius: {args.radius} km")
    print(f"  Min length: {args.min_length} km")
    print(f"  Timeout: {args.timeout}s")
    print(f"  Output: {output_dir}")

    # Query OpenStreetMap
    try:
        roads = get_gravel_roads(center, args.radius, timeout=args.timeout)
        print(f"\nFound {len(roads)} roads")
    except Exception as e:
        print(f"Error querying OpenStreetMap: {e}")
        sys.exit(1)

    if not roads:
        print("No gravel roads found in the specified area.")
        sys.exit(0)

    # Score each road
    print("Calculating premium scores...")
    for road in roads:
        score_data = calculate_premium_score(road)
        road['premium_score'] = score_data['total_score']
        road['premium_tier'] = score_data['tier']
        road['score_breakdown'] = score_data['breakdown']

    # Filter by length, score, and tier
    original_count = len(roads)

    if args.min_length > 0:
        roads = [r for r in roads if r['length_km'] >= args.min_length]
        print(f"Filtered by min length {args.min_length} km: {len(roads)}/{original_count} roads")

    if args.min_score > 0:
        roads = [r for r in roads if r['premium_score'] >= args.min_score]
        print(f"Filtered by min score {args.min_score}: {len(roads)}/{original_count} roads")

    if tier_filter:
        roads = [r for r in roads if r['premium_tier'] in tier_filter]
        print(f"Filtered by tier {','.join(tier_filter)}: {len(roads)}/{original_count} roads")

    if not roads:
        print("No roads match the filter criteria.")
        sys.exit(0)

    # Sort by score (descending)
    roads.sort(key=lambda r: r['premium_score'], reverse=True)

    # Print summary statistics
    print(f"\n=== Summary Statistics ===")
    print(f"Total roads: {len(roads)}")

    tier_counts = {}
    for road in roads:
        tier = road['premium_tier']
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    for tier in ['Premium', 'Good', 'Acceptable', 'Poor']:
        count = tier_counts.get(tier, 0)
        if count > 0:
            print(f"  {tier}: {count}")

    total_length = sum(r['length_km'] for r in roads)
    avg_score = sum(r['premium_score'] for r in roads) / len(roads)
    print(f"Total length: {total_length:.1f} km")
    print(f"Average score: {avg_score:.1f}")

    # Top 5 roads
    print(f"\n=== Top 5 Roads ===")
    for i, road in enumerate(roads[:5], 1):
        name = road['name'] or f"Unnamed (OSM {road['id']})"
        print(f"{i}. {name}")
        print(f"   Score: {road['premium_score']} ({road['premium_tier']}) | "
              f"Length: {road['length_km']} km | "
              f"Surface: {road['surface']}")

    # Export data
    output_path = Path(output_dir)
    print(f"\n=== Exporting Data to {output_path} ===")

    if 'geojson' in formats:
        geojson_path = output_path / 'gravel_roads.geojson'
        save_geojson(roads, str(geojson_path))
        print(f"  GeoJSON: {geojson_path}")

    if 'csv' in formats:
        csv_path = output_path / 'gravel_roads.csv'
        save_csv(roads, str(csv_path))
        print(f"  CSV: {csv_path}")

    if 'html' in formats:
        html_path = output_path / 'gravel_roads.html'
        print(f"  Generating interactive map...")
        create_interactive_map(roads, center, str(html_path))
        print(f"  HTML Map: {html_path}")

    print(f"\nDone! Open {output_path}/gravel_roads.html in a browser to view the map.")


if __name__ == '__main__':
    main()
