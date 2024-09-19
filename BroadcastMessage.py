from Message import Message

class BroadcastMessage(Message):
    """Classe utilisée pour émettre des messages en Broadcast asynchrone"""

    def __init__(self, clock=0, payload=None, sender=0):
        Message.__init__(self, clock, payload, sender)

    def __str__(self):
        return super().__str__()
    

class BroadcastMessageSync(Message):
    """Classe utilisée pour émettre des messages en Broadcast synchrone"""
    
    def __init__(self, clock=0, payload=None, sender=0):
        super().__init__(clock, payload, sender)