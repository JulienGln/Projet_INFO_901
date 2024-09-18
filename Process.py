from threading import Thread, Lock
from Com import Com

class Process(Thread):

    def __init__(self, name):
        Thread.__init__(self)

        self.com = Com()

        self.nbProcess = self.com.getNbProcess()

        self.myId = self.com.getMyId()
        self.setName(name)


        self.alive = True
        self.start()

    def run(self):
        loop = 0

        while self.alive:
            loop += 1

        print(self.getName() + " stopped")