from api import send_message, send_photo
import datetime
import re
from selenium import webdriver
import requests
import bs4

# Este plugin acessa as informações de partida de linhas no site da SPTrans,
# ou, melhor dizendo, no Geologística deles, atualizado para caramba...
# Leia-se: http://itinerarios.sptrans.com.br/PlanOperWeb/

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

    # Primeiro eu preciso de um cookie que você consegue acessando o root do
    # PlanOperWeb. Esse cookie tem um nome bem bacana: "ASPSESSIONIDACBTSSDT"
    # e sem ele o resultado é um erro do MSSQL. Vá entender...
    session = requests.Session()
    session.get("http://itinerarios.sptrans.com.br/PlanOperWeb/")

    # Por algum motivo que me é desconhecido, as coisas não funcionam se eu não
    # fizer este request aqui, que, talvez deva "legitimar" o Cookie, não sei...
    session.get("http://itinerarios.sptrans.com.br/PlanOperWeb/ABInfGrConGWEB.asp?MODULO=WEB")

    # Nessa parte, eu só preciso obter o código da tabela de partidas...
    url = "http://itinerarios.sptrans.com.br/PlanOperWeb/ABInfSvLinG.asp?SvLinCodigo={}&TpLinCodigo={}".format(linha, variante)
    output = session.get(url)
    ensopado = bs4.BeautifulSoup(output.content, "html.parser")
    #print(str(ensopado))
    #print(output.request.headers)

    # Procura o parâmetro do qual precisamos
    expr = re.compile("CdPjOID=(\\d+)")
    match = expr.search(str(ensopado))

    #
    if not match:
        send_message(msg["chat"]["id"], str("Linha não encontrada! "))
        return None

    idTabela = match.group(1) # Não confundir com "matches"
                              # Recebe a id da qual precisamos

    # Caso não haja valor determinado para o dia, procura com
    # base no dia atual...
    diaDeHoje = datetime.datetime.today().weekday()
    if tipoDia == "None": # Eu não sei porque isso vem como "None" ao
                          # inves de uma string vazia... Mas funciona...
        if diaDeHoje == 6: # domingo
            tipoDia = "2"
        elif diaDeHoje == 5: # sábado
            tipoDia = "1"
        else: # úteis
            tipoDia = "0"

    # Informação interessante: a data vigente é requerida, porém não usada...
    # Ele retornará a mais recente de maneira qualquer
    #url = "http://itinerarios.sptrans.com.br/PlanOperWeb/ABInfSvHorD.asp?CdPjOID={}&CdPjODataVig=01/01/1970&MODULO=&TpDiaID={}" \
    #.format(idTabela, tipoDia)
    # Encontrei um outro endpoint cuja formatação estava mais correta...
    # Este endpoint ainda é usado pelo site principal
    # E ele ignora o parâmetro TpDiaID, usando TpDiaIDpar no lugar...
    url = "http://itinerarios.extapps.sptrans.com.br/PlanOperWeb/detalheLinha.asp?" + \
        "CdPjOID={}&TpDiaIDpar={}".format(idTabela, tipoDia)
    print(url)
    output = session.get(url)
    ensopado = bs4.BeautifulSoup(output.content, "html.parser")

    saida = "W.I.P."

    horarios = ensopado.find("table", class_="tabelaHorarios") # Localiza a tabela
    if horarios:

        letreiroIda = ensopado.find("span", id="lblLetreiroTP").getText()
        letreiroVolta = ensopado.find("span", id="lblLetreiroTS").getText()

        dia = "Dias úteis"
        if diaDeHoje == 5:
            dia = "Sábados"
        elif diaDeHoje == 6:
            dia = "Domingos e feriados"
        saida = "*{}-{}* - *{}* ({}) \nHorários para a viagem de ida, a partir de _{}_\n\n" \
            .format(linha, variante, letreiroIda, dia, letreiroVolta)

        for tr in horarios.findAll("tr"):
            tds = tr.findAll("td")
            if tds:
                saida += tds[2].getText() + "\n"


    else: # Se a tabela não foi encontrada, deve ter rolado algum erro
        erro = ""

        # TODO: Implementar um tratamento decente de erros
        errlines = ensopado.findAll("font")
        if errlines is not None:
            erro = str(ensopado.getText())
            print(erro)
        else:
            erro = "Uma resposta inesperada fora recebida: \n"
            erro += str(ensopado.getText())

        send_message(msg["chat"]["id"], erro)

    print(output.request.headers)

    print(saida)
    send_message(msg["chat"]["id"], saida)
