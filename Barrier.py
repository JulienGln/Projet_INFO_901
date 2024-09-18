from Message import Message

class Barrier(Message):

    def __init__(self, clock=0, payload=None, sender=0):
        super().__init__(clock, payload)
        self.sender = sender

    def getSender(self):
        return self.sender