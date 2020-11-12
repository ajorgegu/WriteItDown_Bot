class ItemsList:
    def __init__(self, name, items, hour):
        self.name = name
        self.items = [items]
        self.hour = hour
    
    def showList(self):
        itemsSplitted = lambda items: items.join('\n')
        itemsToShow = itemsSplitted(self.items)
        print(str(itemsToShow))
        var = "Lista" + self.name + '\n' + "Items: " + itemsToShow + '\n' + "Recordatorio: " + self.hour
        print(var)
        return "Lista" + self.name + '\n' + "Items: " + itemsToShow + '\n' + "Recordatorio: " + self.hour