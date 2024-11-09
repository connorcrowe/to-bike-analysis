from qgis.core import *
import processing
from PyQt5.QtCore import QVariant
from collections import defaultdict
import concurrent.futures
import threading
import time
from datetime import datetime

def format_time(seconds):
    """Convert seconds to a human-readable format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def process_trip_batch(trip_batch, network_layer, stations_dict, lock, batch_num):
    batch_start = time.time()
    results = []
    processed_count = 0
    
    for trip in trip_batch:
        start_station_id = trip['Start Station Id']
        end_station_id = trip['End Station Id']

        # Get station features
        start_station = stations_dict.get(start_station_id)
        end_station = stations_dict.get(end_station_id)

        if not start_station or not end_station:
            print(f"Warning: Could not find station(s) for trip {trip['Trip Id']}")
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
            with lock:  # Use lock when running processing algorithm
                result = processing.run("native:shortestpathpointtopoint", params)
            
            if result and 'OUTPUT' in result:
                path_layer = result['OUTPUT']
                path_feature = next(path_layer.getFeatures())
                
                results.append({
                    'geometry': path_feature.geometry(),
                    'trip_id': trip['Trip Id'],
                    'start_station': start_station_id,
                    'end_station': end_station_id
                })
                processed_count += 1
            
        except Exception as e:
            print(f"Error processing trip {trip['Trip Id']}: {str(e)}")
    
    batch_time = time.time() - batch_start
    print(f"Batch {batch_num} completed: {processed_count} trips processed in {format_time(batch_time)}")
    
    return results

def calculate_bike_trips(trips_layer, stations_layer, network_layer, max_trips, batch_size, workers, output_layer_name='bike_trips'):
    total_start_time = time.time()
    print(f"\nStarting processing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Parameters: max_trips={max_trips}, batch_size={batch_size}")
    
    # Create a memory layer to store the paths
    paths_layer = QgsVectorLayer(f"LineString?crs=epsg:4326", output_layer_name, "memory")
    paths_provider = paths_layer.dataProvider()
    
    # Add fields for the paths layer
    paths_provider.addAttributes([
        QgsField("trip_id", QVariant.String),
        QgsField("start_station", QVariant.String),
        QgsField("end_station", QVariant.String)
    ])
    paths_layer.updateFields()

    # Create stations dictionary with cache
    print("Building stations dictionary...")
    stations_dict = {station['station_id']: station for station in stations_layer.getFeatures()}
    print(f"Found {len(stations_dict)} stations")

    # Get all trips up to max_trips
    print("Collecting trips...")
    trips = []
    for trip in trips_layer.getFeatures():
        if max_trips and len(trips) >= max_trips:
            break
        trips.append(trip)
    print(f"Processing {len(trips)} trips")

    # Process trips in batches using multiple threads
    lock = threading.Lock()
    results = []
    
    # Split trips into batches
    trip_batches = [trips[i:i + batch_size] for i in range(0, len(trips), batch_size)]
    print(f"Split into {len(trip_batches)} batches of size {batch_size}")
    
    processing_start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_batch = {
            executor.submit(
                process_trip_batch, 
                batch, 
                network_layer, 
                stations_dict,
                lock,
                batch_num + 1
            ): batch_num for batch_num, batch in enumerate(trip_batches)
        }
        
        for future in concurrent.futures.as_completed(future_to_batch):
            batch_results = future.result()
            results.extend(batch_results)

    processing_time = time.time() - processing_start_time
    print(f"\nPath processing completed in {format_time(processing_time)}")

    # Add all results to the layer at once
    print("Adding features to layer...")
    features = []
    for result in results:
        new_feature = QgsFeature(paths_layer.fields())
        new_feature.setGeometry(result['geometry'])
        new_feature.setAttribute('trip_id', result['trip_id'])
        new_feature.setAttribute('start_station', result['start_station'])
        new_feature.setAttribute('end_station', result['end_station'])
        features.append(new_feature)

    paths_provider.addFeatures(features)
    paths_layer.updateExtents()
    
    # Add the layer to the map
    QgsProject.instance().addMapLayer(paths_layer)
    
    total_time = time.time() - total_start_time
    print(f"\nExecution Summary:")
    print(f"Total trips processed: {len(features)}")
    print(f"Success rate: {(len(features) / len(trips) * 100):.1f}%")
    print(f"Average time per trip: {(processing_time / len(trips)):.2f} seconds")
    print(f"Total execution time: {format_time(total_time)}")
    print(f"Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return paths_layer

# Example usage:
# Get the layers from the QGIS project
trips_layer = QgsProject.instance().mapLayersByName('24_06_rides')[0]
stations_layer = QgsProject.instance().mapLayersByName('stations')[0]
network_layer = QgsProject.instance().mapLayersByName('network')[0]

# Calculate paths for first 1000 trips
paths_layer = calculate_bike_trips(
    trips_layer, 
    stations_layer, 
    network_layer, 
    max_trips=1000,
    batch_size=50,
    workers = 4  # Adjust based on your system's capabilities
)