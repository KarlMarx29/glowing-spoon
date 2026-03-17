import geopandas as gpd

# Load KML file
gdf = gpd.read_file("madurai_wards.kml")

# Convert to GeoJSON
gdf.to_file("static/data/madurai_wards.geojson", driver="GeoJSON")

print("Conversion Completed")