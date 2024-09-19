class Token():
    """Classe pour représenter le Token sur le bus."""

    def __init__(self, to: int = 0):
        self.to = to

    def getTo(self):
        return self.to
    
    def setTo(self, to):
        self.to = to