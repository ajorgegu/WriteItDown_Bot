class BotConfiguration:

    def __init__(self):
        settingsFile = open("settings.txt", "r")
        settingsFile = settingsFile.readlines()
        for line in settingsFile:
            if line.split("=")[0] == "TOKEN": self.token = line.split("=")[1].strip()
            if line.split("=")[0] == "URL": self.url = line.split("=")[1].strip()