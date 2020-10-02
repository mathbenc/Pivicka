from flask import Flask, render_template, jsonify, send_from_directory, make_response
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
continents_data = None
graph = None
graph_global = None
source = None

with open("static/pivicka.json") as json_file:
    country_translations = json.load(json_file)

def process_data(corona_data, corona_yesterday, corona_global_data, corona_continents_data, graph_data):
    global data, graph, global_data, continents_data
    corona_data = json.loads(corona_data.text)
    corona_yesterday = json.loads(corona_yesterday.text)
    graph = graph_data.text
    global_data = json.loads(corona_global_data.text)
    continents_data = json.loads(corona_continents_data.text)

    # Dodamo prevode imen...
    for i in range(len(corona_data)):
        for translation in country_translations:
            if corona_data[i]["countryInfo"]["iso3"] == translation["COUNTRY_ALPHA3_CODE"]:
                corona_data[i]["translation"] = translation["COUNTRY_NAME"]
        for i in range(len(corona_yesterday)):
            if corona_data[i]["country"] == corona_yesterday[i]["country"]:
                corona_data[i]["newTests"] = corona_data[i]["tests"] - corona_yesterday[i]["tests"]

    # Številom dodamo vejice
    for i in range(len(corona_data)):
        corona_data[i]["cases"] = '{:,}'.format(corona_data[i]["cases"])
        corona_data[i]["todayCases"] = '{:,}'.format(corona_data[i]["todayCases"])
        corona_data[i]["deaths"] = '{:,}'.format(corona_data[i]["deaths"])
        corona_data[i]["todayDeaths"] = '{:,}'.format(corona_data[i]["todayDeaths"])
        corona_data[i]["recovered"] = '{:,}'.format(corona_data[i]["recovered"])
        corona_data[i]["todayRecovered"] = '{:,}'.format(corona_data[i]["todayRecovered"])
        corona_data[i]["active"] = '{:,}'.format(corona_data[i]["active"])
        corona_data[i]["critical"] = '{:,}'.format(corona_data[i]["critical"])
        corona_data[i]["tests"] = '{:,}'.format(corona_data[i]["tests"])
        corona_data[i]["casesPerOneMillion"] = '{:,}'.format(corona_data[i]["casesPerOneMillion"])
        corona_data[i]["deathsPerOneMillion"] = '{:,}'.format(corona_data[i]["deathsPerOneMillion"])
        corona_data[i]["testsPerOneMillion"] = '{:,}'.format(corona_data[i]["testsPerOneMillion"])
        corona_data[i]["population"] = '{:,}'.format(corona_data[i]["population"])
        corona_data[i]["newTests"] = '{:,}'.format(corona_data[i]["newTests"])

    data = json.dumps(corona_data)

    print("Data process complete")
    sys.stdout.flush()

def get_data():
    global data_time, source
    corona_response = requests.get("https://disease.sh/v3/covid-19/countries")
    corona_response_yesterday = requests.get("https://disease.sh/v3/covid-19/countries?yesterday=1")
    source="https://www.worldometers.info/coronavirus/"   
    corona_global_data = requests.get("https://disease.sh/v3/covid-19/all")
    corona_continents_data = requests.get("https://disease.sh/v3/covid-19/continents")
    graph_data = requests.get("https://disease.sh/v3/covid-19/historical?lastdays=all")
    now = datetime.now() + timedelta(hours=2)
    data_time = now.strftime("%d.%m.%Y %H:%M")
    process_data(corona_response, corona_response_yesterday, corona_global_data, corona_continents_data, graph_data)
    print("API Update complete")
    sys.stdout.flush()

get_data()

sched = BackgroundScheduler()
sched.add_job(get_data, "interval", minutes=5, max_instances=100)
sched.start()

@app.route('/')
def index():
    return render_template("index.html", 
        title="Pivička",
        data=data,
        globalData=global_data,
        continentData=continents_data,
        dataTime=data_time,
        graphData=graph,
        graphGlobal=graph_global,
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

if __name__ == '__main__':
    app.run(debug=False)