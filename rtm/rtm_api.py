from pathlib import Path
import os
import requests
import json

class BusLign():
    def __init__(self,name='',id='') :
        if name == '' and id == '':
            raise Exception('you need to specify at least one argument')

        path = os.path.join(Path(__file__).parent, "data/lignes_de_bus.json")
        print(path)
        with open(path, 'r') as f:
            data=f.read()

        lignes_de_bus = json.loads(data)

        if name != '' :
            self.name = name
            if id == '' :
                self.id = lignes_de_bus[str(name)]

        elif id != '' :
            self.id = id
            if name == '' :
                self.name = [ i for i in lignes_de_bus.keys() if lignes_de_bus[str(i)] == str(id) ][0]

    def get_routes(self):
        None

