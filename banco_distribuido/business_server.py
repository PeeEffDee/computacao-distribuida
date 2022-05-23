from flask import Flask, jsonify
import requests

from requests.structures import CaseInsensitiveDict

app = Flask(__name__)

dadosBaseUrl = "http://localhost:5000"
nomeServidor = 1
senhaServidor = 'pedro123'

token = None

# depositar para a conta existente
@app.route("/deposito/<acnt>/<amt>", methods=["POST"])
def deposito (acnt, amt):
    global token
    if token is None:
        token = obterToken()

    if not token:
        return jsonify({'message': 'Erro ao tentar obter o Token'}), 400
    if verificarContaBloqueada(acnt).status_code == 400:
        return jsonify(verificarContaBloqueada(acnt).json()), 400
    elif bool(verificarContaBloqueada(acnt).json()["locked"]):
        return jsonify({'message': 'conta {} está bloqueada por outro servidor'.format(acnt)}), 400
        
    url = "{}/definir/saldo/{}/{}/{}".format(dadosBaseUrl, nomeServidor, acnt, amt)
    headers = CaseInsensitiveDict()
    headers["Apikey"] = token
    resp = requests.post(url, headers=headers)
    desbloquearConta(acnt)
    if resp.status_code != 200:
        return jsonify({'message': 'Erro ao tentar realizar deposito na conta {}'.format(acnt)}), 400

    response = jsonify({'message': 'Deposito de {} na conta {} realizado com sucesso'.format(amt, acnt)}), 200
    return response

# realizar saque na conta com saldo disponivel
@app.route("/saque/<acnt>/<amt>", methods=["POST"])
def saque (acnt, amt):
    global token
    if token is None:
        token = obterToken()

    if not token:
        return jsonify({'message': 'Erro ao tentar obter o Token'}), 400
    if verificarContaBloqueada(acnt).status_code == 400:
        return jsonify(verificarContaBloqueada(acnt).json()), 400
    elif bool(verificarContaBloqueada(acnt).json()["locked"]):
        return jsonify({'message': 'conta {} está bloqueada por outro servidor'.format(acnt)}), 400

    url = "{}/definir/saldo/{}/{}/{}".format(dadosBaseUrl, nomeServidor, acnt, '-'+str(amt))
    headers = CaseInsensitiveDict()
    headers["Apikey"] = token
    resp = requests.post(url, headers=headers)
    desbloquearConta(acnt)
    if resp.status_code != 200:
        return jsonify({'message': 'Erro ao tentar realizar saque na conta {}'.format(acnt)}), 400

    response = jsonify({'message': 'saque de {} realizado com sucesso'.format(amt)}), 200
    return response

# obter situacao do saldo
@app.route("/saldo/<acnt>/")
def saldo (acnt):
    global token
    if token is None:
        token = obterToken()

    if not token:
        return jsonify({'message': 'Erro ao tentar obter o Token'}), 400
    if verificarContaBloqueada(acnt).status_code == 400:
        return jsonify(verificarContaBloqueada(acnt).json()), 400
    elif bool(verificarContaBloqueada(acnt).json()["locked"]):
        return jsonify({'message': 'conta {} está bloqueada por outro servidor'.format(acnt)}), 400

    url = "{}/obter/saldo/{}/{}".format(dadosBaseUrl, nomeServidor, acnt)
    headers = CaseInsensitiveDict()
    headers["Apikey"] = token
    resp = requests.get(url, headers=headers)
    desbloquearConta(acnt)
    if resp.status_code != 200:
        return jsonify({'message': 'Erro ao obter saldo na conta {}'.format(acnt)}), 400
    
    response = jsonify({'saldo': resp.json()['saldo']})
    return response

# fazer transacao entre as contas existentes e com saldo disponivel
@app.route("/transferencia/<acnt_orig>/<acnt_dest>/<amt>", methods=["POST"])
def transferencia(acnt_orig, acnt_dest, amt):
    global token
    if token is None:
        token = obterToken()

    if not token:
        return jsonify({'message': 'Erro ao tentar obter o Token'}), 400
    if verificarContaBloqueada(acnt_orig).status_code == 400:
        return jsonify(verificarContaBloqueada(acnt_orig).json()), 400
    elif bool(verificarContaBloqueada(acnt_orig).json()["locked"]):
        return jsonify({'message': 'conta origem({}) está bloqueada por outro servidor'.format(acnt_orig)}), 400

    if verificarContaBloqueada(acnt_dest).status_code == 400:
        return jsonify(verificarContaBloqueada(acnt_dest).json()), 400
    elif bool(verificarContaBloqueada(acnt_dest).json()["locked"]):
        return jsonify({'message': 'conta destino({}) está bloqueada por outro servidor'.format(acnt_dest)}), 400

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
    resp = requests.post("{}/connect/{}/{}".format(dadosBaseUrl, nomeServidor, senhaServidor))
    if resp.status_code != 200:
        return False
    return resp.json()['token']

# verificar se conta ta bloqueada
def verificarContaBloqueada(acnt):
    url = "{}/obter/locked/{}/{}".format(dadosBaseUrl, nomeServidor, acnt)
    headers = CaseInsensitiveDict()
    headers["Apikey"] = token
    resp = requests.get(url, headers=headers)
    return resp
# desbloquear a conta
def desbloquearConta(acnt):
    url = "{}/definir/unlocked/{}/{}".format(dadosBaseUrl, nomeServidor, acnt)
    headers = CaseInsensitiveDict()
    headers["Apikey"] = token
    requests.post(url, headers=headers)

if __name__ == "__main__":
    app.run(port=5001)