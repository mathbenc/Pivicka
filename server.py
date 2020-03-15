from flask import Flask, render_template, jsonify
from flask_sslify import SSLify
import requests
import time
import datetime
import sys
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
#app.config['TEMPLATES_AUTO_RELOAD'] = True
sslify = SSLify(app)

def get_data():
    global corona_response, country_response, data_time
    country_response = requests.get("https://restcountries.eu/rest/v2/all")
    corona_response = requests.get("https://lab.isaaclin.cn/nCoV/api/area?")
    now = datetime.datetime.now() + datetime.timedelta(hours=1)
    data_time = now.strftime("%d.%m.%Y %H:%M")
    print("API Update complete")
    sys.stdout.flush()

country_response = requests.get("https://restcountries.eu/rest/v2/all")
corona_response = requests.get("https://lab.isaaclin.cn/nCoV/api/area?")
now = datetime.datetime.now() + datetime.timedelta(hours=1)
data_time = now.strftime("%d.%m.%Y %H:%M")

@app.route('/')
def index():
    return render_template("index.html", 
        title="Pivička", 
        corona_data=corona_response.text, 
        country_data=country_response.text,
        data_time=data_time)

sched = BackgroundScheduler()
sched.add_job(get_data, "interval", minutes=1, max_instances=10)
sched.start()

if __name__ == '__main__':
    app.run()