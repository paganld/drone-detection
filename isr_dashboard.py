#!/usr/bin/env python3
"""
ISR Intelligence Dashboard - Iran/Gulf Region
Airborne Swarm Deconfliction & Intelligence Analysis

Run: python isr_dashboard.py

Outputs:
- isr_tracks.csv
- isr_tracks.geojson  
- isr_tracks.kml
- isr_map.html (interactive map)
- tos_analytics.csv

Built by Cleo | March 2026
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
    'name': 'Iran / Gulf Region',
    'center_lat': 32.0,
    'center_lon': 53.0,
}

STRATEGIC_POINTS = {
    'Strait of Hormuz': (26.5667, 56.2500),
    'Tehran': (35.6892, 51.3890),
    'Bandar Abbas': (27.1832, 56.2666),
    'Isfahan (Nuclear)': (32.6546, 51.6680),
    'Natanz (Nuclear)': (33.7250, 51.7167),
    'Bushehr (Nuclear)': (28.9684, 50.8385),
    'Al Udeid (US)': (25.1173, 51.3150),
    'Al Dhafra (US)': (24.2481, 54.5476),
    'Bahrain NAVCENT': (26.2285, 50.5860),
}

COLORS = {
    'MQ-9': '#ff4444',
    'RC-135': '#44ff44',
    'RQ-4': '#4444ff',
    'P-8': '#ffff44',
}

# =============================================================================
# DATA GENERATION
# =============================================================================

def generate_isr_tracks(num_points=100, seed=42):
    """Generate synthetic ADS-B style tracks for ISR platforms."""
    np.random.seed(seed)
    start_time = datetime.utcnow()
    
    platforms = [
        ('MQ-9', 'T101', 32.5, 53.5, 0.02, (18000, 25000), 'loiter'),
        ('MQ-9', 'T102', 27.0, 56.5, 0.015, (20000, 25000), 'loiter'),
        ('RC-135', 'R201', 33.0, 52.0, 0.08, (28000, 35000), 'orbit'),
        ('RC-135', 'R202', 28.5, 58.0, 0.06, (30000, 35000), 'orbit'),
        ('RQ-4', 'G301', 31.0, 55.0, 0.05, (55000, 60000), 'transit'),
        ('RQ-4', 'G302', 35.0, 50.0, 0.04, (55000, 60000), 'racetrack'),
        ('P-8', 'P401', 26.0, 57.0, 0.03, (15000, 25000), 'maritime'),
        ('P-8', 'P402', 25.5, 54.0, 0.025, (18000, 28000), 'maritime'),
    ]
    
    data = []
    
    for platform, tail, base_lat, base_lon, variance, alt_range, pattern in platforms:
        for i in range(num_points):
            t = i / 10.0
            
            if pattern == 'loiter':
                lat = base_lat + variance * np.sin(t) + np.random.normal(0, 0.005)
                lon = base_lon + variance * np.cos(t) + np.random.normal(0, 0.005)
                heading = (np.degrees(np.arctan2(np.cos(t), -np.sin(t))) + 360) % 360
            elif pattern == 'orbit':
                lat = base_lat + variance * 1.5 * np.sin(t * 0.7) + np.random.normal(0, 0.01)
                lon = base_lon + variance * np.cos(t * 0.7) + np.random.normal(0, 0.01)
                heading = (np.degrees(np.arctan2(np.cos(t * 0.7), -np.sin(t * 0.7) * 1.5)) + 360) % 360
            elif pattern == 'transit':
                lat = base_lat + i * 0.02 + np.random.normal(0, 0.005)
                lon = base_lon + i * 0.015 + np.random.normal(0, 0.005)
                heading = 45 + np.random.normal(0, 5)
            elif pattern == 'racetrack':
                phase = (i % 40) / 40.0 * 2 * np.pi
                lat = base_lat + variance * np.sin(phase)
                lon = base_lon + 0.1 * (phase / np.pi if phase < np.pi else 2 - phase / np.pi)
                heading = 90 if phase < np.pi else 270
            elif pattern == 'maritime':
                leg = i // 10
                pos_in_leg = (i % 10) / 10.0
                directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
                d = directions[leg % 4]
                scale = (leg // 4 + 1) * variance
                lat = base_lat + d[0] * scale * pos_in_leg + np.random.normal(0, 0.003)
                lon = base_lon + d[1] * scale * pos_in_leg + np.random.normal(0, 0.003)
                heading = [90, 0, 270, 180][leg % 4]
            
            altitude = np.random.randint(alt_range[0], alt_range[1])
            speed = {'MQ-9': 180, 'RC-135': 280, 'RQ-4': 340, 'P-8': 320}[platform]
            speed += np.random.randint(-20, 20)
            
            timestamp = start_time + timedelta(minutes=i * 2)
            
            data.append({
                'Timestamp': timestamp,
                'Platform': platform,
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
    """Calculate fleet statistics and time on station."""
    fleet_stats = df.groupby('Platform')['Tail_Number'].nunique().reset_index(name='Active_Aircraft')
    
    tos_stats = df.groupby(['Platform', 'Tail_Number']).agg(
        Entry_Time=('Timestamp', 'min'),
        Exit_Time=('Timestamp', 'max'),
        Points=('Timestamp', 'count'),
        Avg_Altitude=('Altitude_ft', 'mean'),
        Avg_Speed=('Speed_kts', 'mean'),
    ).reset_index()
    
    tos_stats['Time_on_Station_Hours'] = (
        tos_stats['Exit_Time'] - tos_stats['Entry_Time']
    ).dt.total_seconds() / 3600
    
    return fleet_stats, tos_stats


def detect_loiter_zones(df):
    """Use DBSCAN to detect concentration areas."""
    if not HAS_SKLEARN:
        return pd.DataFrame()
    
    coords = df[['Latitude', 'Longitude']].values
    clustering = DBSCAN(eps=0.3, min_samples=10).fit(coords)
    df_copy = df.copy()
    df_copy['Cluster'] = clustering.labels_
    
    loiter_zones = df_copy[df_copy['Cluster'] >= 0].groupby('Cluster').agg(
        Center_Lat=('Latitude', 'mean'),
        Center_Lon=('Longitude', 'mean'),
        Points=('Cluster', 'count'),
    ).reset_index()
    
    return loiter_zones


def create_map(df, loiter_zones):
    """Create interactive Folium map."""
    if not HAS_FOLIUM:
        return None
    
    m = folium.Map(
        location=[REGION['center_lat'], REGION['center_lon']],
        zoom_start=6,
        tiles='CartoDB dark_matter',
    )
    
    # Strategic points
    for name, (lat, lon) in STRATEGIC_POINTS.items():
        icon_color = 'red' if 'Nuclear' in name else ('blue' if 'US' in name else 'gray')
        folium.Marker(
            [lat, lon],
            popup=f"<b>{name}</b>",
            icon=folium.Icon(color=icon_color),
        ).add_to(m)
    
    # Flight tracks
    for tail in df['Tail_Number'].unique():
        track_df = df[df['Tail_Number'] == tail].sort_values('Timestamp')
        platform = track_df['Platform'].iloc[0]
        
        points = track_df[['Latitude', 'Longitude']].values.tolist()
        folium.PolyLine(
            points,
            weight=2,
            color=COLORS.get(platform, '#ffffff'),
            opacity=0.7,
        ).add_to(m)
        
        last = track_df.iloc[-1]
        folium.CircleMarker(
            [last['Latitude'], last['Longitude']],
            radius=6,
            color=COLORS.get(platform, '#ffffff'),
            fill=True,
            popup=f"{platform} {tail}",
        ).add_to(m)
    
    # Loiter zones
    for _, zone in loiter_zones.iterrows():
        folium.Circle(
            [zone['Center_Lat'], zone['Center_Lon']],
            radius=30000,
            color='#ff00ff',
            fill=True,
            fillOpacity=0.1,
        ).add_to(m)
    
    return m


def export_data(df, tos_stats, m):
    """Export all data formats."""
    # CSV
    df.to_csv('isr_tracks.csv', index=False)
    print('✅ Saved: isr_tracks.csv')
    
    tos_stats.to_csv('tos_analytics.csv', index=False)
    print('✅ Saved: tos_analytics.csv')
    
    # GeoJSON
    if HAS_GEOPANDAS:
        geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
        gdf = gpd.GeoDataFrame(df.copy(), geometry=geometry, crs='EPSG:4326')
        gdf['Timestamp'] = gdf['Timestamp'].astype(str)
        gdf.to_file('isr_tracks.geojson', driver='GeoJSON')
        print('✅ Saved: isr_tracks.geojson')
    
    # KML
    if HAS_KML:
        kml = simplekml.Kml()
        for tail in df['Tail_Number'].unique():
            track_df = df[df['Tail_Number'] == tail].sort_values('Timestamp')
            platform = track_df['Platform'].iloc[0]
            coords = [(row['Longitude'], row['Latitude'], row['Altitude_ft'] * 0.3048)
                      for _, row in track_df.iterrows()]
            line = kml.newlinestring(name=f"{platform} {tail}")
            line.coords = coords
            line.altitudemode = simplekml.AltitudeMode.absolute
        kml.save('isr_tracks.kml')
        print('✅ Saved: isr_tracks.kml')
    
    # HTML Map
    if m:
        m.save('isr_map.html')
        print('✅ Saved: isr_map.html')


def main():
    print("=" * 50)
    print("🛩️  ISR INTELLIGENCE DASHBOARD")
    print("    Iran/Gulf Region Analysis")
    print("=" * 50)
    
    # Generate data
    print("\n📡 Generating synthetic ISR tracks...")
    df = generate_isr_tracks(num_points=100)
    print(f"   Generated {len(df)} track points")
    print(f"   Platforms: {df['Platform'].unique().tolist()}")
    
    # Analyze
    print("\n📊 Analyzing fleet data...")
    fleet_stats, tos_stats = analyze_tracks(df)
    print("\nFleet Composition:")
    print(fleet_stats.to_string(index=False))
    
    print("\nTime on Station:")
    print(tos_stats[['Platform', 'Tail_Number', 'Time_on_Station_Hours']].to_string(index=False))
    
    # Detect loiter zones
    print("\n🎯 Detecting loiter zones...")
    loiter_zones = detect_loiter_zones(df)
    if len(loiter_zones) > 0:
        print(f"   Found {len(loiter_zones)} concentration areas")
    
    # Create map
    print("\n🗺️  Creating interactive map...")
    m = create_map(df, loiter_zones)
    
    # Export
    print("\n💾 Exporting data...")
    export_data(df, tos_stats, m)
    
    print("\n" + "=" * 50)
    print("✅ COMPLETE! Open isr_map.html in your browser.")
    print("=" * 50)


if __name__ == '__main__':
    main()
