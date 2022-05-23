import requests

businessBaseUrl = "http://localhost:5001"

def imprimir(resp):
    if resp.status_code == 200:
        print(resp.json())
    else:
        print(resp.json()['message'])

#obter saldo
def saldo(conta):
    url = businessBaseUrl+'/saldo/{}'.format(conta)
    resp = requests.get(url)
    return resp

#fazer deposito
def deposito(conta, valor):
    url = businessBaseUrl+'/deposito/{}/{}'.format(conta, valor)
    resp = requests.post(url)
    return resp

#fazer saque
def saque(conta, valor):
    url = businessBaseUrl+'/saque/{}/{}'.format(conta, valor)
    resp = requests.post(url)
    return resp

#fazer transferencia
def transferencia(conta_orig, conta_dest, valor):
    url = businessBaseUrl+'/transferencia/{}/{}/{}'.format(conta_orig, conta_dest, valor)
    resp = requests.post(url)
    return resp

imprimir(deposito(1, 100))
imprimir(saldo(1))
imprimir(deposito(11, 100))
imprimir(saque(11, 1000))
imprimir(saque(1, 1000))
imprimir(saldo(1))
imprimir(transferencia(1, 2, 500))
imprimir(transferencia(1, 12, 10))
imprimir(transferencia(1, 2, 10))
imprimir(saldo(1))
imprimir(saldo(2))

