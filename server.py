from flask import Flask, render_template, jsonify, send_from_directory, make_response
from flask_sslify import SSLify
from flask_compress import Compress
import requests
import json
import time
from datetime import datetime, timedelta, timezone
import sys
import re
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
Compress(app)

data_time = None
data = None
global_data = None
good_response = True
graph_data = None

with open("static/pivicka.json") as json_file:
    country_translations = json.load(json_file)

def process_data(corona_data, country_data, corona_global_data):
    global data, good_response, global_data, graph_data
    country = []
    country_flag = []
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
    graph_data = []

    global_data = json.loads(corona_global_data.text)
    country_data = json.loads(country_data.text)
    corona_data = json.loads(corona_data.text)

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
    
    

    """
        graph_data_response = json.loads(requests.get("https://coronavirus-tracker-api.herokuapp.com/v2/locations?country_code="+country_a2_code[i]+"&timelines=true").text)
        if len(graph_data_response["locations"]) == 1:
            graph_data.append(graph_data_response["locations"][0]["timelines"]["confirmed"]["timeline"])
        else:
            graph_data.append("none")
    """
    #Nimamo zadosti točnih podatkov!!!!
    """
    graph_data_response = json.loads(requests.get("https://coronavirus-tracker-api.herokuapp.com/v2/locations?country_code=si&timelines=true").text)
    graph_data.append(graph_data_response["locations"][0]["timelines"]["confirmed"]["timeline"])
    for i in range(len(graph_data[0])):
        dt = datetime(2020, 1, 22, 0, 0, 0, 0, tzinfo=timezone.utc) + timedelta(days=i)
        dt = str(dt).replace(" ", "T")[:-6]+"Z"
        print(dt, "->", graph_data[0][dt])
    # Zdaj ko imamo podatke za vsako državo, moramo izluščiti le število in datum.
    print(graph_data[0]["2020-01-22T00:00:00Z"])
    """

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

    # Ustvarimo JSON
    for i in range(len(country)):
        content = {
            "name": country[i],
            "countryPopulation": country_population[i],
            "area": country_area[i],
            "flag": country_flag[i],
            "capital": country_capital[i],
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
    global data_time
    country_response = requests.get("https://restcountries.eu/rest/v2/all")
    corona_response = requests.get("https://coronavirus-19-api.herokuapp.com/countries")
    corona_global_data = requests.get("https://coronavirus-19-api.herokuapp.com/all")
    now = datetime.now() + timedelta(hours=1)
    data_time = now.strftime("%d.%m.%Y %H:%M")
    process_data(corona_response, country_response, corona_global_data)
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
        dataTime=data_time,
        goodResponse=good_response)

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