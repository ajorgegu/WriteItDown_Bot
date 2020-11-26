from crontab import CronTab
import pathlib
cron = CronTab(user=True)

def createJob(itemList, idChat):
    datetime = itemList.hour.split(" ")
    date = datetime[0].split("-")
    hour = datetime[1].split(":")

    job = cron.new(command=f"python3 {pathlib.Path(__file__).parent.absolute()}/../WriteItDownApplication.py 'sendReminderMessage({idChat}, \"{itemList.name}\")'")
    job.set_comment(f"{idChat}_{itemList.name}")
    job.setall(hour[1], hour[0], date[2], date[1], None)
    cron.write()

def changeJob(nameList, hour, idChat):
    datetime = hour[:len(hour)-6]
    datetime = datetime.split(" ")
    date = datetime[0].split("-")
    hour = datetime[1].split(":")
    jobs = cron.find_comment(f"{idChat}_{nameList}")
    for job in jobs:
        job.setall(hour[1], hour[0], date[2], date[1], None)
        cron.write()

def removeJob(idChat, listName):
    print(f"{idChat}_{listName}")
    cron.remove_all(comment=f"{idChat}_{listName}")
    cron.write()