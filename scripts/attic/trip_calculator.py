from qgis.core import *
import processing

def calculate_bike_trips(trips_layer, stations_layer, network_layer, max_trips, output_layer_name='bike_trips'):
    # Create a memory layer to store the paths
    crs = QgsCoordinateReferenceSystem('EPSG:4326')
    paths_layer = QgsVectorLayer(f"LineString?crs=epsg:4326", output_layer_name, "memory")
    paths_provider = paths_layer.dataProvider()
    
    # Add fields for the paths layer
    paths_provider.addAttributes([
        QgsField("trip_id", QVariant.String),
        QgsField("start_station", QVariant.String),
        QgsField("end_station", QVariant.String)
    ])
    paths_layer.updateFields()

    # Create spatial index for stations layer for faster lookups
    stations_index = QgsSpatialIndex()
    stations_dict = {}
    for station in stations_layer.getFeatures():
        stations_index.addFeature(station)
        stations_dict[station['station_id']] = station

    # Process each trip
    count = 0
    total_features = trips_layer.featureCount()
    for current, trip in enumerate(trips_layer.getFeatures()):
        # Update progress every 100 features
        if count == max_trips: break
        print(f"Processing trip {count}/{max_trips}")

        start_station_id = trip['Start Station Id']
        end_station_id = trip['End Station Id']

        # Get station features
        start_station = stations_dict.get(start_station_id)
        end_station = stations_dict.get(end_station_id)

        if not start_station or not end_station:
            print(f"Warning: Could not find station(s) for trip {trip['Trip Id']}, ({count})")
            continue

        # Get coordinates
        start_point = start_station.geometry().asPoint()
        end_point = end_station.geometry().asPoint()

        # Calculate shortest path
        params = {
            'INPUT': network_layer,
            'STRATEGY': 0,  # Shortest path
            'START_POINT': f'{start_point.x()},{start_point.y()} [EPSG:4326]',
            'END_POINT': f'{end_point.x()},{end_point.y()} [EPSG:4326]',
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }

        try:
            result = processing.run("native:shortestpathpointtopoint", params)
            
            if result and 'OUTPUT' in result:
                # Get the path geometry
                path_layer = result['OUTPUT']
                path_feature = next(path_layer.getFeatures())
                
                # Create new feature
                new_feature = QgsFeature(paths_layer.fields())
                new_feature.setGeometry(path_feature.geometry())
                new_feature.setAttribute('trip_id', trip['Trip Id'])
                new_feature.setAttribute('start_station', start_station_id)
                new_feature.setAttribute('end_station', end_station_id)
                
                paths_provider.addFeature(new_feature)
            
        except Exception as e:
            print(f"Error processing trip {trip['Trip Id']}: {str(e)}")
        count += 1

    paths_layer.updateExtents()
    
    # Add the layer to the map
    QgsProject.instance().addMapLayer(paths_layer)
    
    return paths_layer

# Example usage:

# Get the layers from the QGIS project
trips_layer = QgsProject.instance().mapLayersByName('24_06_rides')[0]
stations_layer = QgsProject.instance().mapLayersByName('stations')[0]
network_layer = QgsProject.instance().mapLayersByName('network')[0]

# Calculate paths
paths_layer = calculate_bike_trips(trips_layer, stations_layer, network_layer, 20)
