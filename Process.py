from threading import Thread, Lock
from Com import Com
from time import sleep

class Process(Thread):

    def __init__(self, name, nbProcess):
        Thread.__init__(self)

        self.com = Com(nbProcess)

        self.nbProcess = self.com.getNbProcess()

        self.myId = self.com.getMyId()
        self.setName(name)


        self.alive = True
        self.start()

    def testAsynchrone(self):
        if self.getName() == "P1":
            self.com.sendTo("Salut !", 2)

        elif self.getName() == "P0":
            self.com.broadcast("Je vous spam tous !")

    def testSectionCritique(self):
        if self.getName() == "P1":
            self.com.sendTo("Salut !", 2)

        elif self.getName() == "P0":
            self.com.requestSC()
            self.com.broadcast("Je vous spam tous !")
            self.com.releaseSC()
        
        elif self.getName() == "P2":
            self.com.requestSC()
            self.com.broadcast("P2 accède à la section critique")
            print(f"P2 : Je suis dans la SC")
            sleep(0.5)
            self.com.releaseSC()

    def testBroadcastSynchrone(self):
        if self.getName() == "P1":
            self.com.broadcastSync(None, 0)

        elif self.getName() == "P0":
            self.com.broadcastSync("Je vous spam tous !", self.myId)
        
        elif self.getName() == "P2":
            self.com.broadcastSync(None, 0)

    def testMsgSynchrone(self):
        if self.getName() == "P2":
            self.com.recevFromSync(None, 0)

        elif self.getName() == "P0":
            self.com.sendToSync("Mesage synchrone pour P2", 2)


    def run(self):
        loop = 0

        while self.alive:
            print(self.getName() + " Loop: " + str(loop))
            sleep(1)

            # self.testAsynchrone()
            # self.testSectionCritique()
            # self.testBroadcastSynchrone()
            self.testMsgSynchrone()

            loop += 1
        print(self.getName() + " stopped")

    def stop(self):
        self.alive = False
        self.com.processDie()

    def waitStopped(self):
        self.join()