from Message import Message

class MessageTo(Message):

    def __init__(self, clock=0, payload=None, to=0):
        Message.__init__(self, clock, payload)
        self.to = to

    def getTo(self):
        return self.to
    
    def setTo(self, to):
        self.to = to