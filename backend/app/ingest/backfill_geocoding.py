from sqlalchemy import text
from app.database import engine

# Simplified state centroids map
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
    'VA': (37.769337, -78.169968), 'WA': (47.400902, -121.490494), 'WV': (38.491222, -80.954453),
    'WI': (44.268543, -89.616508), 'WY': (42.755966, -107.302490), 'DC': (38.907192, -77.036873)
}


def main():
    print("Phase 4: Geocoding Backfill")
    with engine.begin() as conn:
        # 2. Build map from already geocoded awards
        cur_geo = conn.execute(text("""
            SELECT recipient_city, recipient_state, latitude, longitude 
            FROM awards 
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        """))
        city_coords = {}
        for row in cur_geo.fetchall():
            city = row[0].strip().upper() if row[0] else ''
            state = row[1].strip().upper() if row[1] else ''
            if city and state:
                if (city, state) not in city_coords:
                    city_coords[(city, state)] = (row[2], row[3])

        # Set existing ones to 'original' if not set
        conn.execute(text("UPDATE awards SET geocode_method = 'original' WHERE latitude IS NOT NULL AND geocode_method IS NULL"))

        # 3. Process un-geocoded awards
        cur_ungeo = conn.execute(text("SELECT id, recipient_city, recipient_state FROM awards WHERE latitude IS NULL"))
        ungeocoded = cur_ungeo.fetchall()
        
        geocoded_count = 0
        updates = []
        for award in ungeocoded:
            aw_id, raw_city, raw_state = award[0], award[1], award[2]
            city = raw_city.strip().upper() if raw_city else ''
            state = raw_state.strip().upper() if raw_state else ''
            
            lat, lon, method = None, None, None
            
            if city and state and (city, state) in city_coords:
                lat, lon = city_coords[(city, state)]
                method = 'city_match'
            elif state and state in STATE_CENTROIDS:
                lat, lon = STATE_CENTROIDS[state]
                method = 'state_centroid'
            
            if lat and lon:
                updates.append({"lat": lat, "lon": lon, "method": method, "id": aw_id})
                geocoded_count += 1

        if updates:
            update_sql = text("""
                UPDATE awards 
                SET latitude = :lat, longitude = :lon, geocode_method = :method 
                WHERE id = :id
            """)
            batch_size = 2000
            for i in range(0, len(updates), batch_size):
                conn.execute(update_sql, updates[i:i + batch_size])

        print(f"Awards successfully geocoded via backfill: {geocoded_count} / {len(ungeocoded)}")


if __name__ == '__main__':
    main()

