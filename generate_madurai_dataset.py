import geopandas as gpd
import pandas as pd
import random

# Load ward boundary GeoJSON
gdf = gpd.read_file("madurai_wards_fixed.geojson")

# Generate centroids
gdf["lat"] = gdf.geometry.centroid.y
gdf["lon"] = gdf.geometry.centroid.x

# Create dataset list
rows = []

for i,row in gdf.iterrows():

    ward_no = int(row["ward_no"])

    pop2011 = random.randint(9000,20000)
    pop2015 = int(pop2011*1.08)
    pop2020 = int(pop2015*1.10)
    pop2025 = int(pop2020*1.09)

    rows.append({

        "ward_no": ward_no,
        "ward_name": f"Ward {ward_no}",
        "lat": row["lat"],
        "lon": row["lon"],
        "pop_2011": pop2011,
        "pop_2015": pop2015,
        "pop_2020": pop2020,
        "pop_2025": pop2025,
        "councillor": f"Councillor {ward_no}",
        "facilities": "School, PHC, Park"

    })

# Convert to dataframe
df = pd.DataFrame(rows)

# Save dataset
df.to_csv("madurai_population_100wards.csv",index=False)

print("Dataset generated successfully")