"""Enhanced geocoding: normalize state names, expand city maps, reprocess un-geocoded awards."""
from sqlalchemy import text
from app.database import engine



# Full US state name → abbreviation
STATE_NAMES = {
    'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
    'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
    'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
    'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
    'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
    'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
    'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
    'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
    'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
    'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
    'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
    'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
    'wisconsin': 'WI', 'wyoming': 'WY', 'district of columbia': 'DC',
    'puerto rico': 'PR', 'guam': 'GU', 'virgin islands': 'VI',
}

# State centroids
STATE_CENTROIDS = {
    'AL': (32.806671, -86.791130), 'AK': (61.370716, -152.404419), 'AZ': (33.729759, -111.431221),
    'AR': (34.969704, -92.373123), 'CA': (36.116203, -119.681564), 'CO': (39.059811, -105.311104),
    'CT': (41.597782, -72.755371), 'DE': (39.318523, -75.507141), 'FL': (27.766279, -81.686783),
    'GA': (33.040619, -83.643074), 'HI': (21.094318, -157.498337), 'ID': (44.240459, -114.478828),
    'IL': (40.349457, -88.986137), 'IN': (39.849426, -86.258278), 'IA': (42.011539, -93.210526),
    'KS': (38.526600, -96.726486), 'KY': (37.668140, -84.670067), 'LA': (31.169546, -91.867805),
    'ME': (44.693947, -69.381927), 'MD': (39.063946, -76.802101), 'MA': (42.230171, -71.530106),
    'MI': (43.326618, -84.536095), 'MN': (45.694454, -93.900192), 'MS': (32.741646, -89.678696),
    'MO': (38.456085, -92.288368), 'MT': (46.921925, -110.454353), 'NE': (41.125370, -98.268082),
    'NV': (38.313515, -117.055374), 'NH': (43.452492, -71.563896), 'NJ': (40.298904, -74.521011),
    'NM': (34.840515, -106.248482), 'NY': (42.165726, -74.948051), 'NC': (35.630066, -79.806419),
    'ND': (47.528912, -99.784012), 'OH': (40.388783, -82.764915), 'OK': (35.565342, -96.928917),
    'OR': (44.572021, -122.070938), 'PA': (40.590752, -77.209755), 'RI': (41.680893, -71.511780),
    'SC': (33.856892, -80.945007), 'SD': (44.299782, -99.438828), 'TN': (35.747845, -86.692345),
    'TX': (31.054487, -97.563461), 'UT': (40.150032, -111.862434), 'VT': (44.045876, -72.710686),
    'VA': (37.769337, -78.169968), 'WA': (47.400902, -121.490494), 'WV': (38.491226, -80.954456),
    'WI': (44.268543, -89.616508), 'WY': (42.755966, -107.302490), 'DC': (38.897438, -77.026817),
    'PR': (18.220833, -66.590149),
}

# Expanded NY city coordinates
NY_CITIES = {
    'new york': (40.7128, -74.0060), 'new york city': (40.7128, -74.0060), 'nyc': (40.7128, -74.0060),
    'brooklyn': (40.6782, -73.9442), 'manhattan': (40.7831, -73.9712), 'queens': (40.7282, -73.7949),
    'bronx': (40.8448, -73.8648), 'staten island': (40.5795, -74.1502),
    'albany': (42.6526, -73.7562), 'buffalo': (42.8864, -78.8784), 'rochester': (43.1566, -77.6088),
    'syracuse': (43.0481, -76.1474), 'yonkers': (40.9312, -73.8987), 'white plains': (41.0340, -73.7629),
    'ithaca': (42.4440, -76.5019), 'schenectady': (42.8142, -73.9396), 'troy': (42.7284, -73.6918),
    'utica': (43.1009, -75.2327), 'binghamton': (42.0987, -75.9180), 'poughkeepsie': (41.7004, -73.9209),
    'saratoga springs': (43.0831, -73.7846), 'new rochelle': (40.9115, -73.7824),
    'mount vernon': (40.9126, -73.8371), 'kingston': (41.9268, -73.9974),
    'plattsburgh': (44.6995, -73.4529), 'niagara falls': (43.0962, -79.0377),
    'watertown': (43.9748, -75.9108), 'glen cove': (40.8623, -73.6340),
    'long island city': (40.7447, -73.9485), 'stony brook': (40.9257, -73.1409),
    'farmingdale': (40.7326, -73.4454), 'garden city': (40.7268, -73.6343),
    'hauppauge': (40.8254, -73.2026), 'armonk': (41.1265, -73.7140),
    'tarrytown': (41.0762, -73.8587), 'pearl river': (41.0590, -74.0222),
    'niskayuna': (42.7795, -73.8454), 'menands': (42.6918, -73.7262),
    'west nyack': (41.0962, -73.9729), 'purchase': (41.0410, -73.7154),
    'hawthorne': (41.1073, -73.7968), 'ossining': (41.1626, -73.8618),
    'peekskill': (41.2901, -73.9204), 'dobbs ferry': (41.0137, -73.8718),
    'mount kisco': (41.2045, -73.7271), 'rye': (40.9807, -73.6837),
    'port chester': (41.0018, -73.6657), 'mamaroneck': (40.9487, -73.7354),
}

# Top US city coordinates for matching
US_CITIES = {
    'boston': ('MA', 42.3601, -71.0589), 'cambridge': ('MA', 42.3736, -71.1097),
    'san francisco': ('CA', 37.7749, -122.4194), 'san jose': ('CA', 37.3382, -121.8863),
    'los angeles': ('CA', 34.0522, -118.2437), 'san diego': ('CA', 32.7157, -117.1611),
    'seattle': ('WA', 47.6062, -122.3321), 'portland': ('OR', 45.5152, -122.6784),
    'chicago': ('IL', 41.8781, -87.6298), 'houston': ('TX', 29.7604, -95.3698),
    'austin': ('TX', 30.2672, -97.7431), 'dallas': ('TX', 32.7767, -96.7970),
    'denver': ('CO', 39.7392, -104.9903), 'boulder': ('CO', 40.0150, -105.2705),
    'atlanta': ('GA', 33.7490, -84.3880), 'miami': ('FL', 25.7617, -80.1918),
    'philadelphia': ('PA', 39.9526, -75.1652), 'pittsburgh': ('PA', 40.4406, -79.9959),
    'washington': ('DC', 38.9072, -77.0369), 'baltimore': ('MD', 39.2904, -76.6122),
    'detroit': ('MI', 42.3314, -83.0458), 'ann arbor': ('MI', 42.2808, -83.7430),
    'minneapolis': ('MN', 44.9778, -93.2650), 'madison': ('WI', 43.0731, -89.4012),
    'columbus': ('OH', 39.9612, -82.9988), 'cleveland': ('OH', 41.4993, -81.6944),
    'nashville': ('TN', 36.1627, -86.7816), 'raleigh': ('NC', 35.7796, -78.6382),
    'durham': ('NC', 35.9940, -78.8986), 'charlotte': ('NC', 35.2271, -80.8431),
    'salt lake city': ('UT', 40.7608, -111.8910), 'phoenix': ('AZ', 33.4484, -112.0740),
    'tucson': ('AZ', 32.2226, -110.9747), 'las vegas': ('NV', 36.1699, -115.1398),
    'san rafael': ('CA', 37.9735, -122.5311), 'redmond': ('WA', 47.6740, -122.1215),
    'pasadena': ('CA', 34.1478, -118.1445), 'berkeley': ('CA', 37.8716, -122.2727),
    'palo alto': ('CA', 37.4419, -122.1430), 'mountain view': ('CA', 37.3861, -122.0839),
    'sunnyvale': ('CA', 37.3688, -122.0363), 'santa clara': ('CA', 37.3541, -121.9552),
    'irvine': ('CA', 33.6846, -117.8265), 'princeton': ('NJ', 40.3573, -74.6672),
    'new haven': ('CT', 41.3083, -72.9279), 'stanford': ('CA', 37.4275, -122.1697),
    'champaign': ('IL', 40.1164, -88.2434), 'urbana': ('IL', 40.1106, -88.2073),
    'state college': ('PA', 40.7934, -77.8600), 'college park': ('MD', 38.9897, -76.9378),
    'blacksburg': ('VA', 37.2296, -80.4139), 'west lafayette': ('IN', 40.4259, -86.9081),
    'gainesville': ('FL', 29.6516, -82.3248), 'knoxville': ('TN', 35.9606, -83.9207),
}


def normalize_state(state_raw):
    """Normalize state name/abbreviation to 2-letter code."""
    if not state_raw:
        return None
    s = state_raw.strip()
    if len(s) == 2:
        return s.upper() if s.upper() in STATE_CENTROIDS else None
    return STATE_NAMES.get(s.lower())


def geocode_award(city, state_raw):
    """Try to geocode a city/state pair. Returns (lat, lon, method, confidence) or None."""
    city_lower = city.strip().lower() if city else ''
    state = normalize_state(state_raw)
    
    # 1. NY city exact match
    if city_lower in NY_CITIES:
        lat, lon = NY_CITIES[city_lower]
        return lat, lon, 'ny_city_match', 0.9
    
    # 2. US city database match (verify state if available)
    if city_lower in US_CITIES:
        expected_state, lat, lon = US_CITIES[city_lower]
        if not state or state == expected_state:
            return lat, lon, 'us_city_match', 0.85
    
    # 3. State centroid fallback
    if state and state in STATE_CENTROIDS:
        lat, lon = STATE_CENTROIDS[state]
        return lat, lon, 'state_centroid', 0.3
    
    return None


def main():
    with engine.begin() as conn:
        # First, normalize full state names → abbreviations
        print("=== State Name Normalization ===")
        state_updates = 0
        cur_states = conn.execute(text("SELECT id, recipient_state FROM awards WHERE recipient_state IS NOT NULL AND LENGTH(recipient_state) > 2")).fetchall()
        for row in cur_states:
            aid, raw = row[0], row[1]
            norm = normalize_state(raw)
            if norm:
                conn.execute(text("UPDATE awards SET recipient_state = :norm WHERE id = :aid"), {"norm": norm, "aid": aid})
                state_updates += 1
        print(f"Normalized {state_updates} state names to abbreviations")
        
        # Now geocode all awards with city but no lat/lon
        print("\n=== Geocoding Awards ===")
        ungeo = conn.execute(text("""
            SELECT id, recipient_city, recipient_state 
            FROM awards 
            WHERE latitude IS NULL AND recipient_city IS NOT NULL AND recipient_city != ''
        """)).fetchall()
        
        print(f"Processing {len(ungeo)} awards with city but no geocode")
        
        results = {'ny_city_match': 0, 'us_city_match': 0, 'state_centroid': 0, 'failed': 0}
        updates = []
        
        for aid, city, state in ungeo:
            geo = geocode_award(city, state)
            if geo:
                lat, lon, method, confidence = geo
                updates.append({
                    "lat": lat, "lon": lon, "method": method, 
                    "confidence": confidence, "aid": aid
                })
                results[method] = results.get(method, 0) + 1
            else:
                results['failed'] += 1
        
        if updates:
            update_sql = text("""
                UPDATE awards SET latitude = :lat, longitude = :lon, geocode_method = :method, geocode_confidence = :confidence
                WHERE id = :aid
            """)
            batch_size = 2000
            for i in range(0, len(updates), batch_size):
                conn.execute(update_sql, updates[i:i + batch_size])

        # Report
        print(f"\nResults:")
        for method, count in sorted(results.items(), key=lambda x: -x[1]):
            print(f"  {method}: {count}")
        
        # NYSERDA coverage check
        nyserda = conn.execute(text("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN latitude IS NOT NULL THEN 1 ELSE 0 END) as geocoded
            FROM awards WHERE agency = 'NYSERDA'
        """)).fetchone()
        tot_ny = nyserda[0] or 1
        geo_ny = nyserda[1] or 0
        print(f"\nNYSERDA coverage: {geo_ny}/{tot_ny} ({geo_ny*100//tot_ny}%)")
        
        total = conn.execute(text("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN latitude IS NOT NULL THEN 1 ELSE 0 END) as geocoded
            FROM awards
        """)).fetchone()
        tot_all = total[0] or 1
        geo_all = total[1] or 0
        print(f"Overall coverage: {geo_all}/{tot_all} ({geo_all*100//tot_all}%)")
        
    print("\nDone.")


if __name__ == "__main__":
    main()

