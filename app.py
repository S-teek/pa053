from flask import Flask, request, jsonify, Response
import requests
from simpleeval import simple_eval

app = Flask(__name__)

@app.route('/')
def main():
    airport = request.args.get('queryAirportTemp')
    stock = request.args.get('queryStockPrice')
    expression = request.args.get('queryEval')

    if airport:
        coords = {"BRQ": (49.15, 16.69), "PRG": (50.10, 14.26), "LHR": (51.47, -0.45)}
        lat, lon = coords.get(airport.upper(), (50.0, 14.0))
        res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()
        val = res['current_weather']['temperature']
        return Response(str(val), mimetype='application/json')

    elif stock:
        res = requests.get(f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={stock}", headers={'User-Agent': 'Mozilla/5.0'}).json()
        val = res['quoteResponse']['result'][0]['regularMarketPrice']
        return Response(str(val), mimetype='application/json')

    elif expression:
        try:
            val = simple_eval(expression)
            return Response(str(val), mimetype='application/json')
        except:
            return Response("Error", status=400)

    return Response("Undefined", status=400)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
