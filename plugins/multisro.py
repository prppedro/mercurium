import re
from api import send_message, send_photo
import requests
import bs4

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                             #
#           Plugin: MultiSRO        Autor: Pedro T. R. Pinheiro               #
#           Date: 16/10/2017        Version: 0.1b                             #
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
    url = "http://www2.correios.com.br/sistemas/rastreamento/newprint.cfm"
    headers = { 'User-Agent' : 'Mercurium/0.1 (+http://www.tadeu.org/)' }
    # Aparentemente, a ECT ainda não entendeu a existência do UTF-8
    data = { 'objetos' : obj.encode("iso-8859-1")}

    try:
        resposta = requests.post(url, data, headers = headers)
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
            return montaSaida(parseado)

        except Exception:
            return "Processamento: Erro aleatório"

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

def montaSaida(parseado):
    ''' Recebe o parseado do método query e monta a saída para a pesquisa'''
    # Este método, em potencial, recebe uma porrada de coisas praticamente co-
    # ladas da implementação original. Talvez fosse o caso de refatorá-las,
    # portando:
    # TODO: Refatorar isto

    # Este título h4 só aparece quando o pacote não existe
    if parseado.find("body").find("h4") is not None:
        return format("SRO: Este pacote ({}) não retornou resultados", obj)
    else:
        status = ""
        tabelita = parseado.find("table", class_="listEvent sro").findAll("tr")

        # Corre todas as linhas da tabela
        # Por sorte, ao contrário da implementação do Aulete, estas tabelas têm
        # hierarquia lógica, parece... Muito conveniente, I must say...
        for evento in tabelita:
            # retorna um array contendo várias strings da primeira coluna
            localhora = evento.findAll("td")[0].findAll(text=True)
            # retorna um array contendo várias strings da segunda coluna
            natureza = evento.findAll("td")[1].findAll(text=True)

            # O lascado, agora, é que a porcaria da interface dos correios usa <label>
            # em alguns nomes de cidade. O que significa que o índice dois em diante é,
            # geralmente, uma bagunça... O jeito é concatená-los e arrancar os espaços
            # em branco...
            status += "`" + localhora[1].strip() + " " + localhora[0].strip() + "`"
            status += "\n"

            if len(natureza) > 3:
                status += "*{} {}*".format(natureza[1].strip(), natureza[3].strip())
            else:
                status += "*{}*".format(natureza[1].strip())
            status += "\n"

            if len(localhora) > 4:
                status += "_" + localhora[3].strip() + "_"
            else:
                status += "_" + localhora[2].strip() + "_"

            status += "\n\n"

        return status