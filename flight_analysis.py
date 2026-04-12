#!/usr/bin/env python3
"""
Flight Pattern Analysis Pipeline
Geospatial flight trajectory clustering and movement pattern recognition

Run: python flight_analysis.py

Outputs:
- flight_tracks.csv
- flight_tracks.geojson
- flight_tracks.kml
- flight_map.html (interactive map)
- analytics.csv

Built by Dwight Pagán | Geospatial Data Science
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

# Try to import optional dependencies
try:
    import folium
    from folium.plugins import HeatMap
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False
    print("⚠️ folium not installed. Run: pip install folium")

try:
    import geopandas as gpd
    from shapely.geometry import Point
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False
    print("⚠️ geopandas not installed. Run: pip install geopandas")

try:
    from sklearn.cluster import DBSCAN
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import simplekml
    HAS_KML = True
except ImportError:
    HAS_KML = False

# =============================================================================
# CONFIGURATION
# =============================================================================

REGION = {
    'name': 'Mid-Atlantic Region',
    'center_lat': 38.0,
    'center_lon': -77.0,
}

REFERENCE_POINTS = {
    'Dulles Airport (IAD)': (38.9531, -77.4565),
    'Baltimore (BWI)': (39.1754, -76.6683),
    'Washington National (DCA)': (38.8512, -77.0402),
    'Richmond (RIC)': (37.5052, -77.3197),
    'Norfolk (ORF)': (36.8946, -76.2012),
    'Hagerstown (HGR)': (39.7080, -77.7611),
    'Salisbury (SBY)': (38.3390, -75.5103),
}

AIRCRAFT_COLORS = {
    'Cessna 172': '#3b82f6',
    'King Air 350': '#10b981',
    'Learjet 75': '#f59e0b',
    'Dash-8 Q400': '#8b5cf6',
}

# =============================================================================
# DATA GENERATION
# =============================================================================

def generate_flight_tracks(num_points=100, seed=42):
    """Generate synthetic ADS-B style tracks for regional aircraft."""
    np.random.seed(seed)
    start_time = datetime.utcnow()
    
    aircraft = [
        ('Cessna 172', 'N172A', 39.0, -77.5, 0.015, (3000, 7000), 'holding'),
        ('Cessna 172', 'N172B', 38.5, -76.5, 0.012, (2500, 5500), 'survey'),
        ('King Air 350', 'N350A', 39.2, -77.0, 0.04, (15000, 22000), 'transit'),
        ('King Air 350', 'N350B', 37.5, -76.0, 0.03, (18000, 25000), 'racetrack'),
        ('Learjet 75', 'N75A', 38.0, -78.0, 0.06, (30000, 41000), 'transit'),
        ('Learjet 75', 'N75B', 37.0, -75.0, 0.05, (28000, 40000), 'racetrack'),
        ('Dash-8 Q400', 'N400A', 38.5, -77.5, 0.025, (12000, 18000), 'holding'),
        ('Dash-8 Q400', 'N400B', 36.5, -76.5, 0.02, (10000, 16000), 'transit'),
    ]
    
    data = []
    
    for ac_type, tail, base_lat, base_lon, variance, alt_range, pattern in aircraft:
        for i in range(num_points):
            t = i / 10.0
            
            if pattern == 'holding':
                lat = base_lat + variance * np.sin(t) + np.random.normal(0, 0.005)
                lon = base_lon + variance * np.cos(t) + np.random.normal(0, 0.005)
                heading = (np.degrees(np.arctan2(np.cos(t), -np.sin(t))) + 360) % 360
            elif pattern == 'transit':
                lat = base_lat + i * 0.015 + np.random.normal(0, 0.005)
                lon = base_lon + i * 0.012 + np.random.normal(0, 0.005)
                heading = 45 + np.random.normal(0, 5)
            elif pattern == 'survey':
                phase = (i % 20) / 20.0 * 2 * np.pi
                lat = base_lat + variance * np.sin(phase) + np.random.normal(0, 0.003)
                lon = base_lon + 0.08 * ((phase / np.pi) if phase < np.pi else (2 - phase / np.pi))
                heading = 90 if phase < np.pi else 270
            elif pattern == 'racetrack':
                phase = (i % 40) / 40.0 * 2 * np.pi
                lat = base_lat + variance * np.sin(phase)
                lon = base_lon + 0.1 * (phase / np.pi if phase < np.pi else 2 - phase / np.pi)
                heading = 90 if phase < np.pi else 270
            
            altitude = np.random.randint(alt_range[0], alt_range[1])
            base_speed = {'Cessna 172': 110, 'King Air 350': 260, 'Learjet 75': 420, 'Dash-8 Q400': 300}
            speed = base_speed[ac_type] + np.random.randint(-15, 15)
            
            timestamp = start_time + timedelta(minutes=i * 2)
            
            data.append({
                'Timestamp': timestamp,
                'Aircraft_Type': ac_type,
                'Tail_Number': tail,
                'Latitude': round(lat, 6),
                'Longitude': round(lon, 6),
                'Altitude_ft': altitude,
                'Heading': round(heading, 1),
                'Speed_kts': speed,
                'Pattern': pattern,
            })
    
    return pd.DataFrame(data)


def analyze_tracks(df):
    """Calculate fleet statistics and flight analytics."""
    fleet_stats = df.groupby('Aircraft_Type')['Tail_Number'].nunique().reset_index(name='Active_Aircraft')
    
    analytics = df.groupby(['Aircraft_Type', 'Tail_Number']).agg(
        First_Seen=('Timestamp', 'min'),
        Last_Seen=('Timestamp', 'max'),
        Data_Points=('Timestamp', 'count'),
        Avg_Altitude=('Altitude_ft', 'mean'),
        Avg_Speed=('Speed_kts', 'mean'),
    ).reset_index()
    
    analytics['Flight_Duration_Hours'] = (
        analytics['Last_Seen'] - analytics['First_Seen']
    ).dt.total_seconds() / 3600
    
    return fleet_stats, analytics


def detect_concentration_areas(df):
    """Use DBSCAN to detect flight concentration areas."""
    if not HAS_SKLEARN:
        return pd.DataFrame()
    
    coords = df[['Latitude', 'Longitude']].values
    clustering = DBSCAN(eps=0.3, min_samples=10).fit(coords)
    df_copy = df.copy()
    df_copy['Cluster'] = clustering.labels_
    
    concentration_areas = df_copy[df_copy['Cluster'] >= 0].groupby('Cluster').agg(
        Center_Lat=('Latitude', 'mean'),
        Center_Lon=('Longitude', 'mean'),
        Data_Points=('Cluster', 'count'),
    ).reset_index()
    
    return concentration_areas


def create_map(df, concentration_areas):
    """Create interactive Folium map."""
    if not HAS_FOLIUM:
        return None
    
    m = folium.Map(
        location=[REGION['center_lat'], REGION['center_lon']],
        zoom_start=7,
        tiles='CartoDB dark_matter',
    )
    
    # Reference airports/points
    for name, (lat, lon) in REFERENCE_POINTS.items():
        folium.Marker(
            [lat, lon],
            popup=f"<b>{name}</b>",
            icon=folium.Icon(color='blue', prefix='fa', icon='plane'),
        ).add_to(m)
    
    # Flight tracks
    for tail in df['Tail_Number'].unique():
        track_df = df[df['Tail_Number'] == tail].sort_values('Timestamp')
        ac_type = track_df['Aircraft_Type'].iloc[0]
        
        points = track_df[['Latitude', 'Longitude']].values.tolist()
        folium.PolyLine(
            points,
            weight=2,
            color=AIRCRAFT_COLORS.get(ac_type, '#ffffff'),
            opacity=0.7,
        ).add_to(m)
        
        last = track_df.iloc[-1]
        folium.CircleMarker(
            [last['Latitude'], last['Longitude']],
            radius=6,
            color=AIRCRAFT_COLORS.get(ac_type, '#ffffff'),
            fill=True,
            popup=f"{ac_type} {tail}",
        ).add_to(m)
    
    # Concentration area circles
    for _, area in concentration_areas.iterrows():
        folium.Circle(
            [area['Center_Lat'], area['Center_Lon']],
            radius=30000,
            color='#ff00ff',
            fill=True,
            fillOpacity=0.1,
        ).add_to(m)
    
    return m


def export_data(df, analytics, m):
    """Export all data formats."""
    os.makedirs('output', exist_ok=True)
    
    df.to_csv('output/flight_tracks.csv', index=False)
    print('✅ Saved: output/flight_tracks.csv')
    
    analytics.to_csv('output/analytics.csv', index=False)
    print('✅ Saved: output/analytics.csv')
    
    if HAS_GEOPANDAS:
        geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
        gdf = gpd.GeoDataFrame(df.copy(), geometry=geometry, crs='EPSG:4326')
        gdf['Timestamp'] = gdf['Timestamp'].astype(str)
        gdf.to_file('output/flight_tracks.geojson', driver='GeoJSON')
        print('✅ Saved: output/flight_tracks.geojson')
    
    if HAS_KML:
        kml = simplekml.Kml()
        for tail in df['Tail_Number'].unique():
            track_df = df[df['Tail_Number'] == tail].sort_values('Timestamp')
            ac_type = track_df['Aircraft_Type'].iloc[0]
            coords = [(row['Longitude'], row['Latitude'], row['Altitude_ft'] * 0.3048)
                      for _, row in track_df.iterrows()]
            line = kml.newlinestring(name=f"{ac_type} {tail}")
            line.coords = coords
            line.altitudemode = simplekml.AltitudeMode.absolute
        kml.save('output/flight_tracks.kml')
        print('✅ Saved: output/flight_tracks.kml')
    
    if m:
        m.save('output/flight_map.html')
        print('✅ Saved: output/flight_map.html')


def main():
    print("=" * 50)
    print("✈️  FLIGHT PATTERN ANALYSIS")
    print("   Geospatial Trajectory Clustering")
    print("=" * 50)
    
    # Generate data
    print("\n📡 Generating synthetic flight tracks...")
    df = generate_flight_tracks(num_points=100)
    print(f"   Generated {len(df)} track points")
    print(f"   Aircraft types: {df['Aircraft_Type'].unique().tolist()}")
    
    # Analyze
    print("\n📊 Analyzing flight data...")
    fleet_stats, analytics = analyze_tracks(df)
    print("\nFleet Composition:")
    print(fleet_stats.to_string(index=False))
    
    print("\nFlight Analytics:")
    print(analytics[['Aircraft_Type', 'Tail_Number', 'Flight_Duration_Hours']].to_string(index=False))
    
    # Detect concentration areas
    print("\n🎯 Detecting concentration areas...")
    concentration_areas = detect_concentration_areas(df)
    if len(concentration_areas) > 0:
        print(f"   Found {len(concentration_areas)} concentration areas")
    
    # Create map
    print("\n🗺️  Creating interactive map...")
    m = create_map(df, concentration_areas)
    
    # Export
    print("\n💾 Exporting data...")
    export_data(df, analytics, m)
    
    print("\n" + "=" * 50)
    print("✅ COMPLETE! Open output/flight_map.html in your browser.")
    print("=" * 50)


if __name__ == '__main__':
    main()
