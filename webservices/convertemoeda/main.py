from flask import Flask, jsonify

import requests
from requests.structures import CaseInsensitiveDict

app = Flask(__name__)

@app.route("/convertemoeda/<valor>")
def convertemoeda(valor):
   url = "https://api.currencyapi.com/v3/latest?base_currency=BRL&currencies=EUR,USD"

   headers = CaseInsensitiveDict()
   headers["apikey"] = "API_KEY"

   resp = requests.get(url, headers=headers)

   euro = int(valor) * resp.json()['data']['EUR']['value']
   dolar = int(valor) * resp.json()['data']['USD']['value']

   conversao = {
      'conversao': {
         'real': float(valor),
         'dolar': round(dolar,2),
         'euro': round(euro,2),
      }
   }

   return jsonify(conversao)

if __name__ == "__main__":
    app.run()