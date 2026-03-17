import json

# load geojson
with open("madurai_wards.geojson") as f:
    data = json.load(f)

# add ward numbers
for i, feature in enumerate(data["features"]):
    feature["properties"]["ward_no"] = i + 1

# save fixed geojson
with open("madurai_wards_fixed.geojson", "w") as f:
    json.dump(data, f)

print("ward_no added to GeoJSON successfully")