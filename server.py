from flask import Flask, render_template, jsonify
from flask_sslify import SSLify
import requests
import time
import sys
from apscheduler.schedulers.blocking import BlockingScheduler

app = Flask(__name__)
#app.config['TEMPLATES_AUTO_RELOAD'] = True
sslify = SSLify(app)

sched = BlockingScheduler()

def get_data():
    global corona_response, country_response
    country_response = requests.get("https://restcountries.eu/rest/v2/all")
    corona_response = requests.get("https://lab.isaaclin.cn/nCoV/api/area?")
    print("API Update complete")
    sys.stdout.flush()

country_response = requests.get("https://restcountries.eu/rest/v2/all")
corona_response = requests.get("https://lab.isaaclin.cn/nCoV/api/area?")

@app.route('/')
def index():
    return render_template("index.html", 
        title="Pivička", 
        corona_data=corona_response.text, 
        country_data=country_response.text)

sched.add_job(get_data, "interval", minute=10, max_instances=10)
sched.start()

if __name__ == '__main__':
    app.run()