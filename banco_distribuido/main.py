from flask import flask

app = Flask(_name__)

@app.route('/deposito/<acnt>/<amt>')
def deposito(acnt, amt):
   

if __name__ == "__main__":
    app.run()