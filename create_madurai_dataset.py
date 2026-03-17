import geopandas as gpd
import pandas as pd
import random

# Load ward boundaries
gdf = gpd.read_file("madurai_wards_fixed.geojson")

# Convert coordinate system
gdf = gdf.to_crs(epsg=4326)

# Calculate centroids
gdf["lat"] = gdf.geometry.centroid.y
gdf["lon"] = gdf.geometry.centroid.x

# Real ward names for first wards
ward_names = [
"Santhi Nagar","Koodal Nagar","Anaiyur","Sambandhar Alankulam","BB Kulam",
"Meenambalpuram","Kailaasapuram","Vilangudi","Thathaneri","Aarappalayam",
"Ponnaharam","Krishnapalayam","Azhagaradi","Viswasapuri","Melapponnaharam",
"Railway Colony","Ellis Nagar","SS Colony","Ponmeni","Arasaradi"
]

# Fill remaining ward names
for i in range(len(ward_names)+1,101):
    ward_names.append(f"Ward{i}")

rows = []

for i in range(len(gdf)):

    pop2011 = random.randint(8000,30000)
    pop2015 = int(pop2011*1.07)
    pop2020 = int(pop2011*1.17)
    pop2025 = int(pop2011*1.28)

    rows.append({
        "ward_no": i+1,
        "ward_name": ward_names[i],
        "lat": gdf.iloc[i]["lat"],
        "lon": gdf.iloc[i]["lon"],
        "pop_2011": pop2011,
        "pop_2015": pop2015,
        "pop_2020": pop2020,
        "pop_2025": pop2025
    })

df = pd.DataFrame(rows)

df.to_csv("madurai_population_100wards.csv",index=False)

print("Dataset created successfully")