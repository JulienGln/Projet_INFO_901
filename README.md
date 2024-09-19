# Projet_INFO_901
Réalisation d’un intergiciel (middleware) dans le cadre du module INFO 901 - Algorithmes distribués

## Communication asynchrone

## Section critique et synchronisation

## Communication synchrone
La classe `Com` implémente plusieurs méthodes pour gérer la communication synchrone :
- `broadcastSync(self, obj, sender: int)`
- `sendToSync(self, obj, dest: int)`
- `recevFromSync(self, obj, sender: int)`

Deux nouvelles classes ont été créées pour l'implémentation des messages synchrones : `BroadcastMessageSync` et `MessageToSync`.
Cela permet de faire la distinction entre les broadcasts et messages dédiés synchrones et asynchrones, notamment pour les méthodes (avec annotation `@subscribe`) de réception des messages de ce type (`onBroadcastSync(self, msg: BroadcastMessageSync)` et `onMessageToSync(self, msg: MessageToSync)`)