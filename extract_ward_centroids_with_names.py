import geopandas as gpd
import pandas as pd

# Load ward boundary file
gdf = gpd.read_file("madurai_wards_fixed.geojson")

# Ensure WGS84 coordinate system
gdf = gdf.to_crs(epsg=4326)

# Calculate centroid
gdf["lat"] = gdf.geometry.centroid.y
gdf["lon"] = gdf.geometry.centroid.x

# If ward name field exists
if "Name" in gdf.columns:
    ward_names = gdf["Name"]
else:
    ward_names = ["Ward" + str(i+1) for i in range(len(gdf))]

# Create dataframe
df = pd.DataFrame({
    "ward_no": gdf["ward_no"],
    "ward_name": ward_names,
    "lat": gdf["lat"],
    "lon": gdf["lon"]
})

# Save file
df.to_csv("madurai_ward_centroids.csv", index=False)

print("Ward centroid dataset created successfully")