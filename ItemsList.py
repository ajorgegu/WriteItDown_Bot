class ItemsList:

    def __init__(self, name, items, hour):
        self.name = name
        self.items = items.split(" ")
        self.hour = hour
    
    def showList(self):
        itemsInLines = lambda items: '\n'.join(items)
        itemsToShow = itemsInLines(self.items)
        return f"List '{self.name}'\n--------------\nItems: {itemsToShow}\nHour: {self.hour}"