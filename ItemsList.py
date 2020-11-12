class ItemsList:

    def __init__(self, name, items, hour):
        self.name = name
        self.items = items.split(" ")
        self.hour = hour
    
    def showList(self):
        itemsInLines = lambda items: '\n'.join(items)
        itemsToShow = itemsInLines(self.items)
        return f"Lista {self.name}:\nItems--> {itemsToShow}\nRecordatorio--> {self.hour}"