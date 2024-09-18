class Mailbox():

    def __init__(self):
        self.messages = []

    def isEmpty(self):
        return len(self.messages) == 0

    def getMsg(self):
        pass