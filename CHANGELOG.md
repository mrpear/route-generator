# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-03-15

### Changed
- **Tier thresholds adjusted** for better distribution: Premium ≥80 (was ≥85), Good ≥65 (was ≥75), Acceptable ≥50 (was ≥60), Poor <50 (was <60)
- **Smoothness scoring updated** based on OSM wiki standards: `smoothness=bad` now scores 13 points (was 10), as mountain bikes are acceptable for gravel cycling
- **Default minimum length** reduced from 500m to 100m to include short premium connectors and fire access roads

### Added
- Support for gravel residential roads (gravel, fine_gravel, compacted surfaces only)
- Emergency access roads with good smoothness (`service=emergency_access`)
- Detailed smoothness descriptions based on OSM wiki (excellent=roller skates, good=racing bikes, bad=mountain bikes, etc.)
- 676 quality rural gravel streets to dataset

### Fixed
- Exclude concrete:plates and other paved variants using regex filtering (`surface!~"paved|asphalt|concrete|chipseal|metal"`)
- Exclude poorly tagged generic 'unpaved' residential roads to improve quality
- OSM 130404871 (concrete plates) now correctly excluded
- OSM 186200281 (emergency access) now included with score 65
- OSM 1099423412 (175m grade1 forest road) now included with score 87

### Dataset (50km around Wrocław)
- Total: 5,253 roads (8,882 found, filtered by length)
- Premium: 345 roads (up from 79)
- Good: 3,388 roads (up from 787)
- Acceptable: 1,500 roads
- Poor: 20 roads
- Total length: 2,526.5 km
- Average score: 68.4

## [0.3.0] - 2026-03-15

### Changed
- **Default minimum length** lowered from 500m to 100m
- **Smoothness scoring**: `smoothness=bad` now scores 13 points (suitable for gravel bikes)
- Explicitly filter out paved surfaces (paved/asphalt/concrete)

### Added
- Emergency access service roads with good smoothness
- Short premium connectors and forest emergency access roads

### Dataset (50km around Wrocław)
- Total: 4,738 roads (up from 1,521)
- Premium: 324 roads (up from 129)
- Average score: 68.2 (up from 67.9)

### Examples
- OSM 1099423412: 175m grade1 forest road, score 87
- OSM 186200281: 308m emergency access, smoothness=good, score 65

## [0.2.0] - 2026-03-15

### Changed
- **Minimum length** threshold lowered to include shorter fire access roads

### Added
- 1,241 additional roads, including shorter fire access roads ("Dojazd pożarowy")

### Dataset (50km around Wrocław)
- Total: 2,762 roads (up from 1,521)
- Premium: 204 roads (up from 129)
- Total length: 2,088.7 km (up from 1,651 km)

### Examples
- OSM 186355200 now included (0.48km, score 81)

## [0.1.1] - 2026-03-15

### Added
- GitHub Pages deployment with interactive Wrocław map demo
- Live demo available at https://mrpear.github.io/route-generator/

## [0.1.0] - 2026-03-15

### Added
- Initial release: Gravel Road Finder tool
- **Smart scoring system** (0-100 points) based on:
  - Surface quality (25 pts): fine_gravel > gravel > compacted > ground > unpaved > dirt
  - Maintenance/tracktype (25 pts): grade1 > grade2 > grade3 > grade4 > grade5
  - Smoothness (20 pts): excellent > good > intermediate > bad > rough > very_bad
  - Traffic level (15 pts): path > track+forestry > track+yes
  - Width (10 pts): ≥3m > 2-3m > <2m
  - Access (5 pts): bicycle=yes > access=yes > permissive > private
- **Interactive heat map** visualization (red=premium, blue=poor)
- **Multiple export formats**: GeoJSON, CSV, HTML
- **Quality filters**: bad smoothness gets lower scores, minimum length filtering
- Automatic output directory naming from location
- Command-line interface with argparse

### Tech Stack
- Python 3.10+
- overpy (Overpass API client)
- folium (interactive maps)
- geojson (GeoJSON handling)
- shapely (geometry operations)

### Initial Dataset (50km around Wrocław, Poland)
- Total: 1,521 roads
- Premium: 129 roads
- Good: 1,224 roads
- Acceptable: 160 roads
- Total length: 1,651 km
