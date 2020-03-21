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

countries = []
countriesFlags = []
countriesCapitals = []
countriesA2Codes = []
countriesA3Codes = []
countriesTranslated = []
countriesArea = []
countriesDensity = []
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
whole_data = []

country_response = None
corona_response = None
good_response = True

with open("static/pivicka.json") as json_file:
    country_translations = json.load(json_file)

def process_data():
    global whole_data, countries, countriesFlags, countriesA2Codes, countriesA3Codes, countriesCapitals, countriesTranslated, countriesArea, countriesDensity, population, infected, infectedToday, dead, deadToday, cured, active, critical, infectedRatio, deadRatio, populationCuredShare, populationDeadShare, populationHealthyShare, country_response, corona_response, good_response
    countries.clear()
    countriesFlags.clear()
    countriesCapitals.clear()
    countriesA2Codes.clear()
    countriesA3Codes.clear()
    countriesTranslated.clear()
    countriesArea.clear()
    countriesDensity.clear()
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
    whole_data.clear()
    
    country_data = json.loads(country_response.text)
    corona_data = json.loads(corona_response.text)

    if len(corona_data) == 0:
        good_response = False
        return
    good_response = True

    # DODAJ DVA SEZNAMA, PRAVILNIH IN NAPAČNIH IMEN, DA SE IZOGNEŠ ELIFOM!!!

    wrongNames = ["Korea (Republic of)", "Korea (Democratic People's Republic of)", "Iran (Islamic Republic of)", "United Kingdom of Great Britain and Northern Ireland", "Russian Federation", "Viet Nam", "Brunei Darussalam", "Faroe Islands", "Palestine, State of", "United States of America", "Czech Republic", "United Arab Emirates", "Macedonia (the former Yugoslav Republic of)", "Moldova (Republic of)", "Venezuela (Bolivarian Republic of)", "Congo (Democratic Republic of the)", "Bolivia (Plurinational State of)", "Côte d'Ivoire", "Tanzania, United Republic of", "Saint Barthélemy", "Saint Martin (French part)", "Virgin Islands (U.S.)", "Central African Republic", "Holy See", "Saint Vincent and the Grenadines", "Sint Maarten (Dutch part)", "Swaziland"]
    correctNames = ["S. Korea", "North Korea", "Iran", "UK", "Russia", "Vietnam", "Brunei", "Faeroe Islands", "Palestine", "USA", "Czechia", "UAE", "North Macedonia", "Moldova", "Venezuela", "DRC", "Bolivia", "Ivory Coast", "Tanzania", "St. Barth", "Saint Martin", "U.S. Virgin Islands", "CAR", "Vatican City", "St. Vincent Grenadines", "Sint Maarten", "Eswatini"]

    # Prilagodimo imena držav
    for i in range(len(country_data)):
        for j in range(len(wrongNames)):
            if country_data[i]["name"] == wrongNames[j]:
                country_data[i]["name"] = correctNames[j]
 
    # Polnimo podatke v naše sezname
    for i in range(len(corona_data)):
        for j in range(len(country_data)):
            if corona_data[i]["country"] == country_data[j]["name"]: 
                # Podatki o državi
                countries.append(corona_data[i]["country"])
                countriesA2Codes.append(country_data[j]["alpha2Code"])
                countriesA3Codes.append(country_data[j]["alpha3Code"])
                countriesFlags.append(country_data[j]["flag"])
                countriesCapitals.append(country_data[j]["capital"])
                population.append(country_data[j]["population"])
                countriesArea.append(country_data[j]["area"])

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
                if country_data[j]["area"] != None:
                    countriesDensity.append(round(float(country_data[j]["population"] / country_data[j]["area"])))
                else:
                    countriesDensity.append("0")

    for i in range(len(infected)):
        infected[i] = '{:,}'.format(infected[i])
        infectedToday[i] = '{:,}'.format(infectedToday[i])
        dead[i] = '{:,}'.format(dead[i])
        deadToday[i] = '{:,}'.format(deadToday[i])
        cured[i] = '{:,}'.format(cured[i])
        active[i] = '{:,}'.format(active[i])
        critical[i] = '{:,}'.format(critical[i])
        population[i] = '{:,}'.format(population[i])


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
        countriesCapitals=countriesCapitals,
        countriesDensity=countriesDensity,
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

#app.config['TEMPLATES_AUTO_RELOAD'] = True
sslify = SSLify(app)

if __name__ == '__main__':
    app.run()