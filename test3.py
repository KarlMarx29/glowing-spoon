import osmnx as ox
import geopandas as gpd
import pandas as pd

place = "Madurai, Tamil Nadu, India"

# Tags for facilities
tags = {
    "amenity": ["hospital", "school", "clinic", "library"],
    "leisure": ["park"],
    "shop": ["supermarket"]
}

# Download facilities
facilities = ox.features_from_place(place, tags)

facilities = facilities.reset_index()

facilities = facilities[["name","amenity","geometry"]]

print(facilities.head())

wards = gpd.read_file("madurai_wards_fixed.geojson")

facilities = gpd.GeoDataFrame(facilities, geometry="geometry", crs="EPSG:4326")

wards = wards.to_crs("EPSG:4326")

joined = gpd.sjoin(facilities, wards, how="left", predicate="within")

facility_summary = joined.groupby("ward_no")["amenity"].apply(list).reset_index()

facility_summary.columns = ["ward_no","facilities"]

population = pd.read_csv("madurai_population_100wards.csv")

final_dataset = population.merge(facility_summary, on="ward_no", how="left")

final_dataset.to_csv("madurai_ward_facilities.csv", index=False)
