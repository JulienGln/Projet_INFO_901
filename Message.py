class Message():
    """Classe de messages génériques"""

    def __init__(self, stamp=0, payload=None, sender=0):
        self.stamp = stamp
        self.payload = payload
        self.sender = sender

    def getPayload(self):
        return self.payload
    
    def getStamp(self):
        return self.stamp
    
    def setStamp(self, stamp):
        self.stamp = stamp

    def getSender(self):
        return self.sender

    def __str__(self):
        return str(self.payload)