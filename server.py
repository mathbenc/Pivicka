from flask import Flask, render_template, jsonify
from flask_sslify import SSLify
from flask_compress import Compress
import requests
import json
import time
import datetime
import sys
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
Compress(app)
#app.config['TEMPLATES_AUTO_RELOAD'] = True
sslify = SSLify(app)

countries = []
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


def process_data():
    global countries, population, infected, infectedToday, dead, deadToday, cured, active, critical, infectedRatio, deadRatio, populationCuredShare, populationDeadShare, populationHealthyShare, country_response, corona_response
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
            if corona_data[i]["country"] == country_data[j]["name"]:
                # Podatki o državi
                countries.append(corona_data[i]["country"])
                population.append(country_data[j]["population"])

                # Podatki o pivu
                infected.append(int(corona_data[i]["cases"]))
                infectedToday.append(int(corona_data[i]["todayCases"]))
                dead.append(int(corona_data[i]["deaths"]))
                deadToday.append(int(corona_data[i]["todayDeaths"]))
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

country_response = requests.get("https://restcountries.eu/rest/v2/all")
corona_response = requests.get("https://coronavirus-19-api.herokuapp.com/countries")
now = datetime.datetime.now() + datetime.timedelta(hours=1)
data_time = now.strftime("%d.%m.%Y %H:%M")

process_data()

def get_data():
    global corona_response, country_response, data_time
    country_response = requests.get("https://restcountries.eu/rest/v2/all")
    corona_response = requests.get("https://coronavirus-19-api.herokuapp.com/countries")
    now = datetime.datetime.now() + datetime.timedelta(hours=1)
    data_time = now.strftime("%d.%m.%Y %H:%M")
    process_data()
    print("API Update complete")
    sys.stdout.flush()

@app.route('/')
def index():
    return render_template("index.html", 
        title="Pivička",
        corona_data = corona_response.text,
        data_time=data_time,
        countries=countries,
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
        populationHealthyShare=populationHealthyShare)

sched = BackgroundScheduler()
sched.add_job(get_data, "interval", minutes=10, max_instances=10)
sched.start()

if __name__ == '__main__':
    app.run()