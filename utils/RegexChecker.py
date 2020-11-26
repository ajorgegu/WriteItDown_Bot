import re

def checkListName(name):
    return re.findall("\\W", name)

def checkCorrectDatetime(datetime):
    return re.findall("(\\d{4})-(\\d{2})-(\\d{2}) (\\d{2}):(\\d{2}):(\\d{2})", datetime)