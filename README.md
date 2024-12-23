# Toronto Bike Share Analysis

**[Read the results on StoryMaps](https://storymaps.com/stories/977d7a48e8104952b3843b25ddda4ec3)**

![](results/maps/heatmap.png)

## Overview
The objectives of this project were to determine what Toronto Bike Share data revealed about three specific bike lanes in Toronto, Canada that are targeted for removal and to practice geospatial analysis.

With the stated goal of reducing congestion, Bill 212 is a bill passed by the Province of Ontario that will remove bike lanes from three Toronto streets despite evidence that such infrastructure reduces traffic. Among other things, it will also make it more difficult for cities to install new bike infrastructure.

This analysis asks what data from the **Toronto Bike Share**, a station-based bike sharing program started in 2015, can tell us about the impact of removing the three lanes.

Statistical analysis
- General growth of Bike Share ridership
- How ridership changes seasonally
- Usage of Bike Share during rush hours

Geospatial analysis
- Bike share capacity near affected lanes

Heatmap
- Where trips likely passed through


## Key Takeaways
- In 2024, the bike share had an average of 19,500 trips per day
- Ridership has doubled since just 2021
- Ridership is roughly halved in the winter months and peaks in August
- 28% of all trips occured during "rush hour" (7-9AM, 4-6PM), or 4,300 trips each day
- 25% of bike share stations are within a 5 minute walk of the affected bike lanes
- **58% of trips (9,000 per day) started or ended within a 5 minute walk of the affected bike lanes**
- **14% of trips (3,000 per day) started or ended near the affected lanes during rush hour**


## Process
### Statistical Analysis in Python

### Geospatial Analysis in QGIS

### Heatmap Creation with PyQt


## Attribution
I am not affiliated with Toronto Bike Share, the City of Toronto, or the Government of Ontario.

**Tools Used**
- QGIS
- PyQt5
- PostGIS & PostSQL
- StoryMaps

**Data Used**
- Toronto Open Data - Bike Share ridership dataset
- Toronto Open Data - Bike Share stations dataset
- OpenStreetMap - Highway key for raodway network