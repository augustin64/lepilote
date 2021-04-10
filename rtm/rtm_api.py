from pathlib import Path
import os
import requests
import json
import time

null = None #simplify json responses
false = False
true = True

class BusLine():
    def __init__(self,name:str='',ID:str='',color='#000000') :
        self.color = color

        if name == '' and ID == '':
            raise Exception('you need to specify at least one argument')
        path = os.path.join(Path(__file__).parent, "data/lines.json")

        with open(path, 'r') as f:
            data=f.read()
        lines = json.loads(data)

        if name != '' and ID != '':
            self.ID = ID
            self.name = name

        elif name != '' :
            self.name = name
            if ID == '' :
                self.ID = lines[self.name]["ID"]

        elif ID != '' :
            self.ID = ID
            if name == '' :
                self.name = [ i for i in lines.keys() if lines[i]["ID"] == self.ID ][0]

        self.LNE = lines[self.name]['LNE']

    def __repr__(self):
        return(self.name)

    def get_routes(self):
        url = "https://api.rtm.fr/front/getRoutes/" + self.LNE
        content = eval(requests.get(url).text)['data']
        directions = []
        for i in content.keys():
            directions.append(Schedules.BusDirection(
                parent=self,
                name=content[i]['DirectionStations'],
                ID=content[i]['DirectionRef'],
                RefNETEX=content[i]['refNEtex']
                ))
        self.routes = directions
        return(directions)

class Schedules():
    def __init__(self):
        """Just a subclass"""
        None

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
                stops.append(Schedules.BusStop(parent=self,name=content[i]['Name'],ID=content[i]['sqlistationId']))

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
            self.schedules = [Schedules.Hour(data,parent=self) for data in content]
            return(self.schedules)

    class Hour():
        def __init__(self,data,parent=None):
            self.parent = parent
            self.AimedArrivalTime = data['AimedArrivalTime']
            self.AimedDepartureTime = data['AimedDepartureTime']
            self.FrequencyId = data['FrequencyId']
            self.IsCancelled = data['IsCancelled']
            self.LineId = data['LineId']
            self.Order = data['Order']
            self.PredictedArrivalTime = data['PredictedArrivalTime']
            self.PredictedDepartureTime = data['PredictedDepartureTime']
            self.RealArrivalTime = data['RealArrivalTime']
            self.RealDepartureTime = data['RealDepartureTime']
            self.RealTimeStatus = data['RealTimeStatus']
            self.Restriction = data['Restriction']
            self.StopId = data['StopId']
            self.TheoricArrivalTime = data['TheoricArrivalTime']
            self.TheoricDepartureTime = data['TheoricDepartureTime']
            self.VehicleJourneyId = data['VehicleJourneyId']

def get_alerts(period='Today',LNE=None):
    """
    period=today|coming|all
    LNE=bus/metro/tram id
    """
    if LNE == None :
        url = 'https://api.rtm.fr/front/getAlertes/FR/All'
        content = eval(requests.get(url).text)['data']
        AlertesToday = [Alert(data) for data in content['AlertesToday']]
        AlertesComing = [Alert(data) for data in content['AlertesComing']]
    else :
        url = 'https://api.rtm.fr/front/getAlertes/FR/' + LNE
        content = eval(requests.get(url).text)['data']
        AlertesToday = [Alert(data) for data in content['Alertes']]
        AlertesComing = []

    if period == 'today':
        return AlertesToday
    elif period == 'coming' :
        return AlertesComing
    else :
        return {'AlertesToday':AlertesToday, 'AlertesComing':AlertesComing}



class Alert():
    def __init__(self,data):
        self.ItemIdentifier = data['ItemIdentifier']
        self.InfoMessageIdentifier = data['InfoMessageIdentifier']
        self.InfoChannelRef = data['InfoChannelRef']
        self.ValidUntilTime = data['ValidUntilTime']
        self.title = data['MessageA']
        self.MessageB = data['MessageB']
        self.validite = data['MessageC']
        self.html = data['MessageD']
        self.type = data['type']
        self.AffectedLine = []
        for i in data ['AffectedLine'] :
            try :
                self.AffectedLine.append(BusLine(name=i['PublicCode'],color=i['color']))
            except Exception as e:
                print('cannot find',e)