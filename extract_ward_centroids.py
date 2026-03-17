import geopandas as gpd
import pandas as pd

# Load your ward boundary GeoJSON
gdf = gpd.read_file("madurai_wards_fixed.geojson")

# Ensure coordinate system is WGS84
gdf = gdf.to_crs(epsg=4326)

# Compute centroid of each ward polygon
gdf["lat"] = gdf.geometry.centroid.y
gdf["lon"] = gdf.geometry.centroid.x

# If ward names exist
if "Name" in gdf.columns:
    ward_names = gdf["Name"]
else:
    ward_names = ["Ward"+str(i+1) for i in range(len(gdf))]

# Create dataset
df = pd.DataFrame({
    "ward_no": range(1, len(gdf)+1),
    "ward_name": ward_names,
    "lat": gdf["lat"],
    "lon": gdf["lon"]
})

# Save centroid dataset
df.to_csv("madurai_ward_centroids.csv", index=False)

print("Centroid dataset created")