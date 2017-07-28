from api import send_message, send_photo
import requests
import bs4

def on_msg_received(msg, matches):
    url = "http://aulete.com.br/wap/resultado.php"
    headers = {'User-Agent': 'Nokia6630/1.0 (2.3.129) SymbianOS/8.0 Series60/2.6 Profile/MIDP-2.0 Configuration/CLDC-1.1'}
    data = { 'busca' : str(matches.group(1)).encode("iso-8859-1") }
    output = requests.post(url, data, headers=headers)
    ensopado = bs4.BeautifulSoup(output.content, "html.parser")
    definicao_raw = ensopado.find_all("div", id="definicao")

    spans = definicao_raw[0].find_all("span")
    definicao = ""

    if not spans:
        definicao = definicao_raw[0].find(text = True)

        #resultado = definicao_raw[0].findAll(text = True)
        #for frase in resultado:
        #    definicao += frase
    else:
        # Usado para comparar em caso de duas acepções
        cabecoAnterior = False
        cabecoCounter = 0
        for span in spans:
            texto = span.findAll(text = True)
            classe = span["class"][0]

            # definicao += "```" + str(span['class']) + " = " + str(span.findAll(text = True)) + "```"
            # Alta preguiça de definir o que acontece aqui...
            if classe == "cabeco":
                if cabecoAnterior is False:
                    if cabecoCounter > 0:
                        definicao += "\r\n"
                    definicao += "*{}*".format(texto[0])
                    cabecoAnterior = True
                    cabecoCounter = cabecoCounter + 1
                else:
                    definicao += ":_" + texto[0] + "_ "
                    cabecoAnterior = False
            else:
                cabecoAnterior = False

            if classe == "sepsil":
                # Gambiarrinha para conseguir pegar a sílaba tônica
                tonica = span.find("em", text = True)

                for sil in texto:
                    if sil == tonica:
                        definicao += "_{}_".format(sil)
                    else:
                        definicao += "{}".format(sil)

            # Não sei o que isso faz, mas vou colocar aqui, anyway
            #if classe == "ort":
                # Acho que não retorna nada, vou converter por segurança
                # Do contrário, ele pode estourar a pilha de dar erro
                # Adicionei também um pulo de linha para a próx. seção
                #definicao += "[{}]\r\n".format(str(texto))
                # Acabei desativando porque realmente não servia para muita coisa

            if classe == "catgram":
                definicao += "```{}```\r\n".format(texto[0])

            if classe == "numdef":
                definicao += "*{}* ".format(texto[0])

            if classe == "rubrica" or classe == "regio" or classe == "uso":
                definicao += "_{}_ ".format(texto[0])

            if classe == "def":
                definicao += "{}\r\n".format("".join(texto))

            if classe == "achverb":
                definicao += "\n_{}_\n".format("".join(texto))
    print(definicao)

    #parole = definicao_raw[0].find("span", class_="cabeco", text = True)
    #parole = parole.find(text = True)

    #definicao = "*{}*\nDebug: {}".format(parole, type(parole))

    send_message(msg["chat"]["id"], str(definicao))
