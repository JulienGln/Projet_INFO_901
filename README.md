# Projet_INFO_901
## Réalisation d’un intergiciel (middleware) dans le cadre du module INFO 901 - Algorithmes distribués
### GALERNE Julien

# Lancement du projet
Le programme principal se trouve dans le fichier [`Launcher.py`](./Launcher.py). Il utilise les threads des processus de la classe `Process` du fichier [`Process.py`](./Process.py).

Le programme se lance avec la commande suivante :
>```$ python3 Launcher.py```

Le projet n'utilise pas de bibliothèques tierces hors celles incluses dans le langage de base (`threading`, `time`, etc.) et hormis la bibliothèque `pyeventbus3`.
>```$ pip install pyeventbus3```

## Programme principal (méthode run de Process.py)
```py
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
        self.testMsgSynchrone()

        loop += 1
    print(self.getName() + " stopped")
```

Des méthodes nommées `test[...]` sont disponibles pour tester chaque partie du projet.

# Explication des classes
## Communication asynchrone
La classe [`Com`](./Com.py) implémente plusieurs méthodes pour gérer la communication asynchrone :
- `broadcast(self, obj)`
- `sendTo(self, obj, dest: int)`

Deux nouvelles classes ont été créées pour l'implémentation des messages asynchrones : [`BroadcastMessage`](./BroadcastMessage.py) et [`MessageTo`](./MessageTo.py).
Cela permet de faire la distinction entre les broadcasts et messages dédiés synchrones et asynchrones, notamment pour les méthodes (avec annotation `@subscribe`) de réception des messages de ce type (`onBroadcast(self, msg: BroadcastMessage)` et `onReceive(self, m: MessageTo)`)

## Section critique et synchronisation
### Section critique
Pour accéder à la section critique, les communicateurs se transmettent des messages via le bus de type [`Token`](./Token.py). Deux méthodes sont disponibles (dans la classe [`Com`](./Com.py)) pour accéder à la SC : 
- `requestSC(self)` : Cette méthode met à jour la variable d'instance `self.etat` à _request_ et acquiert un verrou `self.scLock`.
- `releaseSC(self)` : Cette méthode relache le verrou `self.scLock` et change l'état à _release_.

Si un processus a le token, il peut alors accéder à la section critique (s'il le demande). Tout cela est implémenté dans la méthode de callback `onToken(self, token: Token)` de la classe `Com`.

### Synchronisation
La synchronisation des processus implémente la logique de **barrière de synchronisation**.

Une classe de message spécifique à la barrière de synchronisation a été créée : la classe [`Barrier`](./Barrier.py)

Les méthodes `synchronize(self)` et `onBarrier(self, msg: Barrier)` de la classe [`Com`](./Com.py) gèrent cette partie.

## Communication synchrone
La classe [`Com`](./Com.py) implémente plusieurs méthodes pour gérer la communication synchrone :
- `broadcastSync(self, obj, sender: int)`
- `sendToSync(self, obj, dest: int)`
- `recevFromSync(self, obj, sender: int)`

Deux nouvelles classes ont été créées pour l'implémentation des messages synchrones : [`BroadcastMessageSync`](./BroadcastMessage.py) et [`MessageToSync`](./MessageTo.py).
Cela permet de faire la distinction entre les broadcasts et messages dédiés synchrones et asynchrones, notamment pour les méthodes (avec annotation `@subscribe`) de réception des messages de ce type (`onBroadcastSync(self, msg: BroadcastMessageSync)` et `onMessageToSync(self, msg: MessageToSync)`)

## Numérotation automatique
Pour les besoins de la numérotation automatique, une classe [`Numerotation`](./Numerotation.py) a été créée pour détecter spécialement ce type de message interne.

Deux méthodes de la classe `Com` implémente la logique de la numérotation automatique :
- `numerotationAutomatique(self)` : Méthode qui implémente la logique de numérotation automatique. Elle remplace les ID provisoires (initialisés à 0) de chaque communicateur par un numéro tiré au sort.
- `onNumerotation(self, msg: Numerotation)` : Méthode de callback lorsqu'un message de type `Numerotation` circule sur le bus. Tous les processus ajoutent le `msg` dans leur boîte aux lettres.

Additionnellement, une méthode `init(self)` a été ajouté à la classe `Com`. Cette méthode est appelée par les [processus](./Process.py) (dans leur méthode `run(self)`) pour "initialiser" leurs communicateurs. Elle est chargée d'appeler la méthode de numérotation automatique.

## Résumé des classes et fichiers utilisés
- [`Com`](./Com.py) :
    - Communicateur du middleware, la classe contient toutes l'ensemble des méthodes de communication.
- [`Process`](./Process.py) :
    - Classe qui hérite de `Thread`, instancie et utilise un communicateur.
- [`Launcher`](./Launcher.py) :
    - Contient la méthode de lancement des threads `__main__`
- [`Message`](./Message.py) :
    - Classe de messages générique avec notamment une estampille et un message (payload).
- [`Mailbox`](./Mailbox.py) :
    - Classe qui représente la boîte aux lettres d'un communicateur. La boîte est représentée par un tableau `self.messages`.
    - Contient des méthodes de manipulation qui permettent entre autre de récupérer le premier message d'un certain type (méthode `getMsgOfType(self, type)`).
- [`BroadcastMessage`](./BroadcastMessage.py) :
    - Classe utilisée par `Com` pour envoyer des messages asynchrones en broadcast aux autres processus.
    - Hérite de la classe `Message`.
- [`BroadcastMessageSync`](./BroadcastMessage.py) :
    - Classe utilisée par `Com` pour envoyer des messages synchrones en broadcast aux autres processus.
    - Hérite de la classe `Message`.
- [`MessageTo`](./MessageTo.py) :
    - Classe utilisée par `Com` pour envoyer des messages dédiés asynchrones à un processus.
    - Utilise une variable `self.to` qui contient l'identifiant du processus destinataire.
    - Hérite de la classe `Message`.
- [`MessageToSync`](./MessageTo.py) :
    - Classe utilisée par `Com` pour envoyer des messages dédiés synchrones à un processus.
    - Hérite de la classe `MessageTo`.
- [`Token`](./Token.py) : 
    - Classe utilisée par `Com` pour accéder à la section critique.
    - Le token a une variable `self.to` pour simuler une topologie en anneau lorsqu'il est envoyé sur le bus.
- [`Barrier`](./Barrier.py) :
    - Les messages de type `Barrier` sont utilisés par le communicateur pour la barrière de synchronisation.
    - Hérite de la classe `Message`.
- [`Numerotation`](./Numerotation.py) :
    - Les messages de type `Numerotation` sont envoyés et reçus en broadcast.
    - Hérite de la classe `Message`.