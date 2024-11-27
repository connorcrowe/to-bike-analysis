from qgis.core import *
import processing
from PyQt5.QtCore import QVariant
import time
from datetime import datetime

def prepare_network_layer(network_layer):
    """Add and initialize trips_count field"""
    if 'trips_count' not in [field.name() for field in network_layer.fields()]:
        network_layer.dataProvider().addAttributes([QgsField('trips_count', QVariant.Int)])
        network_layer.updateFields()
    
    # Reset counts using provider for efficiency
    with edit(network_layer):
        for feature in network_layer.getFeatures():
            feature['trips_count'] = 0
            network_layer.updateFeature(feature)
    
    return network_layer

def find_shortest_path(start_point, end_point, network_layer):
    """Find shortest path between two points"""
    try:
        params = {
            'INPUT': network_layer,
            'STRATEGY': 0,  # Shortest path
            'START_POINT': f'{start_point.x()},{start_point.y()} [EPSG:4326]',
            'END_POINT': f'{end_point.x()},{end_point.y()} [EPSG:4326]',
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
        result = processing.run("native:shortestpathpointtopoint", params)
        return result['OUTPUT'] if result and 'OUTPUT' in result else None
    except Exception as e:
        print(f"Path finding error: {e}")
        return None

def analyze_bike_trips(trips_layer, stations_layer, network_layer, max_trips=None, batch_size=100):
    """
    Analyze bike trips with a QGIS-compatible approach
    
    :param trips_layer: Layer containing trip data
    :param stations_layer: Layer containing station locations
    :param network_layer: Road network layer
    :param max_trips: Maximum number of trips to process (for testing)
    :param batch_size: Number of trips to process in each batch
    :return: Updated network layer
    """
    start_time = time.time()
    
    # Prepare network layer
    network_layer = prepare_network_layer(network_layer)
    
    # Create stations dictionary
    stations_dict = {station['station_id']: station for station in stations_layer.getFeatures()}
    
    # Collect trips
    trips = list(trips_layer.getFeatures())
    if max_trips:
        trips = trips[:max_trips]
    
    # Process trips in batches
    processed_count = 0
    
    for i in range(0, len(trips), batch_size):
        batch = trips[i:i+batch_size]
        
        for trip in batch:
            start_station_id = trip['Start Station Id']
            end_station_id = trip['End Station Id']
            
            start_station = stations_dict.get(start_station_id)
            end_station = stations_dict.get(end_station_id)
            
            if not start_station or not end_station:
                continue
            
            start_point = start_station.geometry().asPoint()
            end_point = end_station.geometry().asPoint()
            
            path_layer = find_shortest_path(start_point, end_point, network_layer)
            
            if path_layer:
                # Update network layer with path segments
                with edit(network_layer):
                    for path_feature in path_layer.getFeatures():
                        path_geom = path_feature.geometry()
                        for segment in network_layer.getFeatures():
                            if segment.geometry().intersects(path_geom):
                                current_count = segment['trips_count'] or 0
                                segment['trips_count'] = current_count + 1
                                network_layer.updateFeature(segment)
            
            processed_count += 1
            
            # Progress reporting
            if processed_count % 100 == 0:
                print(f"Processed {processed_count} trips...")
                # Force QGIS to update UI
                iface.mapCanvas().refresh()  # Refresh the map canvas
                QApplication.processEvents()  # Allow UI to update
    
    # Report results
    total_time = time.time() - start_time
    used_segments = sum(1 for feature in network_layer.getFeatures() if feature['trips_count'] > 0)
    max_segment_trips = max(feature['trips_count'] for feature in network_layer.getFeatures())
    
    print(f"\nExecution Summary:")
    print(f"Total Trips: {processed_count}")
    print(f"Network Segments Used: {used_segments}")
    print(f"Max Trips on Segment: {max_segment_trips}")
    print(f"Total Execution Time: {total_time:.2f} seconds")
    
    network_layer.triggerRepaint()
    return network_layer

# Main execution
trips_layer = QgsProject.instance().mapLayersByName('24_06_rides')[0]
stations_layer = QgsProject.instance().mapLayersByName('stations')[0]
network_layer = QgsProject.instance().mapLayersByName('network_simple')[0]

# Analyze trips
network_layer = analyze_bike_trips(
    trips_layer, 
    stations_layer, 
    network_layer, 
    max_trips=100000,
    batch_size=50
)