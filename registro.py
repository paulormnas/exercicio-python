import time
import json
import random
from leitura import DHT22

dht = DHT22(pino=4)

def registrar_dados(dados):
    dados_json = json.dumps(dados)
    caminho_do_arquivo = "registro/" + dados["property"] + "/" + str(dados["date"]) + ".json"

    with open(caminho_do_arquivo, "a+") as f:
        f.write(dados_json)

def gerar_dados(propriedade, valor):
    id = "dispositivo_001"
    localizacao = ["-22.597412, -43.289396"]
    data = time.time()

    dados = {'id': id,
             'location': localizacao,
             'property': propriedade,
             'date': data,
             'value': valor
             # 'signature': assinatura
             }

    #	hash = Hash.sha256(dados)
    #	assinatura = Crypto.RSA(hash)  # Crypto.Sign()
    #	dados['signature'] = assinatura

    registrar_dados(dados)


contador = 0
while (contador < 10):
    umidade, temperatura = dht.ler_dados()
    if umidade is not None and temperatura is not None:
        gerar_dados("UMIDADE", umidade)
        gerar_dados("TEMPERATURA", temperatura)
        print('{0},{1},{2:0.1f}*C,{3:0.1f}%rn'.format(time.strftime('%m/%d/%y'), time.strftime('%H:%M'), temperatura, umidade))
        contador += 1
    else:
        print("Falha ao receber os dados do sensor.")


    # gerar_dados("UMIDADE", random.randint(30, 80))
    # gerar_dados("TEMPERATURA", random.randint(15, 40))