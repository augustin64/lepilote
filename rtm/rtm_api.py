from pathlib import Path
import os
import requests
import json

class BusLign():
    def __init__(self,name: str='',id: str='') :
        
        if name == '' and id == '':
            raise Exception('you need to specify at least one argument')
        path = os.path.join(Path(__file__).parent, "data/lignes.json")

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

    def __repr__(self):
        return(self.name)

    def get_routes(self):
        url = "https://api.rtm.fr/front/getRoutes/" + self.LNE
        content = eval(requests.get(url).text)['data']
        directions = []
        for i in content.keys():
            directions.append(BusDirection(
                parent=self,
                name=content[i]['DirectionStations'],
                ID=content[i]['DirectionRef'],
                RefNETEX=content[i]['refNEtex']
                ))
        self.routes = directions
        return(directions)


class BusDirection() :
    def __init__(self,parent=None,name='',ID='0',RefNETEX=''):
        self.ID=ID
        self.name=name
        self.parent=parent
        self.RefNETEX=RefNETEX
    
    def __repr__(self):
        return(json.dumps({'ID':self.ID,'Name':self.name,'parent':str(self.parent)},indent=4))
        
