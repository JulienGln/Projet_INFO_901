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

    def run(self):
        loop = 0

        while self.alive:
            print(self.getName() + " Loop: " + str(loop))
            sleep(1)

            if self.getName() == "P1":
                self.com.sendTo("Salut !", 2)

            loop += 1
        print(self.getName() + " stopped")

    def stop(self):
        self.alive = False

    def waitStopped(self):
        self.join()