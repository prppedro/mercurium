import re
from api import send_message, send_photo
import requests
import bs4

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                             #
#           Plugin: MultiSRO        Autor: Pedro T. R. Pinheiro               #
#           Date: 16/10/2017        Version: 0.1b                             #
#           Date: 01/12/2018        Version: 0.1c (Changed “API” source)      #
#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def on_msg_received(msg, matches):
    ''' Plugin MultiSRO: refatoração da implementação original (sro.py) com
        suporte a múltiplas tags.
    '''
    regraGeral = "([A-Z]{2}\d{9}[A-Z]{2})"
    pattern = re.compile(regraGeral)
    _matches = pattern.finditer(matches.group(1))

    matchcont = 0

    for match in _matches:
        if S10ok(match.group(1)):
            q = query(match.group(1))
            send_message(msg["chat"]["id"], q)
        else:
            send_message(msg["chat"]["id"], "Isto é um código S10 inválido. ")
        matchcont += 1

    if (matchcont < 1):
        send_message(msg["chat"]["id"], \
                     "Isto não parece ser formato S10 nem na aparência. ")


def query(obj):
    '''obj: String'''
    url = "http://www.mdlivre.com.br/tracking/view/" + obj;
    headers = \
        {
            'User-Agent' : 'Mozilla/5.0 (Mercurium/0.1; +http://www.aehoo.net)'
        }

    try:
        resposta = requests.post(url, headers = headers)
    except ConnectionResetError:
        return "HTTP: Estourado o tempo limite de resposta"
    except ConnectionAbortedError:
        return "HTTP: Conexão interrompida"
    except ConnectionError:
        return "HTTP: Erro genérico de conexão"
    except ConnectionRefusedError:
        return "HTTP: Conexão recusada"
    finally:
        try:
            parseado = bs4.BeautifulSoup(resposta.content, "html.parser")
            # Delega o trabalho “pesado” ao nosso método montaSaida()
            return montaSaida(parseado, obj)

        except Exception as erro:
            return "*Erro no Python:* " + str(erro)

def S10ok(codigo):
    '''
    Valida o código S10 usado pela ECT (e outras várias empresas):
    https://en.wikipedia.org/wiki/S10_(UPU_standard)
    :param codigo:
    :return:
    '''
    rule = "([A-Z]{2})(\d{8})(\d)([A-Z]{2})"
    pattern = re.compile(rule)
    match = pattern.search(codigo)

    if match:
        code = str(match.group(2))
        checkdigit = int(match.group(3))
        weights = [8, 6, 4, 2, 3, 5, 9, 7]
        S = None
        C = None

        i = 0
        for digi in code:
            if S is None: S = 0
            S += int(digi) * weights[i]
            i += 1

        C = 11 - (S % 11)

        if C == 10: C = 0
        if C == 11: C = 5

        if checkdigit == C:
            return True
        else:
            return False
    else:
        return False

def montaSaida(parseado, obj):
    ''' Recebe o parseado do método query e monta a saída para a pesquisa'''
    # Comecei a scrapar a página do MDLivre, porque a dos correios
    # estava sem condições de tanto cookie que tinha que forçar.

    # Isto só aparece quando as coisas não funcionam
    if parseado.find("body").find("div", class_="text-danger") is not None:
        return format("*SRO:* O pacote " + obj + " não retornou resultados. ")
    else:
        status = ""

        #print("\n\n\n")
        #print(parseado.contents)
        #print("\n\n\n")

        try:
            tabelita = parseado.find("table", class_="hover").findAll("tr")
        except Exception:
            return("*Erro no scraping:* A página não continha uma estrutura esperada pelo parser. ");

        # Corre todas as linhas da tabela
        # Por sorte, ao contrário da implementação do Aulete, estas tabelas têm
        # hierarquia lógica, parece... Muito conveniente, I must say...
        for evento in tabelita:
            # retorna um array contendo várias strings da primeira coluna
            localhora = evento.findAll("td")[0].findAll(text=True)
            # retorna um array contendo várias strings da segunda coluna
            natureza = evento.findAll("td")[1].findAll(text=True)

            status += "`" + localhora[1].strip() + " " + localhora[0].strip() + "`"
            status += "\n"

            if len(natureza) > 3:
                status += "*{} {}*".format(natureza[1].strip(), natureza[3].strip())
            else:
                status += "*{}: {}*".format(natureza[0].strip(), natureza[1].strip())
            status += "\n"

            # Fiz uma adaptação porca, com sono, e nem sei o quão longe vai,
            # mas funciona e é isso aí...
            if len(localhora) > 4:
                status += "_" + localhora[1].strip() + "_"
            else:
                status += "_" + localhora[3].strip() + "_"

            status += "\n\n"

        return status