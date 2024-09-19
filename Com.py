from threading import Lock
from time import sleep

from Mailbox import Mailbox
from BroadcastMessage import BroadcastMessage, BroadcastMessageSync
from MessageTo import MessageTo, MessageToSync
from Token import Token
from Barrier import Barrier

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
        self.processAlive = True

        self.etat = "null"
        self.barrier = False

        PyBus.Instance().register(self, self)

        # Lancement du token 
        if self.myId == self.nbProcess - 1:
            token = Token(to=0)
            PyBus.Instance().post(token)

    def getMyId(self):
        return self.myId

    def getNbProcess(self):
        return self.nbProcess
    
    def inc_clock(self, other_stamp = 0):
        """L'horloge s'incrémente de 1 pour les envois et s'incrémente du max(mon horloge, l'horloge de l'autre) + 1 pour les réceptions"""
        with self.lock:
            self.clock = max(self.clock, other_stamp) + 1
            print(f"Horloge de P{self.myId} = {self.clock}")

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
        """Demande de SC en attente active pour l'instant"""
        self.etat = "request"

        # if self.processAlive:
        #     print(f"Acquisition du verrou par P{self.myId}")
        #     self.lock.acquire(blocking=True, timeout=5)
        while self.etat != "SC" and self.processAlive:
            sleep(1)

    def releaseSC(self):
        self.etat = "release"
        # self.lock.release()

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Token)
    def onToken(self, token: Token):
        """Réception du token et traitement"""
        if token.getTo() == self.myId:
            if self.etat == "request":
                self.etat = "SC"

                while self.etat != "release":
                    sleep(1)
                
                print(f"P{self.myId}: J'ai relaché la SC")
                self.etat = "null"
            
            next = (self.myId + 1) % self.nbProcess
            token.setTo(next)
            if self.processAlive:
                PyBus.Instance().post(token)

    # BARRIERE DE SYNCHRONISATION #

    def synchronize(self):
        """Méthode appelée par un processus lorsqu'il veut se synchroniser (barrière de synchronisation)"""
        leader = 0

        if self.myId == leader:
            print(f"Le leader {leader} envoie : \"J'attends à la barrière\"")
            self.inc_clock()
            PyBus.Instance().post(Barrier(clock=self.clock, payload="J'attends à la barrière", sender=self.myId))

        else: # peut-être à enlever...
            self.barrier = True
            while self.barrier:
                sleep(0.5)
            print(f"P{self.myId} quitte la barrière...")

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Barrier)
    def onBarrier(self, msg: Barrier):
        leader = 0
        next = (self.myId + 1) % self.nbProcess
        prev = (self.myId - 1) % self.nbProcess

        self.inc_clock(msg.getStamp())

        if self.myId == leader and msg.getSender() == prev:
            print(f"Le leader {leader} envoie : \"Tout le monde est à la barrière\"")
            self.inc_clock()
            PyBus.Instance().post(Barrier(clock=self.clock, payload="Tout le monde est à la barrière", sender=self.myId))
        
        else:
            if msg.getSender() == prev:

                if msg.getPayload() == "J'attends à la barrière":
                    print(f"P{self.myId} a reçu le message d'attente de P{msg.getSender()} et le transmet à P{next}")
                    self.inc_clock()
                    PyBus.Instance().post(Barrier(clock=self.clock, payload=msg.getPayload(), sender=self.myId))

                elif msg.getPayload() == "Tout le monde est à la barrière":
                    self.barrier = False


    # COMMUNICATION SYNCHRONE #

    def broadcastSync(self, obj, sender: int):
        """Broadcast synchrone"""
        ack = "ACK BROADCAST"
        if self.myId == sender:
            self.inc_clock()
            msg = BroadcastMessageSync(clock=self.clock, payload=obj, sender=self.myId)
            PyBus.Instance().post(msg)
            print(f"P{self.myId}: J'envoie en broadcast synchrone...")

            #  Attend que tous les autres process aient le message pour repartir faire sa vie
            nbReception = 0

            while nbReception < self.nbProcess - 1:
                sleep(1)
                msg = self.mailbox.getMsgOfType(MessageTo)

                if msg != None and msg.getPayload() == ack:
                    nbReception += 1

            print(f"P{self.myId}: Tout le monde a reçu, je passe à autre chose.")

        else:
            recvMsg = self.mailbox.getMsgOfType(BroadcastMessageSync)
            timeout = 0

            while recvMsg == None:
                sleep(1)
                recvMsg = self.mailbox.getMsgOfType(BroadcastMessageSync)
                timeout += 1

            print(f"P{self.myId}: J'ai reçu \"{recvMsg.getPayload()}\" de P{recvMsg.getSender()}")
            # Envoi d'un acquittement
            PyBus.Instance().post(MessageTo(clock=self.clock, payload=ack, sender=self.myId, to=sender))

    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessageSync)
    def onBroadcastSync(self, msg: BroadcastMessageSync):
        self.inc_clock(msg.getStamp())
        self.mailbox.add(msg)


    def sendToSync(self, obj, dest: int):
        """Méthode d'envoi synchrone spécifique"""
        self.inc_clock()
        msg = MessageToSync(clock=self.clock, payload=obj, sender=self.myId, to=dest)
        PyBus.Instance().post(msg)

        msg = self.mailbox.getMsgOfType(MessageTo)
        while msg == None or msg.getTo() != self.myId or msg.getPayload() != "ACK MESSAGE SYNC":
            sleep(1)
            msg = self.mailbox.getMsgOfType(MessageTo)
        print(f"P{self.myId}: P{dest} a bien reçu mon message. Je passe à autre chose...")

    def recevFromSync(self, obj, sender: int):
        """Récupère de la boîte aux lettres, de manière bloquante, le message de `sender`"""
        msg = self.mailbox.getMsgOfType(MessageToSync)

        print(f"P{self.myId}: J'attends un message de P{sender}...")
        timeout = 0
        while (msg == None or msg.getSender() != sender):
            sleep(1)
            msg = self.mailbox.getMsgOfType(MessageToSync)
            if timeout >= 5:
                print(f"P{self.myId}: Timeout dépassé, j'abandonne...")
                return
            timeout += 1
        print(f"P{self.myId}: J'ai reçu dans ma boîte \"{msg.getPayload()}\" de la part de {msg.getSender()}")
        # Acquittement
        self.inc_clock()
        PyBus.Instance().post(MessageTo(clock=self.clock, payload="ACK MESSAGE SYNC", sender=self.myId, to=sender))

    @subscribe(threadMode=Mode.PARALLEL, onEvent=MessageToSync)
    def onMessageToSync(self, msg: MessageToSync):
        if msg.getTo() == self.myId:
            self.inc_clock(msg.getStamp())
            self.mailbox.add(msg)


    # AUTRES METHODES #

    def processDie(self):
        """Appelée par le processus pour signaler au communicateur qu'il est mort"""
        self.processAlive = False