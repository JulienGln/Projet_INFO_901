# Projet_INFO_901
## Réalisation d’un intergiciel (middleware) dans le cadre du module INFO 901 - Algorithmes distribués
### GALERNE Julien

# Lancement du projet
Le programme principal se trouve dans le fichier [`Launcher.py`](./Launcher.py). Il utilise les threads des processus de la classe `Process` du fichier [`Process.py`](./Process.py).

Le programme se lance avec la commande suivante :
>```$ python3 Launcher.py```

Le projet n'utilise pas de bibliothèques tierces hors celles incluses dans le langage de base (`threading`, `time`, etc.) et hormis la bibliothèque `pyeventbus3`.
>```$ pip install pyeventbus3```

# Explication des classes
## Communication asynchrone
La classe [`Com`](./Com.py) implémente plusieurs méthodes pour gérer la communication asynchrone :
- `broadcast(self, obj)`
- `sendTo(self, obj, dest: int)`

Deux nouvelles classes ont été créées pour l'implémentation des messages asynchrones : [`BroadcastMessage`](./BroadcastMessage.py) et [`MessageTo`](./MessageTo.py).
Cela permet de faire la distinction entre les broadcasts et messages dédiés synchrones et asynchrones, notamment pour les méthodes (avec annotation `@subscribe`) de réception des messages de ce type (`onBroadcast(self, msg: BroadcastMessage)` et `onReceive(self, m: MessageTo)`)

## Section critique et synchronisation
### Section critique

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