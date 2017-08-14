from api import send_message, send_photo
import datetime
import requests
import bs4

def on_msg_received(msg, matches):
    # Bem-vindo à bagunça
    # Este aqui é um exemplar piorado dos irmãos aulete e sro
    # Sem explicar os intrínsecos porquês de eu odiar o sistema da SPTrans,
    # limitar-me-ei a dizer que o GTFS deles é chato de acessar e impreciso,
    # e eles só têm um site nojento e antigo para fornecer as informações mais
    # atuais, por incrível que pareça...
    #
    # E agora vem a parte bizarra: eu tenho de submeter um request para obter
    # uma "CdPjOid", que é, de fato a informação mais importante. Combinada com
    # "TpDiaId" ela fornece a tabela da linha. Uma considerável parte dos res-
    # to dos parâmetros não serve para absolutamente nada.
    linha = str(matches.group(1))
    variante = str(matches.group(2))
    tipoDia = str(matches.group(3)) # se especificado, 0 = útil, 1 = sáb., 2 = dom.
    # Nessa parte, eu só preciso obter o código da tabela de partidas...
    url = "http://itinerarios.sptrans.com.br/PlanOperWeb/ABInfSvLinG.asp?SvLinCodigo={}&TpLinCodigo={}".format(linha, variante)
    output = requests.get(url)
    ensopado = bs4.BeautifulSoup(output.content, "html.parser")
    definicao_raw = ensopado.find_all("div", id="definicao")

    # TODO: implementar esta filtragem
    # Regex: CdPjOID=(\d+)
    idTabela = "" # Com alguma bruxaria vou ter de obter isso aqui do meio da resposta que vier aí acima

    # Caso não haja valor determinado para o dia, procura com
    # base no dia atual...
    diaDeHoje = datetime.datetime.today().weekday()
    if tipoDia == "":
        if diaDeHoje == 6: # domingo
            tipoDia = "2"
        elif diaDeHoje == 5: # sábado
            tipoDia = "1"
        else: # úteis
            tipoDia = "0"

    # Informação interessante: a data vigente é requerida, porém não usada...
    # Ele retornará a mais recente de maneira qualquer
    url2 = "http://itinerarios.sptrans.com.br/PlanOperWeb/ABInfSvHorD.asp?CdPjOID={}&CdPjODataVig=01/01/1970&MODULO=&TpDiaID={}" \
    .format(idTabela, tipoDia)

    # O PlanOperWeb parou de funcionar enquanto estava programando este
    # script... Está dropando instantaneamente, típico sintoma de "puxaram
    # o IIS da tomada"... Se o script ficar por aqui é porque o sistema
    # deles morreu de vez... 

    send_message(msg["chat"]["id"], str("W.I.P."))
