from Message import Message

class MessageTo(Message):

    def __init__(self, clock=0, payload=None, sender=0, to=0):
        Message.__init__(self, clock, payload, sender)
        self.to = to

    def getTo(self):
        return self.to
    
    def setTo(self, to):
        self.to = to

    def __str__(self):
        return super().__str__()