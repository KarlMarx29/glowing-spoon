import osmnx as ox
import geopandas as gpd
import pandas as pd

print("Downloading facilities from OpenStreetMap...")

# ---------------------------------------------------
# 1. Download facilities from OpenStreetMap
# ---------------------------------------------------

place = "Madurai, Tamil Nadu, India"

tags = {
    "amenity": ["hospital", "school", "clinic", "library"],
    "leisure": ["park"],
    "shop": ["supermarket"]
}

facilities = ox.features_from_place(place, tags)

facilities = facilities.reset_index()

facilities = facilities[["name","amenity","leisure","shop","geometry"]]

print("Facilities downloaded:", len(facilities))


# ---------------------------------------------------
# 2. Load Madurai Ward GeoJSON
# ---------------------------------------------------

print("Loading ward boundaries...")

wards = gpd.read_file("madurai_wards_fixed.geojson")

wards = wards.to_crs("EPSG:4326")

facilities = gpd.GeoDataFrame(facilities, geometry="geometry", crs="EPSG:4326")


# ---------------------------------------------------
# 3. Spatial Join (find ward for each facility)
# ---------------------------------------------------

print("Assigning facilities to wards...")

joined = gpd.sjoin(facilities, wards, how="left", predicate="within")


# ---------------------------------------------------
# 4. Create facility type column
# ---------------------------------------------------

def get_type(row):

    if pd.notnull(row["amenity"]):
        return row["amenity"]

    if pd.notnull(row["leisure"]):
        return row["leisure"]

    if pd.notnull(row["shop"]):
        return row["shop"]

    return "other"


joined["facility_type"] = joined.apply(get_type, axis=1)


# ---------------------------------------------------
# 5. Group facilities by ward
# ---------------------------------------------------

print("Grouping facilities per ward...")

facility_summary = joined.groupby("ward_no")["facility_type"].apply(list).reset_index()

facility_summary.columns = ["ward_no","facilities"]


# ---------------------------------------------------
# 6. Load your population dataset
# ---------------------------------------------------

population = pd.read_csv("madurai_population_100wards.csv")


# ---------------------------------------------------
# 7. Merge facilities with ward dataset
# ---------------------------------------------------

final_dataset = population.merge(facility_summary, on="ward_no", how="left")


# ---------------------------------------------------
# 8. Save final dataset
# ---------------------------------------------------

final_dataset.to_csv("madurai_ward_facilities.csv", index=False)

print("Dataset created successfully!")

print("Saved file: madurai_ward_facilities.csv")