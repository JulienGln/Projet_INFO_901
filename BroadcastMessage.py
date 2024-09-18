from Message import Message

class BroadcastMessage(Message):

    def __init__(self, clock=0, payload=None, sender=0):
        Message.__init__(self, clock, payload, sender)

    def __str__(self):
        return super().__str__()