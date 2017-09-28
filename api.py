import json
import os
import requests

def get_updates(offset=0, timeout=60):
    """ Por default, faz longpoll. Retorna uma array de Update """
    url = "https://api.telegram.org/" + os.environ['REBORNKEY'] + "/getUpdates?"
    url += "offset=" + str(offset) + "&"
    url += "timeout=" + str(timeout) + "&"

    try:
        # Esta substituição deixa o código mais compacto e não dá confusão
        # na hora do retorno, quando trabalhando em versões com a 3.4 e 3.5
        # Enfim, não sei... Mas funciona.
        response = requests.get(url).json()
    except Exception as e:
        print(e)
        return None

    if response["ok"] is True:
        return response["result"]
    else:
        return None


def send_message(chat_id, text, parse_mode="Markdown", reply_to_message_id="", reply_markup=""):
    """ reply_markup não é apenas ID, é uma array com opções. """
    url = "https://api.telegram.org/" + os.environ['REBORNKEY'] + "/sendMessage?"
    url += "chat_id=" + str(chat_id) + "&"
    url += "text=" + text + "&"
    url += "parse_mode=" + parse_mode + "&"
    if reply_to_message_id:
        url += "reply_to_message_id=" + str(reply_to_message_id) + "&"
    if reply_markup:
        url += "reply_markup=" + str(reply_markup)

    response = requests.get(url).json()

    return response


def edit_message_text(chat_id, msg_id, text, parse_mode="Markdown", reply_to_message_id="", reply_markup=""):
    """ reply_markup não é apenas ID, é uma array com opções. """
    url = "https://api.telegram.org/" + os.environ['REBORNKEY'] + "/editMessageText?"
    url += "chat_id=" + str(chat_id) + "&"
    url += "message_id=" + str(msg_id) + "&"
    url += "text=" + text + "&"
    url += "parse_mode=" + parse_mode + "&"
    if reply_to_message_id:
        url += "reply_to_message_id=" + str(reply_to_message_id) + "&"
    if reply_markup:
        url += "reply_markup=" + str(reply_markup)

    response = requests.get(url).json()

    return response


def delete_message(chat_id, msg_id):
    url = "https://api.telegram.org/" + os.environ['REBORNKEY'] + "/deleteMessage?"
    url += "chat_id=" + str(chat_id) + "&"
    url += "message_id=" + str(msg_id)

    response = requests.get(url).json()

    return response


def send_photo(chat_id, photo_url, caption="", reply_to_message_id=0):
    """ reply_markup não é apenas ID, é uma array com opções. """
    url = "https://api.telegram.org/" + os.environ['REBORNKEY'] + "/sendPhoto?"
    url += "chat_id=" + str(chat_id) + "&"
    url += "photo=" + photo_url + "&"

    if caption:
        url += "caption=" + caption + "&"
    if reply_to_message_id:
        url += "reply_to_message_id=" + str(reply_to_message_id) + "&"

    response = requests.get(url).json()

    return response

def send_audio_id(chat_id, file_id, caption="", reply_to_message_id=0):
    """ reply_markup não é apenas ID, é uma array com opções. """
    url = "https://api.telegram.org/" + os.environ['REBORNKEY'] + "/sendAudio?"
    url += "chat_id=" + str(chat_id) + "&"
    url += "audio=" + file_id + "&"

    if caption:
        url += "caption=" + caption + "&"
    if reply_to_message_id:
        url += "reply_to_message_id=" + str(reply_to_message_id) + "&"

    response = requests.get(url).json()

    return response


def send_document(chat_id, document_url, caption="", reply_to_message_id=0):
    """ reply_markup não é apenas ID, é uma array com opções. """
    url = "https://api.telegram.org/" + os.environ['REBORNKEY'] + "/sendDocument?"
    url += "chat_id=" + str(chat_id) + "&"
    url += "document=" + document_url + "&"

    if caption:
        url += "caption=" + caption + "&"
    if reply_to_message_id:
        url += "reply_to_message_id=" + str(reply_to_message_id) + "&"

    response = requests.get(url).json()

    return response

def send_sticker(chat_id, sticker_id): 
    url = "https://api.telegram.org/" + os.environ['REBORNKEY'] + "/sendSticker?"
    url += "chat_id=" + str(chat_id) + "&"
    url += "sticker=" + sticker_id + "&"

    response = requests.get(url).json()

    return response

# Vê se o caboclo pertence a tal grupo
def isGroupMember(chat_id, user_id):
    url = "https://api.telegram.org/" + os.environ['REBORNKEY'] + "/getChatMember?"
    url += "chat_id=" + str(chat_id) + "&"
    url += "user_id=" + str(user_id)

    response = requests.get(url).json()

    #return response
    if (response['ok'] == True):
        return True
    else:
        return False

