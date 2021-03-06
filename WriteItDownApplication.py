from telegram.ext import Updater, InlineQueryHandler, CommandHandler, MessageHandler, Filters
from pprint import pprint
import requests, json, logging, datetime, pytz, sys
from model import ItemsList
from configuration import BotConfiguration, MongoDbConfiguration
from utils import JobUtils, RegexChecker, DatetimeParser
from timezonefinder import TimezoneFinder

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
log = logging
configuration = BotConfiguration()
mongo = MongoDbConfiguration()
calledTimezone = dict()
formatDate = "%Y-%m-%d"
formatHour = "%H:%M:%S"
formatDateAndHour = "%Y-%m-%d %H:%M:%S"
bot = None

def save(update, context):
    logMethod("/save", update.message.chat.id, context)
    if(len(context.args) < 3): 
        invalidCommandMessage(update)
    else: 
        if not RegexChecker.checkListName(context.args[0]):
            if RegexChecker.checkCorrectDatetime(" ".join(context.args[len(context.args)-2:])):
                try:                   
                    totalArgs = len(context.args)
                    datetime.datetime.strptime(context.args[totalArgs-2], formatDate)
                    datetime.datetime.strptime(context.args[totalArgs-1], formatHour)
                    formatedDate = datetime.datetime.strptime(" ".join(context.args[totalArgs-2:]), formatDateAndHour)
                    document = mongo.db.itemsList.find({"_id": update.message.chat.id})
                    timezone = document.next().get("timezone")
                    time = DatetimeParser.calculateSettedHour(formatedDate, timezone)
                    timeWithoutOffset = time.replace(tzinfo=None)
                    if timeWithoutOffset > datetime.datetime.today():
                        itemToSave = ItemsList(context.args[0], context.args[1:totalArgs-2], str(timeWithoutOffset))
                        itemListToShow = ItemsList(context.args[0], context.args[1:totalArgs-2], " ".join(context.args[totalArgs-2:]))
                        message = "Saved list!\n\n" + itemListToShow.showList()
                        document = mongo.db.itemsList.find({"_id": update.message.chat.id})
                        if len(list(document)) == 0:
                            message = "First of all set your timezone please!"
                        else:  
                            document = mongo.db.itemsList.find({"_id": update.message.chat.id},{"lists": {"$elemMatch" : { "name": context.args[0]} }})
                            if document.next().get("lists") == None:
                                mongo.db.itemsList.update_one({"_id": update.message.chat.id}, {"$push": {"lists": itemToSave.__dict__ }})
                                JobUtils.createJob(itemToSave, update.message.chat.id)
                            else: message = "You already have a list with this name!"
                        update.message.reply_text(message)
                    else: update.message.reply_text("Incorrect datetime. This datetime is before this moment!")
                except StopIteration:
                    print("StopIteration error: Rewinding Cursor object.")
                    update.message.reply_text("Internal server error, sorry for the incoveniences")
                except ValueError:
                    print("Incorrect format datetime")
                    update.message.reply_text("The datetime is not correct. Please insert a correct datetime with format YYYY-mm-dd HH:MM:SS.")
            else: update.message.reply_text("The datetime is not correct. Please insert a correct datetime YYYY-mm-dd HH:MM:SS.")
        else:
            update.message.reply_text("Invalid list name, the name only can have letters, numbers and '_'")
    
def add(update, context):
    logMethod("/add", update.message.chat.id, context)
    if len(context.args) < 2: invalidCommandMessage(update)
    else:
        try:
            document = mongo.db.itemsList.find({"_id": update.message.chat.id}, {"lists": {"$elemMatch": {"name": context.args[0]} }})
            if document.next().get("lists") != None:
                document.rewind()
                mongo.db.itemsList.update_one({"_id": update.message.chat.id}, {"$set": {"lists.$[elem].items": f"{document.next()['lists'][0].get('items')} {' '.join(context.args[1:])}"}}, array_filters=[{"elem.name": context.args[0]}])
                update.message.reply_text("Added items to the list!")
            else:  update.message.reply_text("You don't have any list with this name! 😔")
        except StopIteration:
            print("StopIteration error: Rewinding Cursor object.")
            update.message.reply_text("Internal server error, sorry for the incoveniences")

def remove(update, context):
    logMethod("/remove", update.message.chat.id, context)
    if not len(context.args) == 1: invalidCommandMessage(update)
    else:
        document = mongo.db.itemsList.update_one({"_id": update.message.chat.id},  { "$pull" : {"lists": { "name" : context.args[0]}}})
        if document.modified_count == 1:
            JobUtils.removeJob(update.message.chat.id, context.args[0])
            update.message.reply_text("Done!")
        else: update.message.reply_text(f"You don't have any list with name '{context.args[0]}'")

def show(update, context):
    logMethod("/show", update.message.chat.id, context)
    if not len(context.args) == 1: invalidCommandMessage(update)
    else:
        try:
            document = mongo.db.itemsList.find({"_id": update.message.chat.id}, {"lists": {"$elemMatch" : { "name": context.args[0]} }})
            message = ""
            if document.next().get("lists") != None:
                document.rewind()
                itemList = document.next()
                itemList = itemList["lists"][0]
                document = mongo.db.itemsList.find({"_id": update.message.chat.id})
                timezone = document.next().get("timezone")
                gettedHour = DatetimeParser.calculateGettedHour(itemList.get("hour"), timezone).replace(tzinfo=None)
                message = ItemsList(itemList.get("name"), [itemList.get("items")], gettedHour).showList()
                update.message.reply_text(message)
            else: update.message.reply_text("A list with this name does not exist!")
        except StopIteration:
            print("StopIteration error: Rewinding Cursor object.")
            update.message.reply_text("Internal server error, sorry for the incoveniences")

def showAll(update, context):
    logMethod("/showAll", update.message.chat.id, context)
    if len(context.args) != 0: invalidCommandMessage(update)
    try:
        document = mongo.db.itemsList.find({"_id": update.message.chat.id})
        message = ""
        document.rewind()
        if len(document.next().get("lists")) != 0:
            document.rewind()
            for value in document.next().get("lists"):
                document = mongo.db.itemsList.find({"_id": update.message.chat.id})
                timezone = document.next().get("timezone")
                gettedHour = DatetimeParser.calculateGettedHour(value["hour"], timezone).replace(tzinfo=None)
                message += ItemsList.ItemsList(value["name"], [value["items"]], gettedHour).showList() + '\n\n'
            update.message.reply_text(message)
        else: update.message.reply_text("You don't have lists for now, create one!")
    except StopIteration:
        print("StopIteration error: Rewinding Cursor object.")
        update.message.reply_text("Internal server error, sorry for the incoveniences")

def timezoneMessage(update, context):
    logMethod("/setTimezone", update.message.chat.id, context)
    if len(context.args) != 0:
        invalidCommandMessage(update)
    else:
        update.message.reply_text("Send me your location! Here is an example about how to share it")
        update.message.reply_animation("BQACAgQAAxkDAAIEP1-3vPkWhmlD19MAASJRK3KzhBKAZgAC8AkAAoOFwFHr1Vax3v-7XR4E")
        calledTimezone[update.message.chat.id] = True

def setTimezone(update, context):
    message = ""
    if calledTimezone.get(update.message.chat.id, False):
        try:
            tf = TimezoneFinder()
            timezone = tf.timezone_at(lng = update.message.location.longitude, lat = update.message.location.latitude)
            document = mongo.db.itemsList.find({"_id": update.message.chat.id})
            if len(list(document)) == 1:
                document.rewind()
                mongo.db.itemsList.update_one({"_id": update.message.chat.id}, {"$set": {"timezone": timezone}})
                message = f"Timezone updated to {timezone}!"
            else:
                mongo.db.itemsList.insert_one({"_id": update.message.chat.id, "lists": [], "timezone": timezone})
                message = f"Timezone setted!"
            update.message.reply_text(message)
            calledTimezone[update.message.chat.id] = False
        except StopIteration:
            calledTimezone[update.message.chat.id] = False
            print("StopIteration error: Rewinding Cursor object.")
            update.message.reply_text("Internal server error, sorry for the incoveniences")


def showTimezone(update,context):
    logMethod("/showTimezone", update.message.chat.id, context)
    if not len(context.args) == 0: 
        invalidCommandMessage(update)
    else:
        try:
            document = mongo.db.itemsList.find({"_id": update.message.chat.id})
            if len(list(document)) == 1:
                document.rewind()
                message = f"Your timezone is {document.next().get('timezone')}"
            else:
                message = "You have not set your timezone yet, please use /timezone command to save it."
            update.message.reply_text(message)
        except StopIteration:
            print("StopIteration error: Rewinding Cursor object.")
            update.message.reply_text("Internal server error, sorry for the incoveniences")

def changeName(update, context):
    logMethod("/changeName", update.message.chat.id, context)
    if not len(context.args) == 2: 
        invalidCommandMessage(update)
    else:
        if not RegexChecker.checkListName(context.args[0]):
            try:
                document = mongo.db.itemsList.find({"_id": update.message.chat.id}, {"lists": {"$elemMatch": {"name": context.args[0]}}})
                if document.next().get("lists") != None:
                    document.rewind()
                    mongo.db.itemsList.update_one({"_id": update.message.chat.id}, {"$set": {"lists.$[elem].name": context.args[1]}}, array_filters=[{"elem.name": context.args[0]}])
                    update.message.reply_text(f"List name changed to '{context.args[1]}'")
                else:
                    update.message.reply_text(f"You don't have any list with name '{context.args[0]}'! 😔")
            except StopIteration:
                print("StopIteration error: Rewinding Cursor object.")
                update.message.reply_text("Internal server error, sorry for the incoveniences")
        else:
            update.message.reply_text("Invalid list name, the name only can have letters, numbers and '_'")

def changeHour(update, context):
    logMethod("/changeHour", update.message.chat.id, context)
    if not len(context.args) == 3: 
        invalidCommandMessage(update)
    else:
        if RegexChecker.checkCorrectDatetime(" ".join(context.args[1:])):
            try:
                datetime.datetime.strptime(context.args[1], formatDate)
                datetime.datetime.strptime(context.args[2], formatHour)
                formatedDate = datetime.datetime.strptime(" ".join(context.args[1:]), formatDateAndHour)
                document = mongo.db.itemsList.find({"_id": update.message.chat.id})
                timezone = document.next().get("timezone")
                time = DatetimeParser.calculateSettedHour(formatedDate, timezone)
                timeWithoutOffset = time.replace(tzinfo=None)
                if timeWithoutOffset > datetime.datetime.today():
                        document = mongo.db.itemsList.find({"_id": update.message.chat.id}, {"lists": {"$elemMatch": {"name": context.args[0]}}})
                        if document.next().get("lists") != None:
                            document.rewind()
                            mongo.db.itemsList.update_one({"_id": update.message.chat.id}, {"$set": {"lists.$[elem].hour": str(time)}}, array_filters=[{"elem.name": context.args[0]}])
                            JobUtils.changeJob(context.args[0], str(time), update.message.chat.id)
                            update.message.reply_text(f"List reminder hour changed to '{' '.join(context.args[1:])}'")
                        else:
                            update.message.reply_text(f"You don't have any list with name '{context.args[0]}'! 😔")
                else: update.message.reply_text("Incorrect datetime. This datetime is before this moment!")
            except StopIteration:
                print("StopIteration error: Rewinding Cursor object.")
                update.message.reply_text("Internal server error, sorry for the incoveniences")
            except ValueError:
                print("Incorrect format datetime")
                update.message.reply_text("The datetime is not correct. Please insert a correct datetime.")
        else: update.message.reply_text("The datetime is not correct. Please insert a correct datetime.")

def removeItems(update, context):
    logMethod("/removeItems", update.message.chat.id, context)
    if not len(context.args) == 2: invalidCommandMessage(update)
    else:
        try:
            document = mongo.db.itemsList.find({"_id": update.message.chat.id}, {"lists": {"$elemMatch": {"name": context.args[0]} }})
            if document.next().get("lists") != None:
                document.rewind()
                oldItems = document.next().get("lists")[0].get("items").split(" ")
                finalItems = [item for item in oldItems if item not in context.args[1:]]
                finalItems = " ".join(finalItems)
                mongo.db.itemsList.update_one({"_id": update.message.chat.id}, {"$set": {"lists.$[elem].items": finalItems}}, array_filters=[{"elem.name": context.args[0]}])
                update.message.reply_text("Removed items!")
            else:  update.message.reply_text("You don't have any list with this name! 😔")
        except StopIteration:
            print("StopIteration error: Rewinding Cursor object.")
            update.message.reply_text("Internal server error, sorry for the incoveniences")

def changeItems(update, context):
    logMethod("/changeItems", update.message.chat.id, context)
    print(len(context.args))
    if len(context.args) < 4 : invalidCommandMessage(update)
    else:
        try:
            document = mongo.db.itemsList.find({"_id": update.message.chat.id}, {"lists": {"$elemMatch": {"name": context.args[0]} }})
            if document.next().get("lists") != None:
                document.rewind()
                oldItems = document.next().get("lists")[0].get("items").split(" ")
                finalItems = [item for item in oldItems if item not in context.args[1]]
                finalItems.append(context.args[3])
                finalItems = " ".join(finalItems)
                mongo.db.itemsList.update_one({"_id": update.message.chat.id}, {"$set": {"lists.$[elem].items": finalItems}}, array_filters=[{"elem.name": context.args[0]}])
                update.message.reply_text("Items have been changed!")
            else:  update.message.reply_text("You don't have any list with this name! 😔")
        except StopIteration:
            print("StopIteration error: Rewinding Cursor object.")
            update.message.reply_text("Internal server error, sorry for the incoveniences")

def echo(update, context):
    logMethod("/echo", update.message.chat.id, context)
    update.message.reply_text("Welcome to WriteItDown Bot! 😈")
    help(update, context)

def repeat(update, context):
    logMethod("/repeat", update.message.chat.id, context)
    if not (context.args == None or len(context.args) == 0): 
        update.message.reply_text(" ".join(update.message.text.split("/repeat")))
    else: 
        update.message.reply_text("Don't be shy, send anything! 😛")

def help(update, context):
    logMethod("/help", update.message.chat.id, context)
    allCommands = f"List of commands: 😎\n\n"
    allCommands += "1. /repeat text: Returns the sent message.\n"
    allCommands += "2. /timezone: Sets your timezone using your location. Example: Europe/Madrid\n"
    allCommands += "3. /save name items hour : Saves a list and sets a reminder hour.\n"
    allCommands += "4. /add name items : Adds items to an existing list.\n"
    allCommands += "5. /remove name : Deletes an existing list.\n"
    allCommands += "6. /show name : Shows a description of the list.\n"
    allCommands += "7. /showAll : Shows all saved list names.\n"
    allCommands += "8. /changeName oldName newName : Changes the name of a created list.\n"
    allCommands += "9. /changeHour name hour : Changes the reminder hour of a created list. If the new hour is = 0, the reminder hour will be deleted.\n"
    allCommands += "10. /removeItems name items : Deletes the items of a list.\n"
    allCommands += "11. /changeItems list oldItems . newItems : Removes old items and adds the new items.\n"
    allCommands += "12. /showTimezone: Shows your saved timezone.\n"
    update.message.reply_text(allCommands)

def invalidCommandMessage(update):
    update.message.reply_text("Incorrect command!")

def logMethod(method, idChat, context):
    if context.args != None:
        log.info(f"User {idChat} >> Command {method} {' '.join(context.args)}")
    else: log.info(f"User {idChat} >> Command {method}") 

def sendReminderMessage(idChat, listName):
    document = mongo.db.itemsList.find({"_id": idChat}, {"lists": {"$elemMatch": {"name": listName} }})
    try:
        year = document.next().get("lists")[0].get("hour").split(" ")[0].split("-")[0]
        if str(datetime.datetime.today().year) == year:
            bot.send_message(idChat, f"Reminder of list '{listName}'!")
            JobUtils.removeJob(idChat, listName)
    except StopIteration as err:
        print("StopIteration error:", err, "-- rewinding Cursor object.")

def main():
    log.info(sys.argv)
    updater = Updater(configuration.token, use_context=True)
    dp = updater.dispatcher
    global bot
    bot = dp.bot
    log.info("Bot: " + str(bot))
    if len(sys.argv) > 1:
        eval(sys.argv[1])
        return
    dp.add_handler(CommandHandler("save", save))
    dp.add_handler(CommandHandler("repeat", repeat))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("remove", remove))
    dp.add_handler(CommandHandler("show", show))
    dp.add_handler(CommandHandler("showAll", showAll))
    dp.add_handler(CommandHandler("timezone", timezoneMessage))
    dp.add_handler(CommandHandler("showTimezone", showTimezone))
    dp.add_handler(CommandHandler("changeName", changeName))
    dp.add_handler(CommandHandler("changeHour", changeHour))
    dp.add_handler(CommandHandler("removeItems", removeItems))
    dp.add_handler(CommandHandler("changeItems", changeItems))
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.location, setTimezone))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()