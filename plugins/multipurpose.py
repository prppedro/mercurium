# Plugin mais feio do mundo, mas é só pra um chat específico.
# Aqui temos comandos que são pequenos demais pra terem seu próprio módulo.

# O stats fora inicialmente implementado aqui, depois fora transferido [Tadeu, 23/Ago]

# A maioria é um port bem rápido de https://github.com/lucasberti/telegrao/blob/master/plugins/taup.lua

# Este plugin é, de certa maneira, uma aberração, porque precisa ser processado
# por último e geralmente dá problema quando alguém desativa/ativa comando pelo
# !plugin [cycrano]... Idealmente, eu me livraria deste plugin, mas ele tem lá
# seus usos, então talvez eu tenha de dar um jeito de o multipurpose ser invo-
# cado diretamente pelo reborn ao invés de ser listado no config... [Tadeu, 23/Ago]

from api import send_message, send_sticker
from random import randint
import requests
import re
import plugins.stats as stats
import plugins.ed as ed


def on_msg_received(msg, matches):
    chat = msg["chat"]["id"]
    text = msg["text"]

    stats.do_statistics(msg)
    ed.run_ed(msg)

    # Precisamos manter log de todas as mensagens pro /xet e /wordcloud
    with open("data/log.txt", "a", encoding='utf-8') as f:
        f.write(text + "\n")

    # /ip
    pattern = re.compile("^[!/]ip(?:@PintaoBot)?$")
    match = pattern.search(text)

    if match:
        # A versão original retornava um IP hardcodded
        # Esta se conecta a um serviço de checkagem de IP externo
        ipregex = re.compile("(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})")
        url = "http://checkip.dyndns.com/"
        saida = ""

        try:
            req = requests.get(url)
            body = str(req.content)
            ipmatch = ipregex.search(body)

            if ipmatch:
                saida = ipmatch[0]
            else:
                saida = "Sei lá, deu algum outro pau aqui... "

        except Exception as e:
            saida = str(e)

        send_message(chat, saida)

    # /mps
    pattern = re.compile("^[!/]mps(?:@PintaoBot)?$")
    match = pattern.search(text)

    if match:
        send_message(chat, "ok to calculando aki q esistem " + str(randint(500, 10000)) + "/s por segundo de SUPER MAEMES NESNTE CHAT1")

    # @todos
    pattern = re.compile("(?:@todos|@todomundo)")
    match = pattern.search(text)

    if match:
        send_message(chat, "@berti @beaea @getulhao @rauzao @xisteaga @axasdas @Garzarella")
    # TODO: fazer esta listagem de modo dinâmico e, talvez, por plugin

    # calma
    pattern = re.compile("^calma$")
    match = pattern.search(text)

    if match:
        send_message(chat, "ok esto mais calmo obrigada")


    # vc esta ai
    pattern = re.compile("^Ping$")
    match = pattern.search(text)

    if match:
        send_message(chat, "Pong")

    # rau
    pattern = re.compile("^rau$")
    match = pattern.search(text)

    if match:
        send_message(chat, "meu pau no seu cu")

