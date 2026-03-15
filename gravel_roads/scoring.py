"""Premium gravel road scoring algorithm."""


def calculate_premium_score(road: dict) -> dict:
    """
    Calculate premium score for a gravel road (0-100 points).

    Scoring criteria:
    - Surface quality (25 pts): fine_gravel > gravel > compacted > ground > unpaved > dirt
    - Maintenance/tracktype (25 pts): grade1 > grade2 > grade3 > unknown > grade4 > grade5
    - Smoothness (20 pts): excellent > good > intermediate > unknown > rough
    - Traffic level (15 pts): path > track+forestry > track+yes > other
    - Width (10 pts): >=3m > 2-3m > unknown > <2m
    - Access (5 pts): bicycle=yes > access=yes > permissive > private

    Args:
        road: Road segment dictionary from osm_query.get_gravel_roads()

    Returns:
        Dictionary with total_score, tier, and breakdown
    """
    # Surface quality (25 points)
    surface_scores = {
        'fine_gravel': 25,
        'gravel': 22,
        'compacted': 20,
        'ground': 15,
        'unpaved': 12,
        'dirt': 10,
        'unknown': 10,
    }
    surface_score = surface_scores.get(road['surface'], 10)

    # Maintenance/tracktype (25 points)
    tracktype_scores = {
        'grade1': 25,
        'grade2': 23,  # Target grade - well-maintained unpaved
        'grade3': 15,
        None: 15,  # Unknown, assume moderate
        'grade4': 8,
        'grade5': 3,
    }
    tracktype_score = tracktype_scores.get(road['tracktype'], 15)

    # Smoothness (20 points)
    smoothness_scores = {
        'excellent': 20,
        'good': 18,
        'intermediate': 15,
        None: 12,  # Unknown
        'bad': 10,
        'rough': 8,
        'very_bad': 5,
        'very_rough': 5,
        'horrible': 3,
        'very_horrible': 1,
        'impassable': 0,
    }
    smoothness_score = smoothness_scores.get(road['smoothness'], 12)

    # Traffic level (15 points)
    highway = road['highway']
    access = road['access']
    bicycle = road['bicycle']

    if highway == 'path':
        traffic_score = 15
    elif highway in ('track', 'service') and access in ('forestry', 'agricultural'):
        traffic_score = 12
    elif highway in ('track', 'service') and bicycle == 'yes' and access == 'no':
        traffic_score = 14  # Bicycle-only service road (no motor vehicles)
    elif highway in ('track', 'service') and access == 'yes':
        traffic_score = 10
    else:
        traffic_score = 8

    # Width (10 points)
    width = road['width']
    if width is None:
        width_score = 7  # Unknown, assume moderate
    elif width >= 3.0:
        width_score = 10
    elif width >= 2.0:
        width_score = 8
    else:
        width_score = 5

    # Access (5 points)
    bicycle = road['bicycle']
    if bicycle in ('designated', 'yes'):
        access_score = 5
    elif access == 'yes':
        access_score = 5
    elif access == 'permissive':
        access_score = 3
    elif access == 'private':
        access_score = 0
    else:
        access_score = 4

    # Total score
    total_score = (
        surface_score +
        tracktype_score +
        smoothness_score +
        traffic_score +
        width_score +
        access_score
    )

    # Determine tier
    if total_score >= 80:
        tier = 'Premium'
    elif total_score >= 60:
        tier = 'Good'
    elif total_score >= 50:
        tier = 'Acceptable'
    else:
        tier = 'Poor'

    return {
        'total_score': total_score,
        'tier': tier,
        'breakdown': {
            'surface': surface_score,
            'tracktype': tracktype_score,
            'smoothness': smoothness_score,
            'traffic': traffic_score,
            'width': width_score,
            'access': access_score,
        }
    }
