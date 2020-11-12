from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
import requests, json
from ItemsList import ItemsList
from BotConfiguration import BotConfiguration

items= []
configuration = BotConfiguration()

def getMessages():
    response = requests.get(configuration.url + configuration.token + "/getUpdates")
    messageJson = response.content.decode("utf8")
    messagesDict = json.loads(messageJson)
    return messagesDict

def save(update, context):
    itemList = ItemsList(context.args[0], context.args[1], context.args[2])
    items.append(itemList)
    itemList.showList()
    update.message.reply_text(itemList.showList())

def echo(update, context):
    update.message.reply_text(update.message.text)

def sendMessage(idchat, text):
    requests.get(configuration.url + "sendMessage?text=" + text + "&chat_id=" + str(idchat))

def main():
    updater = Updater(configuration.token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("save", save))
    dp.add_handler(MessageHandler(Filters.text, echo))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()