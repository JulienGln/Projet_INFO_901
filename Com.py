from threading import Lock
from time import sleep
from random import randint

from Mailbox import Mailbox
from BroadcastMessage import BroadcastMessage, BroadcastMessageSync
from MessageTo import MessageTo, MessageToSync
from Token import Token
from Barrier import Barrier
from Numerotation import Numerotation

from pyeventbus3.pyeventbus3 import *

class Com():
    """Classe communicateur pour l’envoi et la réception de message"""
    # nbProcessCreated = 0

    def __init__(self, nbProcess):
        self.clock = 0
        self.nbProcess = nbProcess
        self.myId = 0 # ID provisoire #Com.nbProcessCreated
        # Com.nbProcessCreated += 1

        self.clockLock = Lock()
        self.scLock = Lock()

        self.mailbox = Mailbox()
        self.processAlive = True

        self.etat = "null"
        self.barrier = False

        PyBus.Instance().register(self, self)


    def getMyId(self):
        return self.myId

    def getNbProcess(self):
        return self.nbProcess
    
    def inc_clock(self, other_stamp = 0):
        """L'horloge s'incrémente de 1 pour les envois et s'incrémente du max(mon horloge, l'horloge de l'autre) + 1 pour les réceptions"""
        with self.clockLock:
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
        """Demande de section critique"""
        self.etat = "request"

        if self.etat != "SC" and self.processAlive:
            print(f"Acquisition du verrou par P{self.myId}")
            self.scLock.acquire(blocking=True, timeout=5)
            
        # while self.etat != "SC" and self.processAlive:
        #     sleep(1)

    def releaseSC(self):
        """Libération de la section critique"""
        print(f"Etat P{self.myId} : {self.etat}")
        self.etat = "release"
        if self.scLock.locked():
            self.scLock.release()

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Token)
    def onToken(self, token: Token):
        """Réception du token et traitement"""
        if token.getTo() == self.myId:
            if self.etat == "request":
                self.etat = "SC"

                # while self.etat != "release":
                while self.scLock.locked():
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

        # else:
        self.barrier = True
        while self.barrier and self.processAlive:
            sleep(0.5)
        print(f"P{self.myId} quitte la barrière...")

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Barrier)
    def onBarrier(self, msg: Barrier):
        """Réception des messages de type `Barrier`"""
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
                if timeout >= 3:
                    print(f"P{self.myId}: Timeout dépassé, j'abandonne...")
                    return
                timeout += 1

            print(f"P{self.myId}: J'ai reçu \"{recvMsg.getPayload()}\" de P{recvMsg.getSender()}")
            # Envoi d'un acquittement
            PyBus.Instance().post(MessageTo(clock=self.clock, payload=ack, sender=self.myId, to=sender))

    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessageSync)
    def onBroadcastSync(self, msg: BroadcastMessageSync):
        """Réception d'un message de broadcast synchrone depuis le bus et ajout dans la boîte aux lettres. 
        Le reste de la logique est gérée dans la méthode `broadcastSync()`"""

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
        """Réception d'un message dédié synchrone depuis le bus et ajout dans la boîte aux lettres. 
        Le reste de la logique est gérée dans la méthode `recevFromSync()`"""

        if msg.getTo() == self.myId:
            self.inc_clock(msg.getStamp())
            self.mailbox.add(msg)


    # AUTRES METHODES #

    def processDie(self):
        """Appelée par le processus pour signaler au communicateur qu'il est mort"""
        self.processAlive = False

    def init(self):
        """Init appelée par le processus"""
        self.numerotationAutomatique()

        # Lancement du token 
        if self.myId == self.nbProcess - 1:
            token = Token(to=0)
            PyBus.Instance().post(token)

    def numerotationAutomatique(self):
        """
        Chaque processus tire un nb aléatoire. Il est envoyé sur le bus et est réceptionné par les autres (méthode `onNumerotation()`). \n
        Les processus classent dans un tableau leur numéro et celui des autres. \n
        Si un numéro est identique à un autre, laprocédure est recommencée. \n
        Enfin, la valeur de retour est l'index du nb tiré par le processus dans le tableau trié.
        Cette valeur sera utilisée en guise d'ID du processus.
        """
        nb = randint(0, self.nbProcess * 1000)
        PyBus.Instance().post(Numerotation(payload=nb))

        sleep(1)
        tab = []
        for _ in range(self.nbProcess):
            msg = self.mailbox.getMsgOfType(Numerotation)
            if msg == None:
                sleep(0.5)
                msg = self.mailbox.getMsgOfType(Numerotation)
            tab.append(int(msg.getPayload()))
        tab.sort()

        for i in range(len(tab) - 1):
            if tab[i] == tab[i+1]:
                return self.numerotationAutomatique()
        
        self.myId = tab.index(nb)
        return tab.index(nb)

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Numerotation)
    def onNumerotation(self, msg: Numerotation):
        self.mailbox.add(msg)
        print(f"Mailbox de P{self.myId} : {self.mailbox}")