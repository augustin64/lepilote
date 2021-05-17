# rtm-api-marseille
API Python non officielle pour suivre les transports en commun Marseillais [Régie des Transports Métropolitains]

## Installation :
```
git clone https://github.com/augustin64/rtm-api-marseille.git
```

## Utilisation :
```py
import rtm
bus_line=rtm.Line({'PublicCode':'7'})           # L'attribut 'PublicCode' correspond à l'identifiant public (nom commun) de la ligne
bus_line.get_routes()                           # On utilise la fonction get_routes() de la classe Line() pour mettre à jour les directions
direction1 = bus_line.routes[0]                 # On retrouve les directions dans la liste routes d'un élément de la classe Line()
direction1.get_stops()                          # On charge la liste des arrêts de bus correspondant à cette direction
stop4 = direction1.stops[3]                     # On récupère le 4ème arrêt de la ligne
stop4.get_schedule()                            # On récupère la liste des prochains bus passant à cet arrêt

alerts_today = rtm.get_alerts(period='today')
alert1 = alerts_today[0]
alert1.html					# Renvoie le message d'erreur sous un format html
alert1.AffectedLine				# Renvoie la liste des lignes et réseaux affectés, certains n'ont pas encore été implémentés
						# et renvoient donc une erreur
```

### Optimisations et Améliorations possibles :
* la fonction `get_alerts()` met beaucoup de temps à s'exécuter car nécessite de recréer tous les objets correspondant aux lignes de bus, les informations contenues dans les résultats de la requete contenant les alertes n'étant que partielles, il faudrait donc la réecrire de manière à ne créer les lignes uniquement lorsqu'elles sont explicitement demandées.

* ajouter le support concernant les lignes CG13, mieux optimiser la partie métro et tram, ce module python étant pour l'instant concentré sur les lignes de bus

### [WIP]
* Ajout des horaires en temps réel (l'API utilisée jusqu'alors ne renvoyant plus que les horaires théoriques)
