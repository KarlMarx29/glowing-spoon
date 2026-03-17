from flask import Flask,render_template,request,redirect,session
import pandas as pd
import folium
import plotly.express as px
from db import get_db_connection
import json
import osmnx as ox

app = Flask(__name__)
app.secret_key="madurai"





# Home
@app.route('/')
def index():
    return render_template('index.html')


# Registration
@app.route('/register',methods=['GET','POST'])
def register():

    if request.method=='POST':

        name=request.form['name']
        email=request.form['email']
        password=request.form['password']

        conn=get_db_connection()
        cur=conn.cursor()

        cur.execute("insert into users(name,email,password) values(%s,%s,%s)",
                    (name,email,password))

        conn.commit()

        return redirect('/login')

    return render_template('register.html')


# Login
@app.route('/login',methods=['GET','POST'])
def login():

    if request.method=='POST':

        email=request.form['email']
        password=request.form['password']

        conn=get_db_connection()
        cur=conn.cursor()

        cur.execute("select * from users where email=%s and password=%s",
                    (email,password))

        user=cur.fetchone()

        if user:
            session['user']=user[0]
            return redirect('/dashboard')

    return render_template('login.html')


# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    df = pd.read_csv("madurai_population_timeline.csv")
    df["pop_2015"] = df["pop_2015"].astype(int)
    df["pop_2020"] = df["pop_2020"].astype(int)
    df["pop_2025"] = df["pop_2025"].astype(int)
    df.to_csv("madurai_population_timeline.csv",index=False)

    wards = df.to_dict(orient="records")

    return render_template("dashboard.html",wards=wards)

@app.route('/heatmap')
def heatmap():

    import pandas as pd
    import folium
    from folium.plugins import HeatMapWithTime

    # Load dataset
    data = pd.read_csv("madurai_population_100wards.csv")

    years = ['pop_2011','pop_2015','pop_2020','pop_2025']

    heat_data = []

    for year in years:

        temp = []

        for i,row in data.iterrows():

            temp.append([row['lat'],row['lon'],row[year]])

        heat_data.append(temp)

    # Create map
    m = folium.Map(location=[9.9252,78.1198],zoom_start=12)

    HeatMapWithTime(
        heat_data,
        index=['2011','2015','2020','2025'],
        auto_play=True
    ).add_to(m)

    # Save heatmap HTML
    m.save("templates/heatmap.html")

    return render_template("heatmap.html")


# Processing Page (Map)
@app.route('/map')
def map():

    df=pd.read_csv('madurai_population_timeline.csv')
    df["pop_2015"] = df["pop_2015"].astype(int)
    df["pop_2020"] = df["pop_2020"].astype(int)
    df["pop_2025"] = df["pop_2025"].astype(int)
    df.to_csv("madurai_population_timeline.csv",index=False)

    m=folium.Map(location=[9.9252,78.1198],zoom_start=12)

    for i,row in df.iterrows():

        folium.CircleMarker(
            location=[row['lat'],row['lon']],
            radius=row['pop_2025']/10000,
            popup=f"Ward {row['ward_no']} Population {row['pop_2025']}",
            color="red",
            fill=True
        ).add_to(m)

    m.save('templates/map.html')

    return render_template('map.html')


# History
@app.route('/history')
def history():

    conn=get_db_connection()
    cur=conn.cursor()

    cur.execute("select * from history")

    data=cur.fetchall()

    return render_template('history.html',data=data)


# Performance Chart
@app.route('/chart')
def chart():

    df=pd.read_csv('madurai_population_timeline.csv')
    df["pop_2015"] = df["pop_2015"].astype(int)
    df["pop_2020"] = df["pop_2020"].astype(int)
    df["pop_2025"] = df["pop_2025"].astype(int)
    df.to_csv("madurai_population_timeline.csv",index=False)

    df=df[['pop_2011','pop_2015','pop_2020','pop_2025']].sum()

    fig=px.line(
        x=['2011','2015','2020','2025'],
        y=df,
        title="Madurai Population Growth"
    )

    graph=fig.to_html()

    return render_template('chart.html',graph=graph)


@app.route('/choropleth')
def choropleth():

    import pandas as pd
    import folium
    import json

    data = pd.read_csv("madurai_population_100wards.csv")

    with open("madurai_wards_fixed.geojson") as f:
        geo_json = json.load(f)

    for feature in geo_json["features"]:

        ward = feature["properties"]["ward_no"]

        row = data[data["ward_no"] == ward]

        if not row.empty:

            ward_name = row["ward_name"].values[0]
            councillor = row["councillor"].values[0]
            facilities = row["facilities"].values[0]

            p2011 = int(row["pop_2011"].values[0])
            p2015 = int(row["pop_2015"].values[0])
            p2020 = int(row["pop_2020"].values[0])
            p2025 = int(row["pop_2025"].values[0])

            feature["properties"]["ward_name"] = ward_name
            feature["properties"]["population"] = p2025

            popup_html = f"""
            <b>Ward:</b> {ward_name}<br>
            <b>Councillor:</b> {councillor}<br><br>

            <b>Facilities:</b><br>
            {facilities}<br><br>

            <b>Population:</b><br>
            2011 : {p2011}<br>
            2015 : {p2015}<br>
            2020 : {p2020}<br>
            2025 : {p2025}<br><br>

            <a href="/ward/{ward}" target="_blank">
            <button style="padding:8px;background:#1976d2;color:white;border:none;border-radius:5px;">
            Open Ward Dashboard
            </button>
            </a>
            """

            feature["properties"]["popup"] = popup_html

    m = folium.Map(location=[9.9252,78.1198],zoom_start=12)

    folium.Choropleth(
        geo_data=geo_json,
        data=data,
        columns=['ward_no','pop_2025'],
        key_on='feature.properties.ward_no',
        fill_color='OrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Population Density 2025"
    ).add_to(m)

    folium.GeoJson(
        geo_json,
        style_function=lambda x:{
            "color":"black",
            "weight":1,
            "fillOpacity":0
        },
        highlight_function=lambda x:{
            "fillColor":"blue",
            "color":"blue",
            "weight":3,
            "fillOpacity":0.5
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["ward_name","population"],
            aliases=["Ward:","Population:"]
        ),
        popup=folium.GeoJsonPopup(
            fields=["popup"],
            labels=False
        )
    ).add_to(m)

    m.save("templates/choropleth_map.html")

    return render_template("choropleth_map.html")
    

@app.route('/wardd/<int:ward_no>')
def ward_details(ward_no):

    import pandas as pd

    data = pd.read_csv("madurai_population_100wards.csv")

    ward = data[data["ward_no"] == ward_no].iloc[0]

    return render_template("ward_details.html", ward=ward)

@app.route('/ward/<int:ward_no>')
def ward_page(ward_no):

    import pandas as pd
    import plotly.express as px
    import numpy as np
    from sklearn.linear_model import LinearRegression
    import folium
    import osmnx as ox

    data = pd.read_csv("madurai_population_100wards.csv")

    ward = data[data["ward_no"] == ward_no].iloc[0]

    lat = ward["lat"]
    lon = ward["lon"]

    # -------- Population Graph --------

    years = [2011,2015,2020,2025]

    population = [
        ward["pop_2011"],
        ward["pop_2015"],
        ward["pop_2020"],
        ward["pop_2025"]
    ]

    fig = px.line(
        x=years,
        y=population,
        markers=True,
        title=f"Population Growth - {ward['ward_name']}"
    )

    graph = fig.to_html()

    # -------- AI Prediction till 2040 --------

    X = np.array(years).reshape(-1,1)
    y = np.array(population)

    model = LinearRegression()
    model.fit(X,y)

    pred2030 = int(model.predict([[2030]])[0])
    pred2035 = int(model.predict([[2035]])[0])
    pred2040 = int(model.predict([[2040]])[0])

    # -------- Facility Map + Statistics --------

    m = folium.Map(location=[lat,lon],zoom_start=14)

    schools = 0
    hospitals = 0
    parks = 0
    clinics = 0
    toilet = 0
    anganwadi = 0

    fac = str(ward["facilities"]).lower()

    if "school" in fac:
        schools += 1

    if "hospital" in fac or "phc" in fac:
        hospitals += 1

    if "park" in fac:
        parks += 1
    
    if "toilet" in fac:
        toilet += 1
    
    if "anganwadi" in fac:
        anganwadi += 1

    tags = {
        "amenity":True,
        "leisure":True
    }

    

    try:

        gdf = ox.geometries_from_point((lat,lon),tags=tags,dist=1500)

        for i,row in gdf.iterrows():

            amenity = str(row.get("amenity",""))
            leisure = str(row.get("leisure",""))

            name = row.get("name","Facility")

            lat2 = row.geometry.centroid.y
            lon2 = row.geometry.centroid.x

            icon_color="blue"
            icon="info-sign"

            # -------- Schools --------

            if amenity in ["school","college","university"]:
                schools += 1
                icon_color="green"
                icon="education"

            # -------- Hospitals --------

            elif amenity in ["hospital"]:
                hospitals += 1
                icon_color="red"
                icon="plus"

            # -------- Clinics --------

            elif amenity in ["clinic","doctors"]:
                clinics += 1
                icon_color="orange"
                icon="plus"

            # -------- Parks --------

            if leisure in ["park","garden","playground"]:
                parks += 1
                icon_color="darkgreen"
                icon="tree"

            folium.Marker(
                location=[lat2,lon2],
                popup=name,
                icon=folium.Icon(color=icon_color,icon=icon,prefix="glyphicon")
            ).add_to(m)

    except:
        pass

    m.save("static/facility_map.html")

    # -------- Population Density --------

    density = int(ward["pop_2025"] / 2)

    # -------- Smart Ward Ranking --------

    education_score = schools * 10
    health_score = (hospitals + clinics) * 12
    green_index = parks * 15

    if density < 6000:
        pressure = "Low"
        pressure_score = 30
    elif density < 9000:
        pressure = "Medium"
        pressure_score = 20
    else:
        pressure = "High"
        pressure_score = 10

    smart_score = education_score + health_score + green_index + pressure_score

    rank = 101 - min(100, smart_score // 5)

    return render_template(
        "ward.html",
        ward=ward,
        graph=graph,
        pred2030=pred2030,
        pred2035=pred2035,
        pred2040=pred2040,
        schools=schools,
        hospitals=hospitals,
        parks=parks,
        clinics=clinics,
        density=density,
        education_score=education_score,
        health_score=health_score,
        green_index=green_index,
        pressure=pressure,
        rank=rank,
        anganwadi=anganwadi,
        toilet=toilet
    )

@app.route('/timeline')
def timeline():

    df = pd.read_csv("madurai_population_timeline.csv")
    df["pop_2015"] = df["pop_2015"].astype(int)
    df["pop_2020"] = df["pop_2020"].astype(int)
    df["pop_2025"] = df["pop_2025"].astype(int)
    df.to_csv("madurai_population_timeline.csv",index=False)

    wards = df.to_dict(orient="records")

    return render_template("timeline.html", wards=wards)


def get_facilities(lat, lon):

    point = (lat, lon)

    tags = {
        "amenity": ["hospital","school","college","clinic"],
        "leisure": ["park"]
    }

    gdf = ox.geometries_from_point(point, tags=tags, dist=1000)

    facilities = []

    for i,row in gdf.iterrows():

        name = row.get("name")

        if name:
            facilities.append(name)

    return facilities[:10]



@app.route('/facilities/<int:ward_no>')
def facilities_map(ward_no):

    import pandas as pd
    import folium

    data = pd.read_csv("madurai_population_100wards.csv")

    ward = data[data["ward_no"] == ward_no].iloc[0]

    lat = ward["lat"]
    lon = ward["lon"]

    facilities = get_facilities(lat,lon)

    m = folium.Map(location=[lat,lon],zoom_start=14)

    for f in facilities:

        folium.Marker(
            location=[lat,lon],
            popup=f,
            icon=folium.Icon(color="blue",icon="info-sign")
        ).add_to(m)

    m.save("templates/facilities_map.html")

    return render_template("facilities_map.html")

from sklearn.linear_model import LinearRegression
import numpy as np

def predict_population(row):

    years = np.array([2011,2015,2020,2025]).reshape(-1,1)

    population = np.array([
        row["pop_2011"],
        row["pop_2015"],
        row["pop_2020"],
        row["pop_2025"]
    ])

    model = LinearRegression()

    model.fit(years,population)

    prediction = model.predict([[2030]])

    return int(prediction[0])


@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/')

if __name__=='__main__':
    app.run(debug=True)