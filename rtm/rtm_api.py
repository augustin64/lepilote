from pathlib import Path
import os
import requests
import json

class BusLign():
    def __init__(self,name: str='',id: str='') :
        if name == '' and id == '':
            raise Exception('you need to specify at least one argument')

        path = os.path.join(Path(__file__).parent, "data/lignes.json")
        print(path)
        with open(path, 'r') as f:
            data=f.read()

        lignes = json.loads(data)

        if name != '' :
            self.name = name
            if id == '' :
                self.id = lignes[self.name]["ID"]

        elif id != '' :
            self.id = id
            if name == '' :
                self.name = [ i for i in lignes.keys() if lignes[i]["ID"] == self.id ][0]

        self.LNE = lignes[self.name]['LNE']

    def get_routes(self):
        url = "https://api.rtm.fr/front/getRoutes/" + self.LNE
        content = eval(requests.get(url).text)['data']