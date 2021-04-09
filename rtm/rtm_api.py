import requests
import json

class BusLign():
    def __init__(self,name='',id='') :
        if name == '' and id == '':
            raise Exception('you need to specify at least one argument')
        
        with open('data/lignes_de_bus.json', 'r') as f:
            data=f.read()

        lignes_de_bus = json.loads(data)

        if name != '' :
            self.name = name
            if id == '' :
                self.id = [ i for i in lignes_de_bus.keys() if lignes_de_bus[str(i)] == name ][0]

        elif id != '' :
            self.id = id
            if name == '' :
                self.name = lignes_de_bus[str(id)]

    def get_routes(self):
        None

