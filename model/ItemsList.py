class ItemsList:

    def __init__(self, name, items, hour):
        self.name = name
        self.items = " ".join(items)
        self.hour = hour
    
    def showList(self):
        message =  f"╔═╣ {self.name} ╠══"
        message += (13-len(self.name))*"═" + "╗\n"
        message += f"║\n"
        if len(self.items) < 28:
            message += f"╠ Items » {self.items}\n"
        else: 
            size = int(len(self.items) / 20)
            for i in range(size):
                if i == 0:
                    message += f"╠ Items » {self.items[0:20]}\n"
                else: 
                    message += f"║ {       self.items[20*i:20*i+20]}\n"

        message += f"╠ Hour  » {self.hour}\n"
        message += f"╚═══════════════════╝"
        return message
