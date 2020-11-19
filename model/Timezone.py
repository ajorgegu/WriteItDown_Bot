import json

class Timezone: 

    def __init__(self):
        self.us = []
        self.europe = []
        self.africa = []
        self.america = []
        self.asia = []
        self.australia = []
        self.pacific = []
        self.indian = []
        self.atlantic = []
        self.antarctica = []
        self.artic = []
        with open("timezones.json") as timezonesFile:
            timezones = json.load(timezonesFile)
            for item in timezones:
                if item["group"] == "US (Common)":
                    values = item["zones"]
                    for value in values:
                        self.us.append(value["value"])
                elif item["group"] == "America":
                    values = item["zones"]
                    for value in values:
                        self.america.append(value["value"])
                elif item["group"] == "Europe":
                    values = item["zones"]
                    for value in values:
                        self.europe.append(value["value"])
                elif item["group"] == "Asia":
                    values = item["zones"]
                    for value in values:
                        self.asia.append(value["value"])
                elif item["group"] == "Africa":
                    values = item["zones"]
                    for value in values:
                        self.africa.append(value["value"])
                elif item["group"] == "Pacific":
                    values = item["zones"]
                    for value in values:
                        self.pacific.append(value["value"])
                elif item["group"] == "Australia":
                    values = item["zones"]
                    for value in values:
                        self.australia.append(value["value"])
                elif item["group"] == "Indian":
                    values = item["zones"]
                    for value in values:
                        self.indian.append(value["value"])
                elif item["group"] == "Atlantic":
                    values = item["zones"]
                    for value in values:
                        self.atlantic.append(value["value"])
                elif item["group"] == "Antarctica":
                    values = item["zones"]
                    for value in values:
                        self.antarctica.append(value["value"])
                elif item["group"] == "Artic":
                    values = item["zones"]
                    for value in values:
                        self.artic.append(value["value"])
        
    def showTimezones(self):
        return f"Europe: \n{self.europe}"
