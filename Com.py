from threading import Lock
from time import sleep

from Mailbox import Mailbox

from pyeventbus3.pyeventbus3 import *

class Com():
    """Classe communicateur pour l’envoi et la réception de message"""

    def __init__(self):
        self.clock = 0
        self.nbProcess = 0
        self.myId = 0
        self.lock = Lock()
        self.mailbox = Mailbox()

        self.etat = "null"

    def getMyId(self):
        return self.myId

    def getNbProcess(self):
        return self.nbProcess
    
    def inc_clock(self):
        with self.lock:
            self.clock += 1

    def broadcast(self, obj):
        pass

    def sendTo(self, obj, dest: int):
        pass

    #  SECTION CRITIQUE ET GESTION DU TOKEN #

    def requestSC(self):
        self.etat = "request"

        # Utiliser une attente passive plutôt
        while self.etat != "SC": # and self.alive
            sleep(1)

    def releaseSC(self):
        self.etat = "release"

    def synchronize(self):
        pass

    # COMMUNICATION SYNCHRONE #

    def broadcastSync(self, obj, sender: int):
        pass

    def sendToSync(self, obj, dest: int):
        pass

    def recevFromSync(self, obj, sender: int):
        pass