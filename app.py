from flask import Flask, request, Response
import requests
from simpleeval import simple_eval
import json
import os
import urllib3

# Suppress the SSL warning for airport-data.com
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

@app.route('/')
def main():
    airport = request.args.get('queryAirportTemp')
    stock = request.args.get('queryStockPrice')
    expression = request.args.get('queryEval')

    try:
        if airport:
            headers = {'User-Agent': 'MUNI-Student-Project-xsinko1'}
            lat, lon = None, None
            
            # Step 1: Try Primary API (Airport-Data)
            try:
                addr = f"https://www.airport-data.com/api/get_airport.json?iata={airport}"
                geo_res = requests.get(addr, headers=headers, verify=False, timeout=5)
                if geo_res.status_code == 200:
                    data = geo_res.json()
                    lat = data.get('latitude')
                    lon = data.get('longitude')
            except Exception:
                pass

            # Step 2: Try Fallback API (Nominatim) if Step 1 failed
            if lat is None or lon is None:
                fallback_url = f"https://nominatim.openstreetmap.org/search?q={airport}+airport&format=json&limit=1"
                fb_res = requests.get(fallback_url, headers=headers, timeout=5)
                if fb_res.status_code == 200:
                    fb_data = fb_res.json()
                    if fb_data:
                        lat = fb_data[0]['lat']
                        lon = fb_data[0]['lon']

            if lat and lon:
                w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
                w_res = requests.get(w_url, timeout=5).json()
                val = w_res['current_weather']['temperature']
                return Response(json.dumps(val), mimetype='application/json')
            
            return Response("undefined", status=400)

        elif stock:
            url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={stock}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            res = requests.get(url, headers=headers, timeout=5).json()
            val = res['quoteResponse']['result'][0]['regularMarketPrice']
            return Response(json.dumps(val), mimetype='application/json')

        elif expression:
            val = simple_eval(expression)
            return Response(json.dumps(val), mimetype='application/json')

    except Exception as e:
        return Response(f"undefined", status=400)

    return Response("undefined", status=400)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5555))
    app.run(host='0.0.0.0', port=port)