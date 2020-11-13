from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
from pprint import pprint
import requests, json
from ItemsList import ItemsList
from BotConfiguration import BotConfiguration
from MongoDbConfiguration import MongoDbConfiguration
from DictToObject import DictToObject
import logging

log = logging.getLogger(__name__)
configuration = BotConfiguration()
mongo = MongoDbConfiguration()

def save(update, context):
    logMethod("/save", context)
    if(len(context.args) < 3): 
        invalidCommandMessage(update)
    else:
        totalArgs = len(context.args)
        itemList = ItemsList(context.args[0], context.args[1:totalArgs-1], context.args[totalArgs - 1])
        document = mongo.db.itemsList.find({"_id": update.message.chat.id})
        try:
            if len(list(document)) == 0:
                document.rewind()  
                mongo.db.itemsList.insert_one({"_id": update.message.chat.id, "lists": [itemList.__dict__]})
            else:  
                mongo.db.itemsList.update_one({"_id": update.message.chat.id}, {"$push": {"lists": itemList.__dict__ }})
            message = "Saved list!\n\n" + itemList.showList()
            update.message.reply_text(message)
        except StopIteration as err:
            print("StopIteration error:", err, "-- rewinding Cursor object.")
            document.rewind()

def echo(update, context):
    logMethod("/echo", context)
    update.message.reply_text("Welcome to WriteItDown Bot! 😈")
    help(update, context)

def repeat(update, context):
    logMethod("/repeat", context)
    if not (context.args == None or len(context.args) == 0): 
        update.message.reply_text(" ".join(update.message.text.split("/repeat")))
    else: 
        update.message.reply_text("Don't be shy, send anything! 😛")

def help(update, context):
    logMethod("/help", context)
    allCommands = f"List of commands: 😎\n\n"
    allCommands += "1. /repeat text: Returns the sent message.\n"
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
    logMethod("/add", context)
    if not len(context.args) == 2: invalidCommandMessage(update)
    else:
        document = mongo.db.itemsList.find({"_id": update.message.chat.id, "lists.name": context.args[0]})
        if len(list(document)) > 0:
            document.rewind()
            mongo.db.itemsList.update_one({"_id": update.message.chat.id, "lists.name": context.args[0]}, {"$set": {"lists.items": f"{document.next().get('lists.items')} {context.args[1]}"}})
            update.message.reply_text("Added items to the list!")
        else:  update.message.reply_text("You don't have any list with this name! 😔")

def remove(update, context):
    logMethod("/remove", context)
    if not len(context.args) == 1: invalidCommandMessage(update)
    else:
        mongo.db.itemsList.update_one({"_id": update.message.chat.id},  { "$pull" : {"lists": { "name" : context.args[0]}}})
        update.message.reply_text("Done!")

def show(update, context):
    logMethod("/show", context)
    if not len(context.args) == 1: invalidCommandMessage(update)
    else:
        try:
            #document = mongo.db.itemsList.find({"_id": update.message.chat.id, "lists": [{"name": context.args[0]}]})
            document = mongo.db.itemsList.find({"_id": update.message.chat.id})
            message = ""
            if len(list(document)) > 0:
                document.rewind()
                for value in document.next().get("lists"):
                    if value["name"] == context.args[0]:
                        message = ItemsList(value["name"], [value["items"]], value["hour"]).showList()
                        break
                update.message.reply_text(message)
            else: update.message.reply_text("Does not exist a list with this name!")
        except StopIteration as err:
            print("StopIteration error:", err, "-- rewinding Cursor object.")
            document.rewind()

def showAll(update, context):
    logMethod("/showAll", context)
    if not len(context.args) == 0: invalidCommandMessage(update)
    try:
        document = mongo.db.itemsList.find({"_id": update.message.chat.id})
        message = ""
        if len(list(document)) > 0:
            document.rewind()
            for value in document.next().get("lists"):
                    message += ItemsList(value["name"], [value["items"]], value["hour"]).showList() + '\n'
            update.message.reply_text(message)
        else: update.message.reply_text("You don't have lists for now, create one!")
    except StopIteration as err:
        print("StopIteration error:", err, "-- rewinding Cursor object.")
        document.rewind()

def invalidCommandMessage(update):
    update.message.reply_text("Incorrect commands!")

def logMethod(method, context):
    log.info(f"Method {method} {context.args}")

def main():
    updater = Updater(configuration.token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("save", save))
    dp.add_handler(CommandHandler("repeat", repeat))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("remove", remove))
    dp.add_handler(CommandHandler("show", show))
    dp.add_handler(CommandHandler("showAll", showAll))
    dp.add_handler(MessageHandler(Filters.text, echo))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()