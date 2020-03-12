from flask import Flask, render_template, jsonify
from flask_sslify import SSLify
import requests
import schedule
import time

app = Flask(__name__)
sslify = SSLify(app)

def get_data():
    global corona_response, country_response
    country_response = requests.get("https://restcountries.eu/rest/v2/all?fields=name;population")
    corona_response = requests.get("https://lab.isaaclin.cn/nCoV/api/area?")

schedule.every(10).minutes.do(get_data)

country_response = requests.get("https://restcountries.eu/rest/v2/all")
corona_response = requests.get("https://lab.isaaclin.cn/nCoV/api/area?")

@app.route('/')
def index():
    return render_template("index.html", 
        title="Pivička", 
        corona_data=corona_response.text, 
        country_data=country_response.text)

if __name__ == '__main__':
    app.run()