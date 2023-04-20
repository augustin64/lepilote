# lepilote API
Client Python de l'API de la RTM (Régie des Transports Métropolitains des Bouches du Rhône)

## Installation :
```
git clone https://github.com/augustin64/lepilote.git
```

## Exemples d'utilisation

#### Récupérer les horaires de bus/métro/tram sur une ligne
```python
import rtm
bus_line=rtm.Line({'PublicCode':'7'})     # L'attribut 'PublicCode' correspond à l'identifiant public de la ligne
bus_line.get_routes()                     # La fonction `get_routes()` charge les directions possibles
direction1 = bus_line.routes[0]           # On retrouve les directions dans la liste `routes` de la ligne (`Line()`) créé précédemment
direction1.get_stops()                    # La fonction `get_stops()` charge les arrêts de bus/métro/tram correspondant à la direction choisie
stop4 = direction1.stops[3]               # On récupère le 4ème arrêt de la ligne
schedules = stop4.get_realtime_schedule() # On récupère la liste des prochains bus passant à cet arrêt en temps réel
if len(schedules) == 0:
    schedules = stop4.get_theoric_schedule()
```

#### Récupérer les alertes concernant le traffic
```python
alerts_today = rtm.get_alerts(period='today')
alert1 = alerts_today[0]
alert1.html               # Renvoie le message d'erreur au format html
alert1.AffectedLine       # Renvoie la liste des lignes et réseaux affectés, certains n'ont pas encore été implémentés
```


## FAQ

Y'a t-il une API et une documentation "officielles" servant de référence ?
> Pas à ma connaissance, n'hésitez pas à me contacter si vous en trouvez une

D'où viennent les endpoints utilisés ici ?
> De https://www.rtm.fr/horaires, l'API n'est pas publique mais les requêtes faites par le site sont assez claires

Y'a t-il d'autres endpoints non référencés ici ?
> Sûrement, je n'ai implémenté que ceux qui me sont utiles. J'ai regardé les requêtes du site et de l'application mobile sans trouver non plus beaucoup plus que cela
