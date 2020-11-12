from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
import requests, json
from ItemsList import ItemsList
from BotConfiguration import BotConfiguration

items = []
configuration = BotConfiguration()

def getMessages():
    response = requests.get(configuration.url + configuration.token + "/getUpdates")
    messageJson = response.content.decode("utf8")
    messagesDict = json.loads(messageJson)
    return messagesDict

def sendMessage(idchat, text):
    requests.get(configuration.url + "sendMessage?text=" + text + "&chat_id=" + str(idchat))

def save(update, context):
    itemList = ItemsList(context.args[0], context.args[1], context.args[2])
    items.append(itemList)
    itemList.showList()
    message = "Saved list!\n\n" + itemList.showList()
    update.message.reply_text(message)

def echo(update, context):
    print(context.args)
    if not len(context.args) == 0 or context.args == None: update.message.reply_text(" ".join(update.message.text.split("/echo")))
    else: update.message.reply_text("Don't be shy, send anything! 😛")

def help(update, context):
    allCommands = f"List of commands: 😎\n\n"
    allCommands += "1. /echo text: Return the sent message.\n"
    allCommands += "2. /save name items hour : Save a list and set a remainder hour.\n"
    allCommands += "3. /add name items : Add items to an existing list.\n"
    allCommands += "4. /remove name : Delete an existing list.\n"
    allCommands += "5. /show name : Show a description's list.\n"
    allCommands += "6. /changeName oldName newtName : Change the name of a created list.\n"
    allCommands += "7. /changeHour name hour : Change the remainder hour of a created list. If the new hour is = 0, the remainder hour will be deleted.\n"
    allCommands += "8. /removeItems name items : Delete the items of a list.\n"
    allCommands += "9. /changeItems oldItems . newItems : Remove old items and add the new items.\n"
    update.message.reply_text(allCommands)

def add(update, context):
    pass

def remove(update, context):
    pass

def show(update, context):
    update.message.reply_text([item for item in items if item.name == context.args[0]][0].showList())

def main():
    updater = Updater(configuration.token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("save", save))
    dp.add_handler(CommandHandler("echo", echo))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("remove", remove))
    dp.add_handler(CommandHandler("show", show))
    dp.add_handler(MessageHandler(Filters.text, echo))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()