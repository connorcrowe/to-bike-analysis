# 🚲 Toronto Bike Share Analysis

**Explore the interactive results: [Bike Share StoryMap](https://storymaps.com/stories/977d7a48e8104952b3843b25ddda4ec3)**

![](results/maps/heatmap.png)

## Overview
This project analyzed ridership data from the Toronto Bike Share (2016-2024) to uncover trends in usage that can predict the impact of some upcoming bicycle infrastructure changes in the city. Useing PostGIS, QGIS and PyQGIS, this study provides insight about the growth and types of usage and how that can inform future infrastructure decisions. 

## Tools & Tech
- **Database & Spatial Analysis:** PostgreSQL, PostGIS
- **Programming & Data Processing:** Python, PyQGIS, PyQt5, Pandas
- **Visualization & Mapping:** QGIS, Plotly, StoryMaps

## Methodology
**1. Data Acquisition & Storage**
- ***Bike Share Ridership and Station Locations:*** City of Toronto Open Data
- ***Roadway Network:*** Open Street Map

**2. Database Setup & Spatial Processing**
- ***PostSQL Database:*** Pulled data into a PostGIS-enabled PostgreSQL database (there is a web API for direct access, but an objective for this analysis was to practice setting up and utilizing PostGIS enabled databases from QGIS and PyQGIS scripts).
- Georeferenced bike share stations.

**3. Statistical Analysis**
- Pandas and Plotly were used to answer and display statistical questions, including the growth of the system, usage during rush hour, usage during the winter, etc.

**4. Geospatial Analysis**
- Queried OpenStreetMap to create connected roadway network of relevant roads only, a network of bike lanes, and a network of bike lanes specifically targeted for removal by legislation.
- Created a buffer around targeted bike lanes to identify nearby bike share stations, and to determine how much bike share ridership may be affected by changes to infrastructure.

**5. Heatmap Generation**
- Wrote script to create a heatmap of bike share trips based on their start and end station.
- Improved script to increment segments of the roadway network to improve efficiency and plotted heatmap for trips in August 2024.

## Results
**Key Takeaways**
- In 2024, the bike share had an average of 19,500 trips per day
- Ridership has doubled since just 2021
- Ridership is roughly halved in the winter months and peaks in August
- 28% of all trips occurred during "rush hour" (7-9AM, 4-6PM), or 4,300 trips each day
- 25% of bike share stations are within a 5 minute walk of the affected bike lanes
- **58% of trips (9,000 per day) started or ended within a 5 minute walk of the affected bike lanes**
- **14% of trips (3,000 per day) started or ended near the affected lanes during rush hour**

**Stations around affected lanes**
![](/results/maps/to_bike_share_stations_400m.jpg)

**Heatmap**
![](results/maps/heatmap.png)

*Full results available in the [StoryMap](https://storymaps.com/stories/977d7a48e8104952b3843b25ddda4ec3)*

## Data Sources
- Bike Share ridership dataset - [City of Toronto Open Data](https://open.toronto.ca/dataset/bike-share-toronto-ridership-data/)
- Bike Share stations dataset - [City of Toronto Open Data](https://open.toronto.ca/dataset/bike-share-toronto/)
- Highway key for roadway network - [OpenStreetMap](https://www.openstreetmap.org/#map=12/43.7177/-79.3763)