from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
from pprint import pprint
import requests, json
from ItemsList import ItemsList
from BotConfiguration import BotConfiguration
from MongoDbConfiguration import MongoDbConfiguration
from DictToObject import DictToObject

items = []
configuration = BotConfiguration()
mongo = MongoDbConfiguration()

def save(update, context):
    itemList = ItemsList(context.args[0], context.args[1], context.args[2])
    document = mongo.db.itemsList.find({"_id": update.message.chat.id})
    try:
        if len(list(document)) == 0:  
            mongo.db.itemsList.insert_one({"_id": update.message.chat.id, "lists": [itemList.__dict__]})
        else:  
            mongo.db.itemsList.update_one({"_id": update.message.chat.id}, {"$push": {"lists": itemList.__dict__ }})
        message = "Saved list!\n\n" + itemList.showList()
        update.message.reply_text(message)
    except StopIteration as err:
        print("StopIteration error:", err, "-- rewinding Cursor object.")
        document.rewind()

def echo(update, context):
    if not context.args == None or len(context.args) == 0: update.message.reply_text(" ".join(update.message.text.split("/echo")))
    else: update.message.reply_text("Don't be shy, send anything! 😛")

def help(update, context):
    allCommands = f"List of commands: 😎\n\n"
    allCommands += "1. /echo text: Returns the sent message.\n"
    allCommands += "2. /save name items hour : Saves a list and set a remainder hour.\n"
    allCommands += "3. /add name items : Adds items to an existing list.\n"
    allCommands += "4. /remove name : Deletes an existing list.\n"
    allCommands += "5. /show name : Shows a description of the list.\n"
    allCommands += "6. /showAll : Shows all list's names.\n"
    allCommands += "7. /changeName oldName newtName : Changes the name of a created list.\n"
    allCommands += "8. /changeHour name hour : Changes the remainder hour of a created list. If the new hour is = 0, the remainder hour will be deleted.\n"
    allCommands += "9. /removeItems name items : Deletes the items of a list.\n"
    allCommands += "10. /changeItems oldItems . newItems : Removes old items and add the new items.\n"
    update.message.reply_text(allCommands)

def add(update, context):
    pass

def remove(update, context):
    pass

def show(update, context):
    try:
        #document = mongo.db.itemsList.find({"_id": update.message.chat.id, "lists": [{"name": context.args[0]}]})
        document = mongo.db.itemsList.find({"_id": update.message.chat.id})
        message = "Does not exist a list with this name!"
        for value in document.next().get("lists"):
            if value["name"] == context.args[0]:
                message = ItemsList(value["name"], " ".join(value["items"]), value["hour"]).showList()
                break
        update.message.reply_text(message)
    except StopIteration as err:
        print("StopIteration error:", err, "-- rewinding Cursor object.")
        document.rewind()

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