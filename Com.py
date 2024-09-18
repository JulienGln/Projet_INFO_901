from threading import Lock
from time import sleep

from Mailbox import Mailbox
from BroadcastMessage import BroadcastMessage
from MessageTo import MessageTo

from pyeventbus3.pyeventbus3 import *

class Com():
    """Classe communicateur pour l’envoi et la réception de message"""
    nbProcessCreated = 0

    def __init__(self, nbProcess):
        self.clock = 0
        self.nbProcess = nbProcess
        self.myId = Com.nbProcessCreated
        Com.nbProcessCreated += 1
        self.lock = Lock()
        self.mailbox = Mailbox()

        self.etat = "null"

        PyBus.Instance().register(self, self)

    def getMyId(self):
        return self.myId

    def getNbProcess(self):
        return self.nbProcess
    
    def inc_clock(self, other_stamp = 0):
        with self.lock:
            self.clock = max(self.clock, other_stamp) + 1

    # COMMUNICATION ASYNCHRONE #

    def broadcast(self, obj):
        """Envoi en broadcast asynchrone d'un message `obj` sur le bus"""
        self.inc_clock()
        msg = BroadcastMessage(clock=self.clock, payload=obj, sender=self.myId)
        PyBus.Instance().post(msg)

    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, m: BroadcastMessage):
        """Réception d'un broadcast `m` (sauf pour l'envoyeur !)"""
        if self.myId != m.getSender():
            self.inc_clock(m.getStamp())
            self.mailbox.add(m)
            print(f"Mailbox de P{self.myId} : {self.mailbox}")

    def sendTo(self, obj, dest: int):
        """Envoi d'un message `obj` à un processus en particulier `dest` sur le bus"""
        self.inc_clock()
        msg = MessageTo(clock=self.clock, payload=obj, sender=self.myId, to=dest)
        print(f"P{self.myId} envoie \"{msg}\" à P{dest}")
        PyBus.Instance().post(msg)

    @subscribe(threadMode=Mode.PARALLEL, onEvent=MessageTo)
    def onReceive(self, m: MessageTo):
        """Réception d'un message dédié `m`"""
        if self.myId == m.getTo():
            self.inc_clock(m.getStamp())
            self.mailbox.add(m)
            print(f"Mailbox de P{self.myId} : {self.mailbox}")

    #  SECTION CRITIQUE ET GESTION DU TOKEN #

    def requestSC(self):
        self.etat = "request"

        self.lock.acquire(blocking=True, timeout=5)
        # while self.etat != "SC": # and self.alive
        #     sleep(1)

    def releaseSC(self):
        self.etat = "release"
        self.lock.release()

    def synchronize(self):
        pass

    # COMMUNICATION SYNCHRONE #

    def broadcastSync(self, obj, sender: int):
        pass

    def sendToSync(self, obj, dest: int):
        pass

    def recevFromSync(self, obj, sender: int):
        pass