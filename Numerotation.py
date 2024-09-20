from Message import Message

class Numerotation(Message):

    def __init__(self, stamp=0, payload=None, sender=0):
        super().__init__(stamp, payload, sender)