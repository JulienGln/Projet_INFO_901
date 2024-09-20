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
            self.com.requestSC()
            self.com.sendTo("Salut !", 2)
            self.com.releaseSC()

        if self.getName() == "P0":
            self.com.requestSC()
            self.com.broadcast("Je vous spam tous !")
            self.com.releaseSC()
        
        elif self.getName() == "P2":
            self.com.requestSC()
            self.com.broadcast("P2 accède à la section critique")
            self.com.releaseSC()

    def testSynchronize(self):
        if self.getName() == "P1":
            self.com.sendTo("Salut !", 2)
            self.com.synchronize()

        elif self.getName() == "P0":
            self.com.broadcast("Je vous spam tous !")
            self.com.synchronize()
        
        elif self.getName() == "P2":
            self.com.broadcast("Hello !")
            sleep(0.5)
            self.com.synchronize()

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
            self.com.sendToSync("Message synchrone pour P2", 2)

    def testExempleInitial(self):
        if self.getName() == "P0":
            self.com.sendTo("j'appelle 2 et je te recontacte après", 1)
            
            self.com.sendToSync("J'ai laissé un message à 2, je le rappellerai après, on se sychronise tous et on attaque la partie ?", 2)
            msg = None
            self.com.recevFromSync(msg, 2)
            
            self.com.sendToSync("2 est OK pour jouer, on se synchronise et c'est parti!",1)
                
            self.com.synchronize()
                
            self.com.requestSC()
            if self.com.mailbox.isEmpty():
                print("Catched !")
                self.com.broadcast("J'ai gagné !!!")
            else:
                msg = self.com.mailbox.getMsg()
                print(str(msg.getSender())+" a eu le jeton en premier")
            self.com.releaseSC()


        if self.getName() == "P1":
            if not self.com.mailbox.isEmpty():
                msg = self.com.mailbox.getMsg()
                self.com.recevFromSync(msg, 0)

                self.com.synchronize()
                
                self.com.requestSC()
                if self.com.mailbox.isEmpty():
                    print("Catched !")
                    self.com.broadcast("J'ai gagné !!!")
                else:
                    msg = self.com.mailbox.getMsg()
                    print(str(msg.getSender())+" a eu le jeton en premier")
                self.com.releaseSC()
                
        if self.getName() == "P2":
            msg = None
            self.com.recevFromSync(msg, 0)
            self.com.sendToSync("OK", 0)

            self.com.synchronize()
                
            self.com.requestSC()
            if self.com.mailbox.isEmpty():
                print("Catched !")
                self.com.broadcast("J'ai gagné !!!")
            else:
                msg = self.com.mailbox.getMsg()
                print(str(msg.getSender())+" a eu le jeton en premier")
            self.com.releaseSC()


    def run(self):
        loop = 0

        sleep(1)
        self.com.init()
        self.myId = self.com.getMyId()
        print(f"{self.getName()}: ID après numérotation = {self.myId}")
        self.setName(f"P{self.myId}")

        while self.alive:
            print(self.getName() + " Loop: " + str(loop))
            sleep(1)

            # self.testAsynchrone()
            # self.testSectionCritique()
            # self.testSynchronize()
            # self.testBroadcastSynchrone()
            # self.testMsgSynchrone()
            self.testExempleInitial()

            loop += 1
        print(self.getName() + " stopped")

    def stop(self):
        self.alive = False
        self.com.processDie()

    def waitStopped(self):
        self.join()