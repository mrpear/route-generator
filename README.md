# Gravel Road Finder

Discover premium gravel cycling roads using OpenStreetMap data. Built for finding the best unpaved routes around Wrocław, Poland, but works anywhere in the world.

![Example Map](https://img.shields.io/badge/OSM-Data-green) ![Python](https://img.shields.io/badge/python-3.10%2B-blue)

**[🗺️ View Live Demo: Wrocław Gravel Roads](https://mrpear.github.io/route-generator/)**

## Features

- 🗺️ **OpenStreetMap Integration** - Query unpaved roads with gravel surfaces
- ⭐ **Smart Scoring** - Rate roads 0-100 based on surface quality, maintenance, smoothness, traffic, and more
- 🎨 **Interactive Maps** - Color-coded Folium maps with detailed popups (heat map: red=best, blue=worst)
- 📊 **Multiple Formats** - Export to GeoJSON, CSV, and HTML
- 🔍 **Advanced Filtering** - Filter by score, tier, length, and quality
- 🏆 **Quality Scoring** - Roads with rough surfaces get lower scores automatically
- 📍 **Example Dataset** - Includes 2,762 gravel roads around Wrocław (ready to explore)

## Quick Start

```bash
# Install dependencies
poetry install

# Search for gravel roads around Wrocław (default: 50km radius, 250m minimum)
poetry run python find_gravel_roads.py --name wroclaw

# View the interactive map
open output/wroclaw/gravel_roads.html
```

## Example Results (Wrocław, 50km radius)

The repository includes a pre-generated example dataset in `output/wroclaw/`:

```
Found: 8,386 roads (within 50km)
Filtered: 2,762 roads (≥ 250m length)
  Premium (80-100): 204 roads
  Good (60-79): 2,225 roads
  Acceptable (50-59): 315 roads
  Poor (<50): 18 roads
Total length: 2,088.7 km
Average score: 67.7
```

## Scoring Methodology

Each road is scored 0-100 points across six categories:

### Surface Quality (25 points)
- **fine_gravel**: 25 pts - Finest quality gravel
- **gravel**: 22 pts - Standard gravel (premium target)
- **compacted**: 20 pts - Well-compacted surface
- **ground**: 15 pts - Natural ground surface
- **unpaved**: 12 pts - Generic unpaved
- **dirt**: 10 pts - Dirt/earth surface

### Maintenance/Tracktype (25 points)
Based on OSM tracktype grade:
- **grade1**: 25 pts - Paved or heavily compacted
- **grade2**: 23 pts - **Target grade** - well-maintained unpaved
- **grade3**: 15 pts - Moderate surface irregularities
- **unknown**: 15 pts - Assumed moderate
- **grade4**: 8 pts - Rough surface
- **grade5**: 3 pts - Very rough, barely passable

### Smoothness (20 points)
- **excellent**: 20 pts
- **good**: 18 pts
- **intermediate**: 15 pts
- **unknown**: 12 pts (assumed moderate)
- **bad**: 10 pts
- **rough**: 8 pts
- **very_bad/very_rough**: 5 pts
- **horrible**: 3 pts
- **very_horrible**: 1 pt
- **impassable**: 0 pts

### Traffic Level (15 points)
- **Bicycle-only paths**: 14 pts - No motor vehicles
- **Path**: 15 pts - Minimal vehicle traffic
- **Track/Service (forestry/agricultural)**: 12 pts - Low traffic
- **Track/Service (general access)**: 10 pts - Moderate traffic

### Width (10 points)
- **≥3m**: 10 pts - Comfortable for bikes
- **2-3m**: 8 pts - Moderate width
- **unknown**: 7 pts
- **<2m**: 5 pts - Narrow

### Access (5 points)
- **bicycle=designated/yes**: 5 pts
- **access=yes**: 5 pts
- **access=permissive**: 3 pts
- **access=private**: 0 pts

## Tier Classification

- 🔴 **Premium** (80-100): Excellent surface, well-maintained, low traffic
- 🟠 **Good** (60-79): Good surface, rideable, some traffic
- 🟡 **Acceptable** (50-59): Passable but may be rough or narrow
- 🔵 **Poor** (<50): Not recommended

## Usage

### Basic Search
```bash
# Default search (50km radius, 250m minimum length)
poetry run python find_gravel_roads.py

# Custom location and radius
poetry run python find_gravel_roads.py --center 52.2297,21.0122 --radius 30
```

### Filtering
```bash
# Only premium roads (score ≥80)
poetry run python find_gravel_roads.py --min-score 80

# Minimum length 2km
poetry run python find_gravel_roads.py --min-length 2.0

# Combine filters
poetry run python find_gravel_roads.py --min-score 70 --min-length 1.0 --tier Premium,Good

# Large area search with extended timeout
poetry run python find_gravel_roads.py --radius 100 --timeout 300
```

### Export Options
```bash
# Named output (creates output/wroclaw/)
poetry run python find_gravel_roads.py --name wroclaw

# Custom output directory (full path override)
poetry run python find_gravel_roads.py --output-dir custom/path/here

# Specific formats only
poetry run python find_gravel_roads.py --formats geojson,html
```

## Output Files

### GeoJSON (`gravel_roads.geojson`)
Standard GeoJSON format with LineString geometries and comprehensive properties:
- OSM tags (surface, tracktype, smoothness, etc.)
- Calculated metrics (length, score, tier)
- Score breakdown by category

Compatible with QGIS, ArcGIS, and other GIS software.

### CSV (`gravel_roads.csv`)
Tabular format with columns:
- Road properties: `osm_id`, `name`, `surface`, `tracktype`, `smoothness`, `width`, `length_km`
- Scoring: `premium_score`, `premium_tier`
- Location: `start_lat`, `start_lon`, `end_lat`, `end_lon`
- Score breakdown: `score_surface`, `score_tracktype`, etc.

### HTML Map (`gravel_roads.html`)
Interactive Folium map with:
- Color-coded road segments by tier (red=Premium, orange=Good, yellow=Acceptable, blue=Poor)
- Clickable popups with detailed road information and score breakdown
- Links to OpenStreetMap for each road
- Toggle between OpenStreetMap and OpenTopoMap base layers
- Legend showing tier colors and score ranges

## How It Works

1. **Query OSM** - Uses Overpass API to find roads matching:
   - `highway=track` with gravel/compacted surfaces
   - `highway=path` with gravel surfaces
   - `highway=service` with gravel surfaces (forest cycling paths, bike-only routes)
   - Well-maintained unpaved roads (`tracktype=grade1/grade2`)

2. **Score Roads** - Analyzes OSM tags to calculate quality scores (roads with rough surfaces get lower scores)

3. **Filter** - Removes roads with:
   - Length below minimum (default 250m)

4. **Export** - Generates interactive maps and data files

## Target Roads

The finder focuses on:
- 🌲 Forest service roads
- 🚒 Fire access roads ("Dojazd pożarowy" in Polish)
- 🚴 Dedicated cycling paths with gravel surfaces
- 🛤️ Well-maintained agricultural tracks
- 🌳 Bicycle-only forest paths

## Example Roads

### Premium Road: OSM Way 188500514
- **Location**: Wrocław area (2.65 km)
- **Type**: Forest cycling path (highway=service)
- **Surface**: compacted, tracktype: grade2, smoothness: good
- **Access**: bicycle=yes, motor_vehicle=no
- **Score**: 87 (Premium)

### Premium Road: Way 865631511
- **Name**: "Dojazd pożarowy nr 6"
- **Tags**: highway=track, surface=gravel, tracktype=grade2
- **Expected Score**: ~87 (Premium)

### Fire Access Road: Way 237161394
- **Tags**: highway=track, surface=compacted, tracktype=grade2, smoothness=intermediate
- **Expected Score**: ~85 (Premium)

## Tips for Finding Premium Routes

1. **Target tracktype=grade2** - Well-maintained unpaved roads, ideal for gravel cycling
2. **Look for forestry roads** - Often tagged `access=forestry`, typically well-maintained
3. **Fire access roads** - Named "Dojazd pożarowy" in Polish, usually high quality
4. **Check surface tags** - `fine_gravel` and `compacted` are premium surfaces
5. **Filter by length** - Use `--min-length 1.0` for roads suitable for route planning

## Project Structure

```
route-generator/
├── find_gravel_roads.py          # Main CLI script
├── gravel_roads/                  # Package directory
│   ├── __init__.py
│   ├── osm_query.py              # OSM Overpass API queries
│   ├── scoring.py                # Premium scoring algorithm
│   ├── storage.py                # GeoJSON/CSV export
│   └── visualization.py          # Folium map generation
└── output/                       # Output directories
    ├── .gitkeep                  # Tracked in git
    └── wroclaw/                  # Example dataset (included in repo)
        ├── gravel_roads.geojson  # 2,762 roads, 5.3 MB
        ├── gravel_roads.csv      # Tabular data, 308 KB
        └── gravel_roads.html     # Interactive map, 8.3 MB
```

## Requirements

- Python 3.10+
- Dependencies (installed via Poetry):
  - **overpy** - OSM Overpass API client
  - **folium** - Interactive web maps
  - **geojson** - GeoJSON format handling
  - **shapely** - Geometry operations

Optional dependencies for satellite imagery (Phase 2):
```bash
poetry install --extras satellite
```

## Troubleshooting

### Overpass API Timeout
If you get timeout errors with large search areas:
```bash
poetry run python find_gravel_roads.py --radius 100 --timeout 300
```

### No Roads Found
- Verify center coordinates are correct (latitude, longitude format)
- Try increasing search radius
- Check if the area has gravel roads tagged in OSM

### Empty Map
- Ensure roads were found and passed filters
- Check browser console for JavaScript errors
- Try regenerating: `poetry run python find_gravel_roads.py --formats html`

## Limitations

- **Data quality** - OSM tagging completeness varies by area
- **No real-time conditions** - Weather, maintenance status not reflected
- **Surface assumptions** - Scoring based on tags, not actual inspection
- **No elevation data** - Climb difficulty not considered (future enhancement)

## Future Enhancements

- **Elevation profiles** - Integrate elevation data for climb analysis
- **Route generation** - Create GPX routes connecting premium segments
- **Strava heatmap overlay** - Identify popular segments
- **Satellite imagery verification** - Visual quality verification (Phase 2)
- **ML surface classification** - When training data becomes available
- **Crowdsourced ratings** - Community quality ratings

## Contributing

Contributions welcome! To customize:

1. **Modify scoring weights** - Edit `gravel_roads/scoring.py`
2. **Change OSM query** - Update `gravel_roads/osm_query.py`
3. **Add export formats** - Extend `gravel_roads/storage.py`
4. **Customize map style** - Modify `gravel_roads/visualization.py`

## License

MIT License - feel free to use for discovering gravel roads anywhere in the world!

## Credits

Built with OpenStreetMap data © OpenStreetMap contributors
