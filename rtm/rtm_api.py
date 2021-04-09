from pathlib import Path
import os
import requests
import json
import time

null = None #simplify json responses
false = False
true = True

class BusLign():
    def __init__(self,name:str='',ID:str='') :
        
        if name == '' and ID == '':
            raise Exception('you need to specify at least one argument')
        path = os.path.join(Path(__file__).parent, "data/lignes.json")

        with open(path, 'r') as f:
            data=f.read()
        lignes = json.loads(data)

        if name != '' :
            self.name = name
            if ID == '' :
                self.ID = lignes[self.name]["ID"]

        elif ID != '' :
            self.ID = ID
            if name == '' :
                self.name = [ i for i in lignes.keys() if lignes[i]["ID"] == self.ID ][0]

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
    def __init__(self,parent=None,name:str='',ID:str='0',RefNETEX:str=''):
        self.ID=ID
        self.name=name
        self.parent=parent
        self.RefNETEX=RefNETEX
    
    def __repr__(self):
        return(json.dumps({'ID':self.ID,'Name':self.name,'parent':str(self.parent)},indent=4))

    def get_stops(self):
        url = 'https://api.rtm.fr/front/getStations/' + self.RefNETEX
        content = eval(requests.get(url).text)['data']
        stops = []

        for i in range(len(content)) :
            stops.append(BusStop(parent=self,name=content[i]['Name'],ID=content[i]['sqlistationId']))

        self.stops = stops
        return(stops)

class BusStop():
    def __init__(self,parent=None,name:str='',ID:str='0'):
        self.name=name
        self.ID=ID
        self.parent=parent

    def __repr__(self):
        return(self.name)

    def get_schedule(self,date=time.strftime("%Y-%m-%d_%H-%M", time.gmtime())):     #Ask for the next bus if no time specified
        url = "https://api.rtm.fr/front/lepilote/GetStopHours/json"                 #Time format must be yyyy-MM-dd or yyyy-MM-dd_HH-mm
        url += "?StopIds=" + self.ID
        url += "&DateTime=" + date
        url += "&LineId=" + self.parent.parent.ID
        url += "&Direction=" + self.parent.ID
        content = eval(requests.get(url).text)['Data']['Hours']
        print(json.dumps(content))
