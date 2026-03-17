import pandas as pd
import random

# load existing dataset
df = pd.read_csv("madurai_population_timeline.csv")

# center of Madurai
lat_center = 9.9252
lon_center = 78.1198

current_max = df["ward_no"].max()

rows = []

for ward in range(current_max + 1, 101):

    base_pop = random.randint(8000, 25000)

    pop2011 = base_pop
    pop2015 = int(pop2011 * 1.07)
    pop2020 = int(pop2011 * 1.17)
    pop2025 = int(pop2011 * 1.28)

    lat = lat_center + random.uniform(-0.04, 0.04)
    lon = lon_center + random.uniform(-0.04, 0.04)

    rows.append({
        "ward_no": ward,
        "ward_name": f"Ward{ward}",
        "lat": round(lat,4),
        "lon": round(lon,4),
        "pop_2011": pop2011,
        "pop_2015": pop2015,
        "pop_2020": pop2020,
        "pop_2025": pop2025
    })

df_new = pd.DataFrame(rows)

final_df = pd.concat([df, df_new], ignore_index=True)

final_df.to_csv("madurai_population_100wards.csv", index=False)

print("100 ward dataset generated successfully")