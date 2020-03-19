from flask import Flask, render_template, jsonify, send_from_directory, make_response
from flask_sslify import SSLify
from flask_sitemap import Sitemap
from flask_compress import Compress
import requests
import json
import time
from datetime import datetime, timedelta, timezone
import sys
import re
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
ext = Sitemap(app=app)
Compress(app)
#app.config['TEMPLATES_AUTO_RELOAD'] = True
sslify = SSLify(app)

countries = []
countriesFlags = []
countriesA2Codes = []
countriesA3Codes = []
countriesTranslated = []
graphData = []
population = []
infected = []
infectedToday = []
dead = []
deadToday = []
cured = []
active = []
critical = []
infectedRatio = []
deadRatio = []
populationDeadShare = []
populationCuredShare = []
populationHealthyShare = []

country_response = None
corona_response = None
good_response = True

with open("static/pivicka.json") as json_file:
    country_translations = json.load(json_file)

def process_data():
    global countries, population, infected, infectedToday, dead, deadToday, cured, active, critical, infectedRatio, deadRatio, populationCuredShare, populationDeadShare, populationHealthyShare, country_response, corona_response, good_response
    countries.clear()
    countriesFlags.clear()
    countriesA2Codes.clear()
    countriesA3Codes.clear()
    countriesTranslated.clear()
    graphData.clear()
    population.clear()
    infected.clear()
    infectedToday.clear()
    dead.clear()
    deadToday.clear()
    cured.clear()
    active.clear()
    critical.clear()
    infectedRatio.clear()
    deadRatio.clear()
    populationCuredShare.clear()
    populationDeadShare.clear()
    populationHealthyShare.clear()
    
    country_data = json.loads(country_response.text)
    corona_data = json.loads(corona_response.text)

    if len(corona_data) == 0:
        good_response = False
        return
    good_response = True

    # Prilagodimo imena držav
    for i in range(len(country_data)):
        if country_data[i]["name"] == "Korea (Republic of)":
            country_data[i]["name"] = "S. Korea"
        elif country_data[i]["name"] == "Korea (Democratic People's Republic of)":
            country_data[i]["name"] = "North Korea"
        elif country_data[i]["name"] == "Iran (Islamic Republic of)":
            country_data[i]["name"] = "Iran"
        elif country_data[i]["name"] == "United Kingdom of Great Britain and Northern Ireland":
            country_data[i]["name"] = "UK"
        elif country_data[i]["name"] == "Russian Federation":
            country_data[i]["name"] = "Russia"
        elif country_data[i]["name"] == "Viet Nam":
            country_data[i]["name"] = "Vietnam"
        elif country_data[i]["name"] == "Brunei Darussalam":
            country_data[i]["name"] = "Brunei"
        elif country_data[i]["name"] == "Faroe Islands":
            country_data[i]["name"] = "Faeroe Islands"
        elif country_data[i]["name"] == "Palestine, State of":
            country_data[i]["name"] = "Palestine"
        elif country_data[i]["name"] == "United States of America":
            country_data[i]["name"] = "USA"
        elif country_data[i]["name"] == "Czech Republic":
            country_data[i]["name"] = "Czechia"
        elif country_data[i]["name"] == "United Arab Emirates":
            country_data[i]["name"] = "UAE"
        elif country_data[i]["name"] == "Macedonia (the former Yugoslav Republic of)":
            country_data[i]["name"] = "North Macedonia"
        elif country_data[i]["name"] == "Moldova (Republic of)":
            country_data[i]["name"] = "Moldova"
        elif country_data[i]["name"] == "Venezuela (Bolivarian Republic of)":
            country_data[i]["name"] = "Venezuela"
        elif country_data[i]["name"] == "Congo (Democratic Republic of the)":
            country_data[i]["name"] = "DRC"
        elif country_data[i]["name"] == "Bolivia (Plurinational State of)":
            country_data[i]["name"] = "Bolivia"
        elif country_data[i]["name"] == "Côte d'Ivoire":
            country_data[i]["name"] = "Ivory Coast"
        elif country_data[i]["name"] == "Tanzania, United Republic of":
            country_data[i]["name"] = "Tanzania"
        elif country_data[i]["name"] == "Saint Barthélemy":
            country_data[i]["name"] = "St. Barth"
        elif country_data[i]["name"] == "Saint Martin (French part)":
            country_data[i]["name"] = "Saint Martin"
        elif country_data[i]["name"] == "Virgin Islands (U.S.)":
            country_data[i]["name"] = "U.S. Virgin Islands"
        elif country_data[i]["name"] == "Central African Republic":
            country_data[i]["name"] = "CAR"
        elif country_data[i]["name"] == "Holy See":
            country_data[i]["name"] = "Vatican City"
        elif country_data[i]["name"] == "Saint Vincent and the Grenadines":
            country_data[i]["name"] = "St. Vincent Grenadines"
        elif country_data[i]["name"] == "Sint Maarten (Dutch part)":
            country_data[i]["name"] = "Sint Maarten"
        elif country_data[i]["name"] == "Swaziland":
            country_data[i]["name"] = "Eswatini"
 
    # Polnimo podatke v naše sezname
    for i in range(len(corona_data)):
        for j in range(len(country_data)):
            #regex = re.search("^"+corona_data[i]["country"]+".*$", country_data[j]["name"])
            #if regex != None:
            if corona_data[i]["country"] == country_data[j]["name"]: 
                # Podatki o državi
                countries.append(corona_data[i]["country"])
                countriesA2Codes.append(country_data[j]["alpha2Code"])
                countriesA3Codes.append(country_data[j]["alpha3Code"])
                countriesFlags.append(country_data[j]["flag"])
                population.append(country_data[j]["population"])

                # Podatki o pivu
                infected.append(int(corona_data[i]["cases"]))
                infectedToday.append(int(corona_data[i]["todayCases"]))
                dead.append(int(corona_data[i]["deaths"]))
                if corona_data[i]["todayDeaths"] != None:
                    deadToday.append(int(corona_data[i]["todayDeaths"]))
                else:
                    deadToday.append(int(0))
                cured.append(int(corona_data[i]["recovered"]))
                active.append(int(corona_data[i]["active"]))
                critical.append(int(corona_data[i]["critical"]))
                
                # Statistika
                infectedRatio.append(round(float(corona_data[i]["cases"] * 100 / country_data[j]["population"]), 5))
                deadRatio.append(round(float(corona_data[i]["deaths"] * 100 / corona_data[i]["cases"]), 5))
                populationDeadShare.append(round(float(corona_data[i]["deaths"] * 100 / country_data[j]["population"]), 5))
                populationHealthyShare.append(round(float((country_data[j]["population"] - corona_data[i]["cases"]) * 100 / country_data[j]["population"]), 5))
                populationCuredShare.append(round(float(corona_data[i]["recovered"] * 100 / country_data[j]["population"]), 5))

    for i in range(len(infected)):
        infected[i] = '{:,}'.format(infected[i])
        infectedToday[i] = '{:,}'.format(infectedToday[i])
        dead[i] = '{:,}'.format(dead[i])
        deadToday[i] = '{:,}'.format(deadToday[i])
        cured[i] = '{:,}'.format(cured[i])
        active[i] = '{:,}'.format(active[i])
        critical[i] = '{:,}'.format(critical[i])
        population[i] = '{:,}'.format(population[i])
        
        """
        graph_data_response = json.loads(requests.get("https://coronavirus-tracker-api.herokuapp.com/v2/locations?country_code="+countriesA2Codes[i]+"&timelines=true").text)
        if len(graph_data_response["locations"]) == 1:
            graphData.append(graph_data_response["locations"][0]["timelines"]["confirmed"]["timeline"])
        else:
            graphData.append("none")

    #Nimamo zadosti točnih podatkov!!!!

    
    graph_data_response = json.loads(requests.get("https://coronavirus-tracker-api.herokuapp.com/v2/locations?country_code=si&timelines=true").text)
    graphData.append(graph_data_response["locations"][0]["timelines"]["confirmed"]["timeline"])

    for i in range(len(graphData[0])):
        dt = datetime(2020, 1, 22, 0, 0, 0, 0, tzinfo=timezone.utc) + timedelta(days=i)
        dt = str(dt).replace(" ", "T")[:-6]+"Z"
        print(dt, "->", graphData[0][dt])

    # Zdaj ko imamo podatke za vsako državo, moramo izluščiti le število in datum.

    print(graphData[0]["2020-01-22T00:00:00Z"])
    """

    # Preverimo razliko števila držav
    missingCountries = len(corona_data) - len(infected)
    if missingCountries > 7:
        print("MANJKAJO DRZAVE!!!! ->", missingCountries)
        missingCountries = []
        for i in range(len(corona_data)):
            found = False
            for j in range(len(countries)):
                if corona_data[i]["country"] == countries[j]:
                    found = True
                    break
            
            if not found:
                missingCountries.append(corona_data[i]["country"])

        print("Manjka: ", len(missingCountries), " -> ", missingCountries)
        sys.stdout.flush()

    # Prevedemo imena držav
    for i in range(len(countries)):
        for j in range(len(country_translations)):
            if countriesA3Codes[i] == country_translations[j]["COUNTRY_ALPHA3_CODE"]:
                countriesTranslated.append(country_translations[j]["COUNTRY_NAME"])
                break

    print("Data process complete")
    sys.stdout.flush()

    print(len(countries))
    print(len(countriesTranslated))

def get_data():
    global corona_response, country_response, data_time
    country_response = requests.get("https://restcountries.eu/rest/v2/all")
    corona_response = requests.get("https://coronavirus-19-api.herokuapp.com/countries")
    now = datetime.now() + timedelta(hours=1)
    data_time = now.strftime("%d.%m.%Y %H:%M")
    process_data()
    print("API Update complete")
    sys.stdout.flush()

get_data()

@app.route('/')
def index():
    return render_template("index.html", 
        title="Pivička",
        corona_data = corona_response.text,
        data_time=data_time,
        countries=countries,
        countriesTranslated=countriesTranslated,
        countriesFlags=countriesFlags,
        population=population,
        infected=infected,
        infectedToday=infectedToday,
        dead=dead,
        deadToday=deadToday,
        cured=cured,
        active=active,
        critical=critical,
        infectedRatio=infectedRatio,
        deadRatio=deadRatio,
        populationDeadShare=populationDeadShare,
        populationCuredShare=populationCuredShare,
        populationHealthyShare=populationHealthyShare,
        goodResponse=good_response)

@ext.register_generator
def sitemap():
    yield 'index', {}

@app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json")

@app.route("/sw.js")
def service_worker():
    response = make_response(send_from_directory('static', 'sw.js'))
    response.headers['Cache-Control'] = 'no-cache'
    return response

sched = BackgroundScheduler()
sched.add_job(get_data, "interval", minutes=10, max_instances=10)
sched.start()

if __name__ == '__main__':
    app.run()