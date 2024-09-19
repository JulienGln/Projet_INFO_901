class Mailbox():
    """Classe qui représente la boîte aux lettres du communicateur"""

    def __init__(self):
        self.messages = []

    def isEmpty(self):
        return len(self.messages) == 0

    def getMsg(self):
        """Retire et retourne le premier message de la boîte aux lettres. Retourne `None` si la boîte est vide."""
        if not self.isEmpty():
            return self.messages.pop(0)
        return None
        
    def getMsgOfType(self, type):
        """Retire et renvoie le premier message du `type` précisé. Retourne `None` si il n'y a aucun message de ce `type`."""
        for i, msg in enumerate(self.messages):
            if isinstance(msg, type):
                return self.messages.pop(i)
        return None

    def add(self, msg):
        self.messages.append(msg)

    def __str__(self):
        res = "[ "

        for i in range(len(self.messages)):
            msg = self.messages[i]
            res += f"{msg.getPayload()} [sender=P{msg.getSender()}]"
            if i != len(self.messages) - 1:
                res += ", "
        
        return res + " ]"