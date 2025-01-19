import requests
import folium
import webbrowser
import os
import geopandas as gpd
import osmnx as ox
r = 1

weather_api_key = "aca02f774ce3ad4985ba560f68b634ac"
weather_root_url = "https://api.openweathermap.org/data/2.5/weather?"
city_name = input("City: ")
url = f"{weather_root_url}appid={weather_api_key}&q={city_name}"
r = requests.get(url)
weather_root_url2 = "https://api.openweathermap.org/data/2.5/forecast?"

data = r.json()
def risk(t,h,p,w,r):
    ris = 0
    if t<20:
        ris+=1
    elif t > 20 and  t< 30:
        ris += 2
    else:
        ris+= 4
    if h > 60:
        ris+=1
    elif h <=60 and h>=30:
        ris+=2
    elif h < 30:
        ris+=3
    if w < 15:
        ris+= 1
    elif w >= 15 and w <= 30:
        ris+=2
    elif w > 30 and w <= 50:
        ris+=3
    else :
        ris+= 4
    if p < 1013:
        ris+=2
    elif p == 1013:
        ris += 1
    else:
        ris+=0
    if(r == 0):
        ris = 0
    if(ris/4) <= 1:
        return(0)
    elif(ris/4) >1 and ris/4 <= 2:
        return(2)
    elif ris/4 > 2 and ris/4 < 3:
        return(2)
    else:
        return(3)


def get_city_boundary(city_name):
    try:
       # Fetch the city boundary
       gdf = ox.geocode_to_gdf(city_name)
       return gdf
    except Exception as e:
       print(f"Error fetching data for {city_name}: {e}")
       return None

def create_map(city_name, col):
        gdf = get_city_boundary(city_name)

        if gdf is not None and not gdf.empty:
            # Create a base map
            center_point = gdf.geometry.centroid.iloc[0]
            m = folium.Map(location=[center_point.y, center_point.x], zoom_start=10)

            # Add the city boundary to the map
            folium.GeoJson(
                gdf,
                name='City Boundary',
                style_function=lambda x: {'fillColor': col, 'color': 'black', 'weight': 2, 'fillOpacity': 0.1}
            ).add_to(m)

            # Add layer control
            folium.LayerControl().add_to(m)

            # Save the map
            output_file = f'{city_name.replace(" ", "_")}_boundary_map.html'
            m.save(output_file)
            print(f"Map saved as {output_file}")
        else:
            print(f"Unable to create map for {city_name}")

if r.json()['cod'] == 200:
    lo = data['coord']['lon']
    la = data['coord']['lat']
    url2 = f"{weather_root_url2}appid={weather_api_key}&q={city_name}"
    rr = requests.get(url2)
    data2 = rr.json()
    print(data2)
    m = folium.Map(location = [la,lo],zoom_start=12)
    if(data['weather'][0]['main'] == "Clouds"):
        folium.Marker([la+0.01,lo+0.01],popup = city_name,icon = folium.Icon(icon='cloud',color = 'blue')).add_to(m)
    if data['weather'][0]['main'] == 'Clear':
        folium.Marker([la,lo],popup = city_name,icon = folium.Icon(icon = 'sun',color = 'orange')).add_to(m)
    if data['weather'][0]['main'] == 'Rain':
        folium.Marker([la, lo], popup=city_name, icon=folium.Icon(icon='rain', color='beige')).add_to(m)
    if data['weather'][0]['main'] == 'Thunderstorm':
        folium.Marker([la, lo], popup=city_name, icon=folium.Icon(icon='cloud-showers-heavy', color='beige')).add_to(m)
    if data['weather'][0]['main'] == 'Snow':
        folium.Marker([la, lo], popup=city_name, icon=folium.Icon(icon='snowflake', color='blue')).add_to(m)
    if data['weather'][0]['main'] == 'Mist':
        folium.Marker([la, lo], popup=city_name, icon=folium.Icon(icon='cloud', color='beige')).add_to(m)
    url = "https://data.cityofnewyork.us/api/geospatial/tqmj-j8zm?method=export&format=GeoJSON"
    gdf = gpd.read_file(url)

    # Add the city boundaries to the map

    def tempnum(a):
        return data2['list'][a]['main']['temp'] - 273.15

    def hnum(a):
        return data2['list'][a]['main']['humidity']

    def pnum(a):
        return data2['list'][a]['main']['pressure']

    def wnum(a):
        return data2['list'][a]['wind']['speed']
    print(data)
    print(data2)
    weather_r = data['weather'][0]['main']
    if(weather_r == "Rain"):
        a = data['rain']['1h']
        print(f" Rain is {a} mm/hr")
        r = 0

    if (weather_r == "Snow"):
        a = data['snow']['1h']
        print(f" Snow is {a} mm/hr")
        r = 0

    temp = data['main']['temp'] - 273.15
    humid = data['main']['humidity']
    weather_d = data['weather'][0]['description']
    print(weather_d)
    wi = data['wind']['speed'] * 3.6
    pressure = data['main']['pressure']
    print(f" Temperature: {round(temp)} degrees C")
    print(f" Humidity: {humid}%")
    print(f" Wind: {wi} km/hr")
    risk_factor = risk(temp,humid,pressure,wi,r)

#   Write code to print level of risk

    for i in range(8):
        risk(tempnum(i), hnum(i), pnum(i), wnum(i), r)
    if risk(temp, humid, pressure, wi, r) == 0:
        create_map(city_name, 'green')
    elif risk(temp,humid,pressure,wi,r) == 1:
        create_map(city_name, 'orange')
    elif risk(temp, humid, pressure, wi, r) == 2:
        create_map(city_name, 'red')
    else:
        create_map(city_name, 'black')

    file_path = os.path.abspath(f'{city_name.replace(" ", "_")}_boundary_map.html')
    webbrowser.open(f"file://{file_path}")

else:
    print("Something went wrong... please try another city")

'''
### Code to display map start ###
def get_city_boundary(city_name):
    try:
        # Fetch the city boundary
        gdf = ox.geocode_to_gdf(city_name)
        return gdf
    except Exception as e:
        print(f"Error fetching data for {city_name}: {e}")
        return None


def create_map(city_name,col):
    gdf = get_city_boundary(city_name)

    if gdf is not None and not gdf.empty:
        # Create a base map
        center_point = gdf.geometry.centroid.iloc[0]
        m = folium.Map(location=[center_point.y, center_point.x], zoom_start=10)

        # Add the city boundary to the map
        folium.GeoJson(
            gdf,
            name='City Boundary',
            style_function=lambda x: {'fillColor': col, 'color': 'black', 'weight': 2, 'fillOpacity': 0.4}
        ).add_to(m)

        # Add layer control
        folium.LayerControl().add_to(m)

        # Save the map
        output_file = f'{city_name.replace(" ", "_")}_boundary_map.html'
        m.save(output_file)
        print(f"Map saved as {output_file}")
    else:
        print(f"Unable to create map for {city_name}")

### Code to display map end ###

### Extra functions

def svaporpressure(t):
    a = 6.116441 * (2.71820182 ** ((17.502 * t) / (t + 240.97)))
    return a
def avaporpressure(t,h):
    e = (h) * svaporpressure(t)
    return e
def specifichumidity(t,h,p):
    q = (0.622 * svaporpressure(t)/(p-svaporpressure(t)))
    return q
def density(p,t):
    b = p/(287.05*(t))
    return b
def v (t,p):
    return -density(p,t)*9.81

def rainfall(t,h,p):
    rai =  specifichumidity(t,h,p)*v(t,p) *density(p,t) * 3600
    if rai < 0:
        rai = 0
    print(rai)
    '''