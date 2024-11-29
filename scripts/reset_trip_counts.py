# Reset trips_count to 0 for network layer
network_layer = QgsProject.instance().mapLayersByName('network_simple')[0]

with edit(network_layer):
   for feature in network_layer.getFeatures():
       feature['trips_count'] = 0
       network_layer.updateFeature(feature)

network_layer.triggerRepaint()
print("Network layer trips_count reset to 0")