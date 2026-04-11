# 🛡️ Drone Detection & ISR Intelligence Dashboard

**Airborne swarm deconfliction & intelligence analysis for defense ISR operations**

Built by [Dwight Pagán](https://github.com/paganld) · AI-Powered GEOINT

---

## Overview

An intelligence analysis pipeline that generates **synthetic** airborne ISR tracks (MQ-9 Reaper, RC-135 Rivet Joint, RQ-4 Global Hawk, P-8 Poseidon) over the Iran/Gulf region, performs DBSCAN clustering to detect loiter zones, and exports multi-format geospatial outputs including interactive heatmaps, GeoJSON, KML, and CSV analytics.

Built as an open-source alternative to ArcGIS Pro for airborne ISR pattern analysis.

## ⚠️ Data & Privacy

All ISR tracks in this project are **synthetic (simulated)** for demonstration and research purposes only. No classified, real-time, or restricted flight data is included. Aircraft positions, tail numbers, flight patterns, and mission parameters are entirely fabricated. The geographic focus (Iran/Gulf region) is illustrative and does not correspond to any real-world intelligence operation.

The OpenSky Network integration is provided for optional real ADS-B data fetching — all data sourced from the publicly available, unencrypted ADS-B broadcasts.

## Features

- ✈️ **Multi-platform ISR simulation** — Realistic flight patterns (loiter, orbit, transit, racetrack, maritime patrol)
- 🎯 **DBSCAN loiter detection** — Automatic identification of concentration areas
- 📊 **Time-on-Station analytics** — Fleet composition, endurance, and altitude analysis
- 🗺️ **Interactive heatmap** — Folium-powered ISR activity density visualization
- 📈 **Plotly dashboard** — Altitude profiles, speed analysis, activity heatmaps
- 💾 **Multi-format export** — CSV, GeoJSON, KML, HTML map

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.9+ |
| Data Processing | Pandas, NumPy |
| Mapping | Folium (interactive maps + heatmaps) |
| ML / Clustering | Scikit-learn (DBSCAN) |
| Geospatial | GeoPandas + Shapely (GeoJSON export) |
| KML Export | SimpleKML |
| Analytics | Plotly |

## Quick Start

```bash
git clone https://github.com/paganld/drone-detection.git
cd drone-detection

# Install
pip install -r requirements.txt

# Run the dashboard
python isr_dashboard.py
```

### Outputs

| File | Format | Content |
|------|--------|---------|
| `isr_tracks.csv` | CSV | All track points with platform, position, and heading |
| `isr_tracks.geojson` | GeoJSON | Geospatial track data for GIS applications |
| `isr_tracks.kml` | KML | 3D flight paths for Google Earth |
| `isr_map.html` | HTML | Interactive map with flight tracks + loiter zones |
| `tos_analytics.csv` | CSV | Time-on-Station analytics per aircraft |

## Platform Types

| Platform | Role | Pattern | Altitude |
|----------|------|---------|----------|
| MQ-9 Reaper | Armed ISR | Loiter | 18K–25K ft |
| RC-135 Rivet Joint | SIGINT | Wide orbit | 28K–35K ft |
| RQ-4 Global Hawk | High-altitude ISR | Transit / Racetrack | 55K–60K ft |
| P-8 Poseidon | Maritime patrol | Maritime grid | 15K–28K ft |

## Data Sources

- [OpenSky Network](https://opensky-network.org/) — Open ADS-B flight data (optional)

All data sources are publicly available and used in compliance with their respective terms of service.

## Author

**Dwight Pagán** — Data Scientist & AI Engineer
Building platforms that turn raw data into actionable intelligence.

- GitHub: [@paganld](https://github.com/paganld)
- LinkedIn: [linkedin.com/in/dwightjosefpagan](https://linkedin.com/in/dwightjosefpagan)

---

*Part of the OrbitData platform family — geospatial intelligence for the open-source community.*
