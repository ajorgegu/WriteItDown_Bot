from pymongo import MongoClient

class MongoDbConfiguration:

    def __init__(self):
        settingsFile = open("/home/alejandro.jorge/WriteItDown_Bot/settings.txt", "r")
        settingsFile = settingsFile.readlines()
        for line in settingsFile:
            if line.split("=")[0] == "MONGO": mongoUrl = "=".join(line.split("=")[1:]).strip()
            if line.split("=")[0] == "MONGOPASSWORD": mongoPassword = line.split("=")[1].strip()
            if line.split("=")[0] == "MONGODBNAME": mongoDbName = line.split("=")[1].strip() 
        mongoUrl = mongoUrl.replace("<password>", mongoPassword).replace("<dbname>", mongoDbName)
        client = MongoClient(mongoUrl)
        self.db = client.writeitdowm