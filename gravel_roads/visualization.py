"""Generate interactive maps for gravel roads."""

import folium
from pathlib import Path


def create_interactive_map(
    roads: list[dict],
    center: tuple[float, float],
    output_path: str
) -> None:
    """
    Generate interactive Folium map with color-coded road segments.

    Args:
        roads: List of roads with scoring data
        center: (latitude, longitude) tuple for map center
        output_path: Path to save HTML file
    """
    # Create base map
    m = folium.Map(
        location=center,
        zoom_start=11,
        tiles='OpenStreetMap'
    )

    # Add alternative tile layers
    folium.TileLayer('OpenTopoMap', name='Topo Map').add_to(m)

    # Color mapping by tier - Heat map (red=hot/best, blue=cold/worst)
    tier_colors = {
        'Premium': '#FF0000',    # Red (hot/best)
        'Good': '#FF8800',       # Orange (warm)
        'Acceptable': '#FFDD00', # Yellow (cool)
        'Poor': '#0088FF',       # Blue (cold/worst)
    }

    # Add roads to map
    for road in roads:
        tier = road['premium_tier']
        color = tier_colors.get(tier, '#888888')

        # Create popup content
        name = road['name'] or f"Unnamed road (OSM {road['id']})"
        breakdown = road['score_breakdown']

        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 13px; min-width: 200px;">
            <h4 style="margin: 0 0 8px 0;">{name}</h4>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td><b>Score:</b></td><td>{road['premium_score']} pts ({tier})</td></tr>
                <tr><td><b>Length:</b></td><td>{road['length_km']} km</td></tr>
                <tr><td colspan="2" style="padding-top: 8px;"><b>Properties:</b></td></tr>
                <tr><td>Surface:</td><td>{road['surface']}</td></tr>
                <tr><td>Tracktype:</td><td>{road['tracktype'] or 'N/A'}</td></tr>
                <tr><td>Smoothness:</td><td>{road['smoothness'] or 'N/A'}</td></tr>
                <tr><td>Width:</td><td>{road['width'] or 'N/A'} m</td></tr>
                <tr><td colspan="2" style="padding-top: 8px;"><b>Score Breakdown:</b></td></tr>
                <tr><td>Surface:</td><td>{breakdown['surface']}/25</td></tr>
                <tr><td>Tracktype:</td><td>{breakdown['tracktype']}/25</td></tr>
                <tr><td>Smoothness:</td><td>{breakdown['smoothness']}/20</td></tr>
                <tr><td>Traffic:</td><td>{breakdown['traffic']}/15</td></tr>
                <tr><td>Width:</td><td>{breakdown['width']}/10</td></tr>
                <tr><td>Access:</td><td>{breakdown['access']}/5</td></tr>
            </table>
            <p style="margin: 8px 0 0 0; font-size: 11px;">
                <a href="https://www.openstreetmap.org/way/{road['id']}" target="_blank">
                    View on OpenStreetMap
                </a>
            </p>
        </div>
        """

        # Add road as polyline
        folium.PolyLine(
            locations=road['coordinates'],
            color=color,
            weight=5,
            opacity=0.9,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{name} ({tier}, {road['premium_score']} pts)"
        ).add_to(m)

    # Add legend
    legend_html = f"""
    <div style="position: fixed;
                bottom: 50px; right: 50px; width: 160px; height: 140px;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:14px; padding: 10px; border-radius: 5px;">
        <p style="margin: 0 0 8px 0; font-weight: bold;">Road Quality</p>
        <p style="margin: 4px 0;"><span style="color: {tier_colors['Premium']}; font-size: 20px;">●</span> Premium (80-100)</p>
        <p style="margin: 4px 0;"><span style="color: {tier_colors['Good']}; font-size: 20px;">●</span> Good (65-79)</p>
        <p style="margin: 4px 0;"><span style="color: {tier_colors['Acceptable']}; font-size: 20px;">●</span> Acceptable (50-64)</p>
        <p style="margin: 4px 0;"><span style="color: {tier_colors['Poor']}; font-size: 20px;">●</span> Poor (<50)</p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Add layer control
    folium.LayerControl().add_to(m)

    # Save map
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    m.save(output_path)
