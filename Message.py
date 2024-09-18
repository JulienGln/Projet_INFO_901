class Message():
    """Classe de messages génériques"""

    def __init__(self, stamp=0, payload=None):
        self.stamp = stamp
        self.payload = payload

    def getPayload(self):
        return self.payload
    
    def getStamp(self):
        return self.stamp
    
    def setStamp(self, stamp):
        self.stamp = stamp

    def __str__(self):
        return str(self.payload)