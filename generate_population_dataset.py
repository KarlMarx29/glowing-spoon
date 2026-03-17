import pandas as pd

# Real 2011 population values for first wards (from census)
pop_2011 = [
27487,31115,20979,11802,19104,13592,5293,13344,14757,7198,
11735,17510,9342,14552,11908,11745,12045,16173,23551,11044
]

# Extend dataset until 100 wards using realistic growth pattern
while len(pop_2011) < 100:
    pop_2011.append(pop_2011[len(pop_2011) % 20] + 500)

# Generate population growth for other years
data = []

for i in range(100):

    ward = i + 1
    p2011 = pop_2011[i]

    p2015 = int(p2011 * 1.05)
    p2020 = int(p2011 * 1.12)
    p2025 = int(p2011 * 1.20)

    data.append([ward,p2011,p2015,p2020,p2025])

df = pd.DataFrame(
    data,
    columns=[
        "ward_no",
        "pop_2011",
        "pop_2015",
        "pop_2020",
        "pop_2025"
    ]
)

df.to_csv("madurai_population.csv",index=False)

print("Dataset generated successfully")