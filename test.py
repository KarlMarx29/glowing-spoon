import pandas as pd
import folium
from folium.plugins import HeatMapWithTime

data = pd.read_csv("madurai_population_timeline.csv")

years = ['pop_2011','pop_2015','pop_2020','pop_2025']

heat_data = []

for year in years:

    temp = []

    for i,row in data.iterrows():

        temp.append([row['lat'],row['lon'],row[year]])

    heat_data.append(temp)

m = folium.Map(location=[9.9252,78.1198],zoom_start=12)

HeatMapWithTime(
heat_data,
index=['2011','2015','2020','2025'],
auto_play=True
).add_to(m)

m.save("templates/heatmap.html")