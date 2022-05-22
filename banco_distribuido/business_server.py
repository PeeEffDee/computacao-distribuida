from flask import Flask, jsonify
import requests

from requests.structures import CaseInsensitiveDict

app = Flask(__name__)

dadosBaseUrl = "http://localhost:5000"
nomeServidor = 1
senhaServidor = 'pedro123'

token = None

@app.route("/deposito/<acnt>/<amt>", methods=["POST"])
def deposito (acnt, amt):
    global token
    if token is None:
        resp = requests.post("{}/connect/{}/{}".format(dadosBaseUrl, nomeServidor, senhaServidor))
        token = resp.json()['token']

    if verificarContaBloqueada(acnt):
        return jsonify({'message': 'conta está bloqueada por outro servidor'}), 400
        
    url = "{}/definir/saldo/{}/{}/{}".format(dadosBaseUrl, nomeServidor, acnt, amt)
    headers = CaseInsensitiveDict()
    headers["Apikey"] = token
    resp = requests.post(url, headers=headers)
    desbloquearConta(acnt)
    if resp.status_code != 200:
        return 'erro ao realizar deposito', 400

    response = jsonify({'message': 'Deposito de {} realizado com sucesso'.format(amt)}), 200
    return response

@app.route("/saque/<acnt>/<amt>", methods=["POST"])
def saque (acnt, amt):
    global token
    if token is None:
        resp = requests.post("{}/connect/{}/{}".format(dadosBaseUrl, nomeServidor, senhaServidor))
        token = resp.json()['token']

    if verificarContaBloqueada(acnt):
        return jsonify({'message': 'conta está bloqueada por outro servidor'}), 400

    url = "{}/definir/saldo/{}/{}/{}".format(dadosBaseUrl, nomeServidor, acnt, '-'+str(amt))
    headers = CaseInsensitiveDict()
    headers["Apikey"] = token
    resp = requests.post(url, headers=headers)
    desbloquearConta(acnt)
    if resp.status_code != 200:
        return 'erro ao realizar saque', 400

    response = jsonify({'message': 'saque de {} realizado com sucesso'.format(amt)}), 200
    return response

@app.route("/saldo/<acnt>/")
def saldo (acnt):
    global token
    if token is None:
        resp = requests.post("{}/connect/{}/{}".format(dadosBaseUrl, nomeServidor, senhaServidor))
        token = resp.json()['token']
    
    if verificarContaBloqueada(acnt):
        return jsonify({'message': 'conta está bloqueada por outro servidor'}), 400

    url = "{}/obter/saldo/{}/{}".format(dadosBaseUrl, nomeServidor, acnt)
    headers = CaseInsensitiveDict()
    headers["Apikey"] = token
    resp = requests.get(url, headers=headers)
    desbloquearConta(acnt)
    if resp.status_code != 200:
        return jsonify({'message': 'erro ao obter saldo'}), 400
    
    response = jsonify({'saldo': resp.json()['saldo']})
    return response

@app.route("/transferencia/<acnt_orig>/<acnt_dest>/<amt>", methods=["POST"])
def transferencia(acnt_orig, acnt_dest, amt):
    global token
    if token is None:
        resp = requests.post("{}/connect/{}/{}".format(dadosBaseUrl, nomeServidor, senhaServidor))
        token = resp.json()['token']
    
    if verificarContaBloqueada(acnt_orig):
        return jsonify({'message': 'conta origem está bloqueada por outro servidor'}), 400
    if verificarContaBloqueada(acnt_dest):
        return jsonify({'message': 'conta destino está bloqueada por outro servidor'}), 400

    status = saque(acnt_orig, amt)[1]
    if status != 200:
        return jsonify({"menssage": "Erro ao realizar saque na conta {}".format(acnt_orig)})
    
    status = deposito(acnt_dest, amt)[1]
    if status != 200:
        return jsonify({'message': 'Erro ao efetuar deposito na conta {}'.format(acnt_dest)})
    
    response = jsonify(
        {
            'mensagem': 'transferência de {} realizada da conta {} para conta {}'
                .format(amt, acnt_orig, acnt_dest)
        })

    return response


def obterToken():
    global token
    resp = requests.post("{}/connect/{}/{}".format(dadosBaseUrl, nomeServidor, senhaServidor))
    token = resp.json()['token']

def verificarContaBloqueada(acnt):
    if token is None:
        obterToken()

    url = "{}/obter/locked/{}/{}".format(dadosBaseUrl, nomeServidor, acnt)
    headers = CaseInsensitiveDict()
    headers["Apikey"] = token
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return False
    return bool(resp.json()['locked'])

def desbloquearConta(acnt):
    if token is None:
        obterToken()

    url = "{}/definir/unlocked/{}/{}".format(dadosBaseUrl, nomeServidor, acnt)
    headers = CaseInsensitiveDict()
    headers["Apikey"] = token
    requests.post(url, headers=headers)

if __name__ == "__main__":
    app.run(port=5001)