class Mailbox():

    def __init__(self):
        self.messages = []

    def isEmpty(self):
        return len(self.messages) == 0

    def getMsg(self):
        if not self.isEmpty():
            return self.messages.pop(0)
        
    def getMsgOfType(self, type):
        """Renvoie le premier message du type précisé"""
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