# TODO: Async, !wunder add e talvez descobrir um jeito de não cortar a imagem

import datetime
import json
import requests
import api
import urllib.parse

gUrlConditions  = "http://api.wunderground.com/api/dbcee4e7c140bb2d/lang:BR/conditions/forecast/q/"
gUrlSatellite   = "http://api.wunderground.com/api/dbcee4e7c140bb2d/animatedsatellite/q/"


def load_locations():
    locations = None

    with open("data/wunder.json") as fp:
        locations = json.load(fp)

    return locations


def add_entry(user_id, location):
    user_id     = str(user_id)
    locations   = load_locations()

    locations[user_id] = location

    with open("data/wunder.json", "w") as fp:
        json.dump(locations, fp)


def resolve_location(user_id):
    user_id     = str(user_id)
    locations   = load_locations()

    if user_id in locations:
        return locations[user_id]
    else:
        return None


def get_conditions_and_forecast(place):
    url = gUrlConditions
    url += urllib.parse.quote(place) + ".json"

    response = requests.get(url)
    response = json.loads(response.content)
    print(url)
    print(str(response))

    return response


def get_satellite_url(place):
    return gUrlSatellite + place + ".gif?basemap=1&timelabel=1&timelabel.y=10&num=5&delay=50&radius=500&radunits=km&borders=1&key=sat_ir4"


def process_conditions(conditions):
    '''conditions_dict = {
        "": "pora n sei n da pra ve",
        "Bruma": "VEI TA TD BRAMCO",
        "Céu Limpo": "LINPIN LINPJIN",
        "Céu Encoberto": "ceu coberto con 1 endredonm",
        "Chuva": "i vai chove em",
        "Chuva Fraca": "una chuvinia lvevina",
        "Chuviscos Fracos": "una chuvinia fraquinia hummmmmmmmm",
        "Muito Nublado": "muitas nuve",
        "Neblina": "presemsa d esnop dog",
        "Nuvens Dispersas": "umas nove espalhada",
        "Parcialmente Nublado": "1as nuve por ai",
        "Possibilidade de Chuva": "vix tauves vai cai umas agua",
        "Possibilidade de Trovoada": "i tauves vai da us trovao em",
        "Trovoada": "vei vai da ums trovao mASA",
        "Trovoadas com Chuva": "1s trovao c chuv",
        "Trovoadas Fracas e Chuva": "troamvãoiizn i xhuvaaaaa"
    }

    if conditions in conditions_dict:
        return conditions_dict[conditions]
    else:'''
    return conditions

def check_data(data):
    '''
    Às vezes a saída é um erro ou uma lista de resultados
    :param data:
    :return:
    '''
    if "current_observation" in data:
        return generate_string(data)
    elif "results" in data["response"]:
        return "Múltiplos resultados"
    elif "error" in data["response"]:
        return "Deu merda" #~~provisório~~
    return "Deu algum outro B.O. qualquer aqui"

def generate_string(data):
    if "current_observation" not in data:
        print("talbot")
    conditions  = data["current_observation"]
    forecast    = data["forecast"]["simpleforecast"]["forecastday"]

    cityname    = conditions["display_location"]["full"]
    temp_c      = conditions["temp_c"]
    feels_c     = conditions["feelslike_c"]
    weather     = conditions["weather"]
    station     = conditions["observation_location"]["city"]
    obs_time    = conditions["observation_time_rfc822"]
    humidity    = conditions["relative_humidity"]
    wind_vel    = conditions["wind_kph"]
    wind_from   = conditions["wind_dir"]
    dewpoint    = conditions["dewpoint_c"]

    header  = ""
    footer  = ""
    now     = datetime.datetime.now()

    header = "Situação metereológica em *{}*\r\n".format(cityname)
    header += "A temperatura é de {}ºC, com uma sensação térmica de {}ºC\n".format(temp_c, feels_c)
    header += "com dados da estação meterológica de {}, em {}.\n".format(station, obs_time[5:])
    header += "Humidade em {}\n".format(humidity)
    header += "Ventos de {} narizes do retcha/h, de {}\n".format(wind_vel, wind_from)
    header += "Aspecto: {}".format(process_conditions(weather))

    # Se já é noite, pegue a previsão do dia seguinte. (index 0 é hoje, 1 é amanhã)
    if now.hour >= 18:
        forecast_max    = forecast[1]["high"]["celsius"]
        forecast_min    = forecast[1]["low"]["celsius"]
        precipitation   = forecast[1]["pop"]
        conditions      = process_conditions(forecast[1]["conditions"])

        footer = "\n\nTempo amanhã: \n"
        footer += "{} com una probabilidade de precipitação de {} (unid. desconhecida)\n".format(conditions, precipitation)
        footer += "Máxima: {}ºC Mínima: {}ºC Ponto do Orvalho: {}ºC".format(forecast_max , forecast_min, dewpoint)
    else:
        forecast_max    = forecast[0]["high"]["celsius"]
        forecast_min    = forecast[0]["low"]["celsius"]
        precipitation   = forecast[0]["pop"]
        conditions      = process_conditions(forecast[0]["conditions"])

        footer = "\n\nTempo hoje: \n"
        footer += "{} com una probabilidade de precipitação de {} (unid. desconhecida)\n".format(conditions, precipitation)
        footer += "Máxima: {}ºC Mínima: {}ºC Ponto do Orvalho: {}ºC".format(forecast_max, forecast_min, dewpoint)

    return header + footer


def on_msg_received(msg, matches):
    chat        = msg["chat"]["id"]
    user        = msg["from"]["id"]
    if str(matches.group(1)) == "":
        location = resolve_location(user)
    else:
        location = matches.group(1)

    if location is None:
        api.send_message(chat, "Use */wunder add [estação]* para especificar seu local")
        return

    data            = get_conditions_and_forecast(location)
    satellite_img   = get_satellite_url(location)
    message         = check_data(data)

    api.send_document(chat, satellite_img)
    api.send_message(chat, message)
