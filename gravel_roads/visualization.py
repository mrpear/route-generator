"""Generate interactive maps for gravel roads."""

import folium
from pathlib import Path
from datetime import datetime
from . import __version__


def create_interactive_map(
    roads: list[dict],
    center: tuple[float, float],
    output_path: str
) -> None:
    """
    Generate interactive Folium map that loads GeoJSON data separately.

    Args:
        roads: List of roads with scoring data (used for stats only)
        center: (latitude, longitude) tuple for map center
        output_path: Path to save HTML file
    """
    # Create base map with OpenStreetMap only
    m = folium.Map(
        location=center,
        zoom_start=11,
        tiles='OpenStreetMap'
    )

    # Heat map colors - hot (best) to cool (worst) - ColorBrewer accessible
    tier_colors = {
        'Premium': '#D81B60',    # Magenta (hot/best)
        'Good': '#FF6F00',       # Vivid Orange
        'Acceptable': '#FDD835', # Bright Yellow
        'Poor': '#1976D2',       # Deep Blue (cool/worst)
    }

    # Add legend with version and creation time
    creation_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    legend_html = f"""
    <div style="position: fixed;
                bottom: 50px; right: 50px; width: 180px; height: 180px;
                background-color: rgba(255, 255, 255, 0.95); border: 2px solid #333;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); z-index: 9999;
                font-size: 14px; padding: 10px; border-radius: 5px;">
        <p style="margin: 0 0 8px 0; font-weight: bold;">Road Quality</p>
        <p style="margin: 4px 0;"><span style="color: {tier_colors['Premium']}; font-size: 20px;">●</span> Premium (80-100)</p>
        <p style="margin: 4px 0;"><span style="color: {tier_colors['Good']}; font-size: 20px;">●</span> Good (65-79)</p>
        <p style="margin: 4px 0;"><span style="color: {tier_colors['Acceptable']}; font-size: 20px;">●</span> Acceptable (50-64)</p>
        <p style="margin: 4px 0;"><span style="color: {tier_colors['Poor']}; font-size: 20px;">●</span> Poor (<50)</p>
        <hr style="margin: 8px 0; border: none; border-top: 1px solid #ccc;">
        <p style="margin: 4px 0; font-size: 11px; color: #666;">Generated: {creation_time}</p>
        <p style="margin: 4px 0; font-size: 11px; color: #666;">Version: {__version__}</p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # JavaScript to load and display GeoJSON
    geojson_script = f"""
    <script>
    // Load GeoJSON data
    fetch('gravel_roads.geojson')
        .then(response => response.json())
        .then(data => {{
            // Color mapping by tier
            const tierColors = {{
                'Premium': '{tier_colors["Premium"]}',
                'Good': '{tier_colors["Good"]}',
                'Acceptable': '{tier_colors["Acceptable"]}',
                'Poor': '{tier_colors["Poor"]}'
            }};

            // Add GeoJSON layer
            L.geoJSON(data, {{
                style: function(feature) {{
                    const tier = feature.properties.premium_tier;
                    return {{
                        color: tierColors[tier] || '#888888',
                        weight: 4,
                        opacity: 0.5
                    }};
                }},
                onEachFeature: function(feature, layer) {{
                    const props = feature.properties;
                    const name = props.name || `Unnamed road (OSM ${{props.osm_id}})`;
                    const breakdown = props.score_breakdown;

                    // Create popup
                    const popupContent = `
                        <div style="font-family: Arial, sans-serif; font-size: 13px; min-width: 200px;">
                            <h4 style="margin: 0 0 8px 0;">${{name}}</h4>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr><td><b>Score:</b></td><td>${{props.premium_score}} pts (${{props.premium_tier}})</td></tr>
                                <tr><td><b>Length:</b></td><td>${{props.length_km}} km</td></tr>
                                <tr><td colspan="2" style="padding-top: 8px;"><b>Properties:</b></td></tr>
                                <tr><td>Surface:</td><td>${{props.surface}}</td></tr>
                                <tr><td>Tracktype:</td><td>${{props.tracktype || 'N/A'}}</td></tr>
                                <tr><td>Smoothness:</td><td>${{props.smoothness || 'N/A'}}</td></tr>
                                <tr><td>Width:</td><td>${{props.width || 'N/A'}} m</td></tr>
                                <tr><td colspan="2" style="padding-top: 8px;"><b>Score Breakdown:</b></td></tr>
                                <tr><td>Surface:</td><td>${{breakdown.surface}}/25</td></tr>
                                <tr><td>Tracktype:</td><td>${{breakdown.tracktype}}/25</td></tr>
                                <tr><td>Smoothness:</td><td>${{breakdown.smoothness}}/20</td></tr>
                                <tr><td>Traffic:</td><td>${{breakdown.traffic}}/15</td></tr>
                                <tr><td>Width:</td><td>${{breakdown.width}}/10</td></tr>
                                <tr><td>Access:</td><td>${{breakdown.access}}/5</td></tr>
                            </table>
                            <p style="margin: 8px 0 0 0; font-size: 11px;">
                                <a href="https://www.openstreetmap.org/way/${{props.osm_id}}" target="_blank">
                                    View on OpenStreetMap
                                </a>
                            </p>
                        </div>
                    `;

                    layer.bindPopup(popupContent, {{maxWidth: 300}});
                    layer.bindTooltip(`${{name}} (${{props.premium_tier}}, ${{props.premium_score}} pts)`);
                }}
            }}).addTo({m.get_name()});
        }})
        .catch(error => console.error('Error loading GeoJSON:', error));
    </script>
    """
    m.get_root().html.add_child(folium.Element(geojson_script))

    # Save map
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    m.save(output_path)
