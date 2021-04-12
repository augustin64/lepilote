# rtm-api-marseille
API Python non officielle pour suivre les transports en commun Marseillais [Régie des Transports Métropolitains]

Installation :
```
git clone https://github.com/augustin64/rtm-api-marseille.git
```

Utilisation :
```py
import rtm
bus_line=rtm.Line({'PublicCode':'7'})           # L'attribut 'PublicCode' correspond à l'identifiant public (nom commun) de la ligne
bus_line.get_routes()                           # On utilise la fonction get_routes() de la classe Line() pour mettre à jour les directions
direction1 = bus_line.routes[0]                 # On retrouve les directions dans la liste routes d'un élément de la classe Line()
direction1.get_stops()                          # On charge la liste des arrêts de bus correspondant à cette direction
stop4 = direction1.stops[3]                     # On récupère le 4ème arrêt de la ligne
stop4.get_schedule()                            # On récupère la liste des prochains bus passant à cet arrêt
```
