from flask import Flask, jsonify, request
import mock_data

import datetime

app = Flask(__name__)

# Acesso aos dados mockados
contas = mock_data.contas
auth_server = mock_data.auth_server

# Comeca a contagem de operacoes quando o servidor inicia
numOperacao = 0

# Cria o arquivo de log quando o servidor inicia
log_file = open("log.txt", "w")
log_file.writelines('TIMESTAMP NumOperacao IdServidorNegocio TipoOperacao Conta Valor \n')
log_file.close()

#obter token a partir de id_negoc e a senha que foi passado
@app.route("/connect/<id_negoc>/<senha>", methods=["POST"])
def connect(id_negoc, senha):
    for server in auth_server:
        if (server['id'] == int(id_negoc)):
            if server['senha'] == senha:
                return jsonify({'token': server['token']})
    
    return '-1', 400

# retorna -1 se a conta estiver travada por outro servidor de negócio 
@app.route("/obter/saldo/<id_negoc>/<conta>")
def getSaldo (id_negoc, conta):
    # verificar se o servidor de negocio esta autenticado
    servidor_autenticado = authenticate(id_negoc, request.headers.get("Apikey"))
    if not servidor_autenticado:
        return '-1', 400

    for c in contas:
        if int(conta) == c['id']:
            # nao permite operacao se a conta esta sendo usada por outro servidor
            if c['isLocked'] == True:
                return '-1', 400

            c['isLocked'] = True
            log(id_negoc, 'getSaldo', conta, c['saldo'])
            return jsonify({'saldo': str(c['saldo'])})

    return '-1', 400

# retorna -1 se a conta estiver travada por outro servidor de negócio
@app.route("/definir/saldo/<id_negoc>/<conta>/<valor>", methods=["POST"])
def setSaldo (id_negoc, conta, valor):
    # verificar se o servidor de negocio esta autenticado
    servidor_autenticado = authenticate(id_negoc, request.headers.get("Apikey"))
    if not servidor_autenticado:
        return '-1', 400
    
    for i in contas:
        if int(conta) == i['id']:
            # nao permite operacao se a conta esta sendo usada por outro servidor
            if i['isLocked'] == True:
                return '-1', 400
            
            i['isLocked'] = True
            if float(valor) < 0:
                if i['saldo'] < abs(float(valor)):
                    return '-1', 400
            i['saldo'] += float(valor)
            log(id_negoc, 'setSaldo', conta, i['saldo'])
            resp = jsonify()
            return resp

    return '-1', 400

# retorna -1 se a conta estiver travada por outro servidor de negócio
@app.route("/obter/locked/<id_negoc>/<conta>")
def getLock (id_negoc, conta):
    # verificar se o servidor de negocio esta autenticado
    servidor_autenticado = authenticate(id_negoc, request.headers.get("Apikey"))
    if not servidor_autenticado:
        return jsonify({"message": "falha na autenticacao"}), 400

    for i in contas:
        if int(conta) == i['id']:
            log(id_negoc, 'getLock', conta, 0)
            return jsonify({'locked': i['isLocked']})

    return jsonify({'message': 'conta {} não existe'.format(conta)}), 400

# retorna -1 se a conta estiver travada por outro servidor de negócio
@app.route("/definir/unlocked/<id_negoc>/<conta>", methods=["POST"])
def unLock (id_negoc, conta):
    # verificar se o servidor de negocio esta autenticado
    servidor_autenticado = authenticate(id_negoc, request.headers.get("Apikey"))
    if not servidor_autenticado:
        return '-1', 400
    
    for i in contas:
        if int(conta) == i['id']:
            log(id_negoc, 'unLock', conta, 0)
            i['isLocked'] = False
            resp = jsonify()
            return resp

    return '-1', 400

# verificar se o servidor de negocio e o token esta autorizado para realizar operacao
def authenticate(id_negocio, token):
    for server in auth_server:
        if server['id'] == int(id_negocio):
            if server['token'] == token:
                return True
    return False

# funcao para registrar log
def log(id_negoc, tipoOperacao, conta, valor):
    timestamp = datetime.datetime.now()
    global numOperacao
    numOperacao += 1

    log_file = open("log.txt", mode = "a")
    log_message = '{} {} {} {} {} {} \n'.format(str(timestamp), 
        str(numOperacao), str(id_negoc), str(tipoOperacao), 
        str(conta), str(valor))

    log_file.writelines(log_message)
    log_file.close()


if __name__ == "__main__":
    app.run()