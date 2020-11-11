from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import requests, json
from ItemsList import ItemsList

TOKEN = "1413728744:AAFOqecadjAmJo0fUGRh37qCj9-KupcEfG0"
URL = "https://api.telegram.org/bot" + TOKEN + "/"

items= []

def getMessages():
    response = requests.get(URL + "getUpdates")
    messageJson = response.content.decode("utf8")
    messagesDict = json.loads(messageJson)
    return messagesDict

def iterMessages():
 
    messages = getMessages()
    indice = len(messages["result"])-1
    nameList = "aaaa"
    items = ["Item1", "Item2"]
    hour = "12-12-12 10:00:00"
    #nameList = messages["result"][indice]["message"]["nameList"]
    #items = messages["result"][indice]["message"]["items"]
    #hour = messages["result"][indice]["message"]["hour"]
    idchat = messages["result"][indice]["message"]["chat"]["id"]
    showedList = save(nameList, items, hour)
    print(showedList)
    return idchat, showedList

def save(nameList, items, hour):
    itemList = ItemsList(nameList, items, hour)
    items.append(itemList)
    return itemList.showList

def sendMessage(idchat, text):
    requests.get(URL + "sendMessage?text=" + text + "&chat_id=" + str(idchat))

def main():
    idchat, showedList = iterMessages()
    sendMessage(idchat, showedList)

if __name__ == '__main__':
    main()