from qgis.core import *
import processing
from PyQt5.QtCore import QVariant
import time

def ensure_trip_calculated_field(trips_layer):
    """Add trip_calculated field"""
    # Check if layer is currently in edit mode and commit/rollback if needed
    if trips_layer.isEditable():
        try:
            trips_layer.commitChanges()
        except:
            trips_layer.rollbackChanges()
    
    # Check if field already exists
    if 'trip_calculated' not in trips_layer.fields().names():
        # Start editing
        trips_layer.startEditing()
        
        try:
            # Add the field
            trips_layer.dataProvider().addAttributes([QgsField('trip_calculated', QVariant.Int)])
            trips_layer.updateFields()
            
            # Set initial values to 0
            field_index = trips_layer.fields().indexFromName('trip_calculated')
            for feature in trips_layer.getFeatures():
                trips_layer.changeAttributeValue(feature.id(), field_index, 0)
            
            # Commit changes
            trips_layer.commitChanges()
            
            print("Added 'trip_calculated' field")
            for field in trips_layer.fields(): 
                print(field.name())
        
        except Exception as e:
            # If anything goes wrong, rollback changes
            trips_layer.rollbackChanges()
            print(f"Error adding field: {e}")
    
    return trips_layer

def analyze_bike_trips(trips_layer, stations_layer, network_layer, max_trips=None, batch_size=100):
    """
    Analyze bike trips with trip calculation tracking
    
    :param trips_layer: Layer containing trip data
    :param stations_layer: Layer containing station locations
    :param network_layer: Road network layer
    :param max_trips: Maximum number of trips to process
    :param batch_size: Number of trips to process in each batch
    :return: Updated network layer
    """
    start_time = time.time()
    
    # Ensure trip_calculated field exists
    trips_layer = ensure_trip_calculated_field(trips_layer)
    
    # Create stations dictionary
    stations_dict = {station['station_id']: station for station in stations_layer.getFeatures()}
    
    # Collect uncalculated trips
    trips = [
        trip for trip in trips_layer.getFeatures() 
        if trip['trip_calculated'] == 0
    ]
    
    if max_trips:
        trips = trips[:max_trips]
    
    print(trips[0]['fid'])
    # Process trips in batches
    processed_count = 0
    
    for i in range(0, len(trips), batch_size):
        batch = trips[i:i+batch_size]
        
        for trip in batch:
            start_station_id = trip['start_station_id']
            end_station_id = trip['end_station_id']
            
            start_station = stations_dict.get(start_station_id)
            end_station = stations_dict.get(end_station_id)
            
            if not start_station or not end_station:
                trips_layer = update_trip_calculated(trips_layer, trip, -1)
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
            
            # Mark trip as calculated
            with edit(trips_layer):
                if path_layer: status = trip['trip_calculated'] = 1
                else: trip['trip_calculated'] = -1
                trips_layer.updateFeature(trip)
            
            processed_count += 1
            
            # Progress reporting
            if processed_count % 100 == 0:
                print(f"Processed {processed_count} trips...")
                QApplication.processEvents()
    
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
    trips_layer.triggerRepaint()
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
        #print(f"Path finding error: {e}")
        return None

def update_trip_calculated(trips_layer, trip, status):
    with edit(trips_layer):
        trip['trip_calculated'] = status
        trips_layer.updateFeature(trip)
    return trips_layer

# Main execution
trips_layer = QgsProject.instance().mapLayersByName('24_08_rush')[0]
stations_layer = QgsProject.instance().mapLayersByName('stations')[0]
network_layer = QgsProject.instance().mapLayersByName('network_simple')[0]

# Analyze trips
network_layer = analyze_bike_trips(
    trips_layer, 
    stations_layer, 
    network_layer, 
    max_trips=20000,
    batch_size=20
)