from operator import itemgetter
from os import path
from os import environ
import requests
import json
import psycopg2 as psql
from api import send_message
import datetime as dt

# Isso deve ser suficiente para transplantar as estatísticas para
# um plugin independente
def on_msg_received(msg, matches):
    chat = msg["chat"]["id"]

    print("O que chegou para mim: " + matches[1])

    # Implementação crua
    if matches[1] == "stats":
        result = return_statistics(chat)
        send_message(chat, result)
    elif matches[1] == "fullstats":
        result = return_full_statistics(chat)
        send_message(chat, result)

# TODO: estatísticas por horário
def return_full_statistics(chat):
    chat = str(chat)
    stats = {}
    total = 0
    result = "*Mensagens* \n\n"

    # Abre e lê o arquivo JSON
    with open("data/stats.json") as fp:
        stats = json.load(fp)

    if chat in stats:
        stats = stats[chat]
    else:
        return "n ten isotirco nesste xet ;()"

    # Conecta-se à base SQL



    dictofdicts = {}

    # Passa cada usuário do chat pro dictofdicts, onde a chave é o nome e o valor é a qtde.
    for user in stats:
        dictofdicts[stats[user]["name"]] = stats[user]["msg_count"]

    # Não sei programar em Python, logo farei a seguinte gambiarra:
    firstpass = 1;
    maxalgarismos = 0;
    primeirovalor = ""
    # Ordena a partir dos valores, de forma decrescente.
    for k, v in sorted(dictofdicts.items(), key=itemgetter(1), reverse=True):
        # Toda esta gambiarra tem o objetivo de deixar o número bonitinho, por sugestão do @thexp
        if (firstpass == 1):
            maxalgarismos = len(str(v))
            primeirovalor = str(v)
            firstpass = 0

        padding = ""

        if len(str(v)) < maxalgarismos:
            diff = maxalgarismos - len(str(v))
            for i in range(0,diff):
                padding += "  "

        result += padding + str(v) + " - " + k + "\n"
        total += v

    result += "\nTotal: " + str(total)
    # result += "\n*Debug*"
    # result += "\nMaxAlg: " + str(maxalgarismos)
    # result += "\nPadding: " + str(len(padding))
    # result += "\nPrimeiro valor: " + primeirovalor

    return result



def return_statistics(chat):
    chat = str(chat)
    stats = {}
    total = 0
    result = "*Mensagens* \n"
    result += "Período: _" + str(dt.datetime.today().strftime("%m/%y")) + "_ \n\n"

    # Abre e lê o arquivo JSON
    with open("data/stats.json") as fp:
        stats = json.load(fp)

    if chat in stats:
        stats = stats[chat]
    else:
        return "Não há histórico para este chat"


    dictofdicts = {}

    # Passa cada usuário do chat pro dictofdicts, onde a chave é o nome e o valor é a qtde.
    for user in stats:
        vigencia = str(dt.datetime.today().strftime('%Y%m'))
        userdata = stats[user]

        if "statsbymonth" in userdata and vigencia in userdata["statsbymonth"]:
            dictofdicts[stats[user]["name"]] = stats[user]["statsbymonth"][vigencia]

    # Não sei programar em Python, logo farei a seguinte gambiarra:
    firstpass = 1;
    maxalgarismos = 0;
    primeirovalor = ""
    # Ordena a partir dos valores, de forma decrescente.
    for k, v in sorted(dictofdicts.items(), key=itemgetter(1), reverse=True):
        # Toda esta gambiarra tem o objetivo de deixar o número bonitinho, por sugestão do @thexp
        if (firstpass == 1):
            maxalgarismos = len(str(v))
            primeirovalor = str(v)
            firstpass = 0

        padding = ""

        if len(str(v)) < maxalgarismos:
            diff = maxalgarismos - len(str(v))
            for i in range(0,diff):
                padding += "  "

        result += padding + str(v) + " - " + k + "\n"
        total += v

    result += "\nTotal: " + str(total)
    # result += "\n*Debug*"
    # result += "\nMaxAlg: " + str(maxalgarismos)
    # result += "\nPadding: " + str(len(padding))
    # result += "\nPrimeiro valor: " + primeirovalor

    return result




# TODO: estatísticas por horário
def do_statistics(msg):
    chat_id = str(msg["chat"]["id"])
    from_id = str(msg["from"]["id"])
    name = msg["from"]["first_name"]
    stats = {}

    # Abre e lê o arquivo JSON
    if path.isfile("data/stats.json"):
        with open("data/stats.json") as fp:
            stats = json.load(fp)

        # Checa se há key do chat no objeto. Se não existir, cria.
    if not chat_id in stats:
        stats[chat_id] = {}

        # Se existir key do usuário no obj do chat, atualiza. Caso contrário, cria.
    if from_id in stats[chat_id]:
        stats[chat_id][from_id]["msg_count"] += 1
        # Aqui estou adicionando uma entrada mensal. Originalmente seria feito
        # pelo banco de dados, mas por ora implementarei no JSON

        vigencia = str(dt.datetime.today().strftime('%Y%m'))

        # Para lidar com o legado:
        if "statsbymonth" not in stats[chat_id][from_id]:
            stats[chat_id][from_id]["statsbymonth"] = {}
            stats[chat_id][from_id]["statsbymonth"][vigencia] = 1

        if vigencia in stats[chat_id][from_id]["statsbymonth"]:
            # Se o mês já começou e o usuário já foi inserido:
            stats[chat_id][from_id]["statsbymonth"][vigencia] += 1
        else:
            # Se não há registros para o mês:
            stats[chat_id][from_id]["statsbymonth"][vigencia] = 1
    else:
        vigencia = str(dt.datetime.today().strftime('%Y%m'))
        stats[chat_id][from_id] = {}
        stats[chat_id][from_id]["msg_count"] = 1
        stats[chat_id][from_id]["name"] = name
        stats[chat_id][from_id]["statsbymonth"] = {}
        stats[chat_id][from_id]["statsbymonth"][vigencia] = 1


        # Abre e salva o arquivo JSON
    with open("data/stats.json", "w") as fp:
        json.dump(stats, fp, indent=4, sort_keys=True)
