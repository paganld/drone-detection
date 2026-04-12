# 🛰️ Flight Pattern Analysis

**Geospatial flight trajectory clustering and movement pattern recognition using open-source ADS-B data**

Built by [Dwight Pagán](https://github.com/paganld) · Geospatial Data Science

---

## Overview

Flight Pattern Analysis is a Python-based geospatial data science pipeline that analyzes aircraft movement patterns using open-source ADS-B data. It generates synthetic flight tracks with realistic movement behaviors, applies DBSCAN spatial clustering to identify concentration areas, and exports results in multiple geospatial formats (GeoJSON, KML, CSV, HTML).

This project demonstrates spatial clustering, time-series analysis, and geospatial visualization techniques using publicly available aviation data.

## Features

- ✈️ **Synthetic flight track generation** — Realistic movement patterns (holding, transit, survey grids, racetrack orbits)
- 🎯 **DBSCAN spatial clustering** — Automatic identification of flight concentration areas
- 📊 **Trajectory analytics** — Flight duration, altitude profiles, speed analysis per aircraft
- 🗺️ **Interactive heatmap** — Folium-powered flight density visualization
- 📈 **Plotly analytics** — Altitude profiles, speed distributions, activity heatmaps
- 💾 **Multi-format export** — CSV, GeoJSON, KML, interactive HTML map

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.9+ |
| Data Processing | Pandas, NumPy |
| Spatial Clustering | Scikit-learn (DBSCAN) |
| Mapping | Folium (interactive maps + heatmaps) |
| Geospatial | GeoPandas + Shapely |
| KML Export | SimpleKML |
| Analytics | Plotly |

## Quick Start

```bash
git clone https://github.com/paganld/flight-pattern-analysis.git
cd flight-pattern-analysis

# Install
pip install -r requirements.txt

# Run
python flight_analysis.py
```

### Outputs

| File | Format | Content |
|------|--------|---------|
| `flight_tracks.csv` | CSV | All track points with aircraft ID, position, heading, speed |
| `flight_tracks.geojson` | GeoJSON | Geospatial track data for GIS applications |
| `flight_tracks.kml` | KML | 3D flight paths for Google Earth |
| `flight_map.html` | HTML | Interactive map with flight tracks and concentration zones |
| `analytics.csv` | CSV | Per-aircraft analytics: duration, avg altitude, avg speed |

## Pattern Types

The pipeline simulates and detects these common aviation movement patterns:

| Pattern | Description | Typical Altitude |
|---------|-------------|-----------------|
| Holding | Circular/oval patterns near waypoints | 10K–25K ft |
| Transit | Linear point-to-point movement | 25K–40K ft |
| Survey Grid | Systematic back-and-forth grid | 5K–15K ft |
| Racetrack | Standard racetrack holding procedure | 15K–35K ft |

## Data Sources

- [OpenSky Network](https://opensky-network.org/) — Open ADS-B flight data (optional integration)

All data used in this project is **synthetic or publicly available** from open ADS-B broadcasts.

## Use Cases

- **Aviation data science education** — Spatial clustering on real-world-ish movement data
- **Air traffic pattern analysis** — Identify frequently used routes and holding areas
- **Portfolio project** — Full Python geospatial pipeline with ML clustering
- **Research base** — Foundation for anomaly detection in flight behaviors

## Author

**Dwight Pagán** — Data Scientist & AI Engineer
Building platforms that turn spatial data into actionable insights.

- GitHub: [@paganld](https://github.com/paganld)
- LinkedIn: [linkedin.com/in/dwightjosefpagan](https://linkedin.com/in/dwightjosefpagan)

---

*Part of the OrbitData platform family — geospatial data science for the open-source community.*
