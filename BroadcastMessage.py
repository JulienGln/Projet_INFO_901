from Message import Message

class BroadcastMessage(Message):

    def __init__(self, clock=0, payload=None):
        Message.__init__(self, clock, payload)