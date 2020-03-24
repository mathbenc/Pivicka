from flask import Flask, render_template, jsonify, send_from_directory, make_response
from flask_sslify import SSLify
from flask_compress import Compress
import requests
import json
import time
from operator import add
from datetime import datetime, timedelta, timezone
import sys
import re
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
Compress(app)

data_time = None
data = None
global_data = None
europe_data = None
good_response = True
graph = None
source = None

with open("static/pivicka.json") as json_file:
    country_translations = json.load(json_file)

def process_data(corona_data, country_data, corona_global_data, graph_data_response):
    global data, good_response, global_data, graph, europe_data
    country = []
    country_flag = []
    country_region = []
    country_capital = []
    country_a2_code = []
    country_a3_code = []
    country_translated = []
    country_area = []
    country_density = []
    country_population = []
    infected = []
    infected_today = []
    dead = []
    dead_today = []
    cured = []
    active = []
    critical = []
    infected_ratio = []
    dead_ratio = []
    population_cured_share = []
    population_dead_share = []
    population_healthy_share = []
    data = []
    global_data = []
    graph_data_confirmed = []
    graph_data_dead = []
    graph_data_recovered = []
    graph_countries = []
    graph_dates = []
    europe_data = {
        "cases": 0,
        "deaths": 0,
        "recovered": 0
    }
    graph = {}

    global_data = json.loads(corona_global_data.text)
    country_data = json.loads(country_data.text)
    corona_data = json.loads(corona_data.text)
    graph_data_response = json.loads(graph_data_response.text)

    if len(corona_data) == 0:
        good_response = False
        return
    good_response = True

    # Prilagodimo imena držav
    wrongNames = ["Korea (Republic of)", "Korea (Democratic People's Republic of)", "Iran (Islamic Republic of)", "United Kingdom of Great Britain and Northern Ireland", "Russian Federation", "Viet Nam", "Brunei Darussalam", "Faroe Islands", "Palestine, State of", "United States of America", "Czech Republic", "United Arab Emirates", "Macedonia (the former Yugoslav Republic of)", "Moldova (Republic of)", "Venezuela (Bolivarian Republic of)", "Congo (Democratic Republic of the)", "Bolivia (Plurinational State of)", "Côte d'Ivoire", "Tanzania, United Republic of", "Saint Barthélemy", "Saint Martin (French part)", "Virgin Islands (U.S.)", "Central African Republic", "Holy See", "Saint Vincent and the Grenadines", "Sint Maarten (Dutch part)", "Swaziland"]
    correctNames = ["S. Korea", "North Korea", "Iran", "UK", "Russia", "Vietnam", "Brunei", "Faeroe Islands", "Palestine", "USA", "Czechia", "UAE", "North Macedonia", "Moldova", "Venezuela", "DRC", "Bolivia", "Ivory Coast", "Tanzania", "St. Barth", "Saint Martin", "U.S. Virgin Islands", "CAR", "Vatican City", "St. Vincent Grenadines", "Sint Maarten", "Eswatini"]
    for i in range(len(country_data)):
        for j in range(len(wrongNames)):
            if country_data[i]["name"] == wrongNames[j]:
                country_data[i]["name"] = correctNames[j]
 
    # Polnimo podatke v naše sezname
    for i in range(len(corona_data)):
        for j in range(len(country_data)):
            if corona_data[i]["country"] == country_data[j]["name"]: 
                # Podatki o državi
                country.append(corona_data[i]["country"])
                country_region.append(country_data[j]["region"])
                country_a2_code.append(country_data[j]["alpha2Code"])
                country_a3_code.append(country_data[j]["alpha3Code"])
                country_flag.append(country_data[j]["flag"])
                country_capital.append(country_data[j]["capital"])
                country_population.append(country_data[j]["population"])
                country_area.append(country_data[j]["area"])

                # Podatki o pivu
                infected.append(int(corona_data[i]["cases"]))
                infected_today.append(int(corona_data[i]["todayCases"]))
                dead.append(int(corona_data[i]["deaths"]))
                if corona_data[i]["todayDeaths"] != None:
                    dead_today.append(int(corona_data[i]["todayDeaths"]))
                else:
                    dead_today.append(int(0))
                cured.append(int(corona_data[i]["recovered"]))
                active.append(int(corona_data[i]["active"]))
                critical.append(int(corona_data[i]["critical"]))
                if country_data[j]["region"] == "Europe":
                    europe_data["cases"] += corona_data[i]["cases"]
                    europe_data["deaths"] += corona_data[i]["deaths"]
                    europe_data["recovered"] += corona_data[i]["recovered"]
                
                # Statistika
                infected_ratio.append(round(float(corona_data[i]["cases"] * 100 / country_data[j]["population"]), 5))
                dead_ratio.append(round(float(corona_data[i]["deaths"] * 100 / corona_data[i]["cases"]), 5))
                population_dead_share.append(round(float(corona_data[i]["deaths"] * 100 / country_data[j]["population"]), 5))
                population_healthy_share.append(round(float((country_data[j]["population"] - corona_data[i]["cases"]) * 100 / country_data[j]["population"]), 5))
                population_cured_share.append(round(float(corona_data[i]["recovered"] * 100 / country_data[j]["population"]), 5))
                if country_data[j]["area"] != None:
                    country_density.append(int(country_data[j]["population"] / country_data[j]["area"]))
                else:
                    country_density.append(0)

    # Spremenimo format datuma
    dates = list(graph_data_response["locations"][0]["timelines"]["confirmed"]["timeline"].keys())
    for k in range(len(dates)):
        dates[k] = dates[k][8:10]+"."+dates[k][5:7]+"."+dates[k][:4]

    for i in range(len(graph_data_response["locations"])):
        for j in range(len(country_a2_code)):
            if graph_data_response["locations"][i]["country_code"] == country_a2_code[j]:
                # Če obstaja, posodobimo številke
                if graph_data_response["locations"][i]["country_code"] in graph_countries:
                    index = graph_countries.index(graph_data_response["locations"][i]["country_code"])     
                    graph_data_confirmed[index] = list(map(add, graph_data_confirmed[index], list(graph_data_response["locations"][i]["timelines"]["confirmed"]["timeline"].values())))
                    graph_data_dead[index] = list(map(add, graph_data_dead[index], list(graph_data_response["locations"][i]["timelines"]["deaths"]["timeline"].values())))
                    graph_data_recovered[index] = list(map(add, graph_data_recovered[index], list(graph_data_response["locations"][i]["timelines"]["recovered"]["timeline"].values())))

                # Drugače dodamo novo
                else:
                    graph_countries.append(graph_data_response["locations"][i]["country_code"])
                    country_graph_data_confirmed = list(graph_data_response["locations"][i]["timelines"]["confirmed"]["timeline"].values())
                    country_graph_data_dead = list(graph_data_response["locations"][i]["timelines"]["deaths"]["timeline"].values())
                    country_graph_data_recovered = list(graph_data_response["locations"][i]["timelines"]["recovered"]["timeline"].values())
                    graph_data_confirmed.append(country_graph_data_confirmed)
                    graph_data_dead.append(country_graph_data_dead)
                    graph_data_recovered.append(country_graph_data_recovered)

    # Številom dodamo vejice
    for i in range(len(infected)):
        infected[i] = '{:,}'.format(infected[i])
        infected_today[i] = '{:,}'.format(infected_today[i])
        dead[i] = '{:,}'.format(dead[i])
        dead_today[i] = '{:,}'.format(dead_today[i])
        cured[i] = '{:,}'.format(cured[i])
        active[i] = '{:,}'.format(active[i])
        critical[i] = '{:,}'.format(critical[i])
        country_population[i] = '{:,}'.format(country_population[i])
        country_density[i] = '{:,}'.format(country_density[i])
    europe_data["cases"] = '{:,}'.format(europe_data["cases"])
    europe_data["deaths"] = '{:,}'.format(europe_data["deaths"])
    europe_data["recovered"] = '{:,}'.format(europe_data["recovered"])
        

    global_data["cases"] = '{:,}'.format(global_data["cases"])
    global_data["deaths"] = '{:,}'.format(global_data["deaths"])
    global_data["recovered"] = '{:,}'.format(global_data["recovered"])

    # Preverimo razliko števila držav
    missingCountries = len(corona_data) - len(infected)
    if missingCountries > 7:
        print("MANJKAJO DRZAVE!!!! ->", missingCountries)
        missingCountries = []
        for i in range(len(corona_data)):
            found = False
            for j in range(len(country)):
                if corona_data[i]["country"] == country[j]:
                    found = True
                    break
            
            if not found:
                missingCountries.append(corona_data[i]["country"])

        print("Manjka: ", len(missingCountries), " -> ", missingCountries)
        sys.stdout.flush()

    # Prevedemo imena držav
    for i in range(len(country)):
        for j in range(len(country_translations)):
            if country_a3_code[i] == country_translations[j]["COUNTRY_ALPHA3_CODE"]:
                country_translated.append(country_translations[j]["COUNTRY_NAME"])
                break

    print("Data process complete")
    sys.stdout.flush()

    # Ustvarimo JSON za graf
    dates = {
        "dates": dates
    }
    for i in range(len(graph_countries)):
        content = {
            graph_countries[i]: {
                "confirmed": graph_data_confirmed[i],
                "dead": graph_data_dead[i],
                "recovered": graph_data_recovered[i]
            }
        }
        graph.update(content)
    graph.update(dates)
    graph = json.dumps(graph)

    # Ustvarimo JSON
    for i in range(len(country)):
        content = {
            "name": country[i],
            "countryPopulation": country_population[i],
            "area": country_area[i],
            "flag": country_flag[i],
            "capital": country_capital[i],
            "region": country_region[i],
            "A2code": country_a2_code[i],
            "A3code": country_a3_code[i],
            "slovenianName": country_translated[i],
            "density": country_density[i],
            "infected": infected[i],
            "infectedToday": infected_today[i],
            "infectedRatio": infected_ratio[i],
            "dead": dead[i],
            "deadToday": dead_today[i],
            "deadRatio": dead_ratio[i],
            "cured": cured[i],
            "critical": critical[i],
            "active": active[i],
            "populationHealthyShare": population_healthy_share[i],
            "populationCuredShare": population_cured_share[i],
            "populationDeadShare": population_dead_share[i]
        }
        data.append(content)
    data = json.dumps(data)

def get_data():
    global data_time, source
    country_response = requests.get("https://restcountries.eu/rest/v2/all") 
    try:
        corona_response = requests.get("https://corona.lmao.ninja/countries") #https://coronavirus-19-api.herokuapp.com/countries
        source="https://corona.lmao.ninja/countries"
    except Exception:
        corona_response = requests.get("https://coronavirus-19-api.herokuapp.com/countries")
        source="https://coronavirus-19-api.herokuapp.com/countries"
    corona_global_data = requests.get("https://coronavirus-19-api.herokuapp.com/all")
    graph_data = requests.get("https://coronavirus-tracker-api.herokuapp.com/v2/locations?timelines=1") #https://coronavirus-tracker-api.herokuapp.com/all
    now = datetime.now() + timedelta(hours=1)
    data_time = now.strftime("%d.%m.%Y %H:%M")
    process_data(corona_response, country_response, corona_global_data, graph_data)
    print("API Update complete")
    sys.stdout.flush()

get_data()

sched = BackgroundScheduler()
sched.add_job(get_data, "interval", minutes=10, max_instances=10)
sched.start()

@app.route('/')
def index():
    return render_template("index.html", 
        title="Pivička",
        data=data,
        globalData=global_data,
        europeData=europe_data,
        dataTime=data_time,
        graphData=graph,
        goodResponse=good_response,
        source=source)

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory("static", "sitemap.xml")

@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt")

@app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json")

@app.route("/sw.js")
def service_worker():
    response = make_response(send_from_directory('static', 'sw.js'))
    response.headers['Cache-Control'] = 'no-cache'
    return response

#app.config['TEMPLATES_AUTO_RELOAD'] = True
sslify = SSLify(app)

if __name__ == '__main__':
    app.run()