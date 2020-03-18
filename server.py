from flask import Flask, render_template, jsonify, send_from_directory, make_response
from flask_sslify import SSLify
from flask_sitemap import Sitemap
from flask_compress import Compress
import requests
import json
import time
import datetime
import sys
import re
from apscheduler.schedulers.background import BackgroundScheduler
from googletrans import Translator

app = Flask(__name__)
ext = Sitemap(app=app)
Compress(app)
#app.config['TEMPLATES_AUTO_RELOAD'] = True
sslify = SSLify(app)

# API za risanje grafa poteka okužbe
#https://coronavirus-tracker-api.herokuapp.com/all

countries = []
countriesTranslated = []
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

def process_data():
    global countries, population, infected, infectedToday, dead, deadToday, cured, active, critical, infectedRatio, deadRatio, populationCuredShare, populationDeadShare, populationHealthyShare, country_response, corona_response, good_response
    countries.clear()
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

    #? Prilagodimo imena držav
    for i in range(len(country_data)):
        if country_data[i]["name"] == "Korea (Republic of)":
            country_data[i]["name"] = "South Korea"
        elif country_data[i]["name"] == "Korea (Democratic People's Republic of)":
            country_data[i]["name"] = "North Korea"
    for i in range(len(corona_data)):
        if corona_data[i]["country"] == "S. Korea":
            corona_data[i]["country"] = "South Korea"
        elif corona_data[i]["country"] == "UK":
            corona_data[i]["country"] = "United Kingdom"
        elif corona_data[i]["country"] == "USA":
            corona_data[i]["country"] = "United States of America"
 
    #? Polnimo podatke v naše sezname
    for i in range(len(corona_data)):
        for j in range(len(country_data)):
            regex = re.search("^"+corona_data[i]["country"]+".*$", country_data[j]["name"])
            if regex != None:
                # Podatki o državi
                countries.append(corona_data[i]["country"])
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
        if countries[i] == "Turkey":
            countriesTranslated.append("Turčija")
        elif countries[i] == "Togo":
            countriesTranslated.append("Togo")
        elif countries[i] == "Japan":
            countriesTranslated.append("Japonska")
        else:
            translator = Translator()
            try:
                result = translator.translate(countries[i], src="en", dest="sl").text
            except json.decoder.JSONDecodeError:
                result = countries[i]
                """
        countriesTranslated.append(countries[0])

    print("Data process complete")
    sys.stdout.flush()

def get_data():
    global corona_response, country_response, data_time
    country_response = requests.get("https://restcountries.eu/rest/v2/all")
    corona_response = requests.get("https://coronavirus-19-api.herokuapp.com/countries")
    now = datetime.datetime.now() + datetime.timedelta(hours=1)
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