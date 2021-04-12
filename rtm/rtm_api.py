from pathlib import Path
import os
import requests
import json
import time

null = None #simplify json responses
false = False
true = True

class Line():
    def __init__(self,data) :
        base_informations = ['name', 'id', 'Carrier', 'Operator', 'PublicCode', 'TypeOfLine', 'VehicleType', 'night', 'lepiloteId', 'color', 'sqliType']

        if 'id' in data.keys():
            self.id = data['id']
            self.lepiloteId = ''
            self.PublicCode = ''
        elif 'lepiloteId' in data.keys():
            self.id = ''
            self.lepiloteId = data['lepiloteId']
            self.PublicCode = ""
        elif 'PublicCode' in data.keys():
            self.id = ''
            self.lepiloteId = ''
            self.PublicCode = data['PublicCode']
        else :
            raise Exception('You must give id, lepiloteId or PublicCode to identify the line')

        if False in [False for i in base_informations if i not in data.keys()]:
            if 'sqliType' in data.keys():
                lines = get_lines(type=data['sqliType'])
            else :
                content = get_lines(type='all')
                lines = {}
                [lines.update(content[i]) for i in content.keys()]

            for i in lines.keys():
                if lines[i]['id'] == self.id or lines[i]['lepiloteId'] == self.lepiloteId or lines[i]['PublicCode'] == self.PublicCode :
                    self.name = lines[i]['name']
                    self.id = lines[i]['id']
                    self.Carrier = lines[i]['Carrier']
                    self.Operator = lines[i]['Operator']
                    self.PublicCode = lines[i]['PublicCode']
                    self.TypeOfLine = lines[i]['TypeOfLine']
                    self.VehicleType = lines[i]['VehicleType']
                    self.night = lines[i]['night']
                    self.lepiloteId = lines[i]['lepiloteId']
                    self.color = lines[i]['color']
                    self.sqliType = lines[i]['sqliType']
                    break

        else :
            self.name = data['name']
            self.id = data['id']
            self.Carrier = data['Carrier']
            self.Operator = data['Operator']
            self.PublicCode = data['PublicCode']
            self.TypeOfLine = data['TypeOfLine']
            self.VehicleType = data['VehicleType']
            self.night = data['night']
            self.lepiloteId = data['lepiloteId']
            self.color = data['color']
            self.sqliType = data['sqliType']


    def get_routes(self):
        url = "https://api.rtm.fr/front/getRoutes/" + self.id
        content = eval(requests.get(url).text)['data']
        directions = []
        for i in content.keys():
            directions.append(Schedules.Direction(content[i],parent=self))
        self.routes = directions
        return(directions)

class Schedules():
    def __init__(self):
        """Just a subclass"""
        None

    class Direction() :
        def __init__(self,data,parent=None):
            self.parent=parent
            if self.parent.id != None:
                self.lineRef = self.parent.id
            elif data['lineRef'] != None :
                self.lineRef = data['lineRef']
            else :
                self.lineRef = Line(data).id

            if self.parent == None and 'lineRef' not in data and 'sqlilineNumber' not in data :
                raise Exception('You must specify at least parent, lineRef or sqlilinenumber')

            base_informations = ['id', 'refNEtex', 'sqlistationId', 'sqlilineNumber', 'pointId', 'lineId', 'sqliOrdering', 'DirectionRef', 'Direction', 'operator', 'lineRef', 'DirectionStations', 'DirectionStationsSqli']

            if False in [False for i in base_informations if i not in data.keys()]:
                if 'id' in data :
                    self.id = data['id']
                    self.refNEtex = ''
                    self.sqlistationId = ''
                    self.DirectionRef = ''
                    self.Direction = ''
                    self.DirectionStations = ''

                elif 'refNEtex' in data:
                    self.refNEtex = data['refNEtex']
                    self.id = ''
                    self.sqlistationId = ''
                    self.DirectionRef = ''
                    self.Direction = ''
                    self.DirectionStations = ''

                elif 'sqlistationId' in data:
                    self.sqlistationId = data['sqlistationId']
                    self.id = ''
                    self.refNEtex = ''
                    self.DirectionRef = ''
                    self.Direction = ''
                    self.DirectionStations = ''

                elif 'DirectionRef' in data:
                    self.DirectionRef = data['DirectionRef']
                    self.id = ''
                    self.refNEtex = ''
                    self.sqlistationId = ''
                    self.Direction = ''
                    self.DirectionStations = ''

                elif 'Direction' in data:
                    self.Direction = data['Direction']
                    self.id = ''
                    self.refNEtex = ''
                    self.sqlistationId = ''
                    self.DirectionRef = ''
                    self.DirectionStations = ''

                elif 'DirectionStations' in data:
                    self.DirectionStations = data['DirectionStations']
                    self.id = ''
                    self.refNEtex = ''
                    self.sqlistationId = ''
                    self.DirectionRef = ''
                    self.Direction = ''

                else :
                    raise Exception('You must specify at least one information')

                r = eval(requests.get('https://api.rtm.fr/front/getRoutes/'+self.lineRef).text)['data']

                for i in r.keys():

                    if r[i]['id']==self.id or r[i]['refNEtex']==self.refNEtex or r[i]['sqlistationId']==self.sqlistationId or r[i]['DirectionStations']==self.DirectionStations or r[i]['DirectionRef']==self.DirectionRef or r[i]['Direction']==self.Direction :
                        self.id = r[i]['id']
                        self.refNEtex = r[i]['refNEtex']
                        self.sqlistationId = r[i]['sqlistationId']
                        self.sqlilineNumber = r[i]['sqlilineNumber']
                        self.pointId = r[i]['pointId']
                        self.lineId = r[i]['lineId']
                        self.sqliOrdering = r[i]['sqliOrdering']
                        self.DirectionRef = r[i]['DirectionRef']
                        self.Direction = r[i]['Direction']
                        self.operator = r[i]['operator']
                        self.lineRef = r[i]['lineRef']
                        self.DirectionStations = r[i]['DirectionStations']
                        self.DirectionStationsSqli = r[i]['DirectionStationsSqli']
                        break
            
            else :
                self.id = data['id']
                self.refNEtex = data['refNEtex']
                self.sqlistationId = data['sqlistationId']
                self.sqlilineNumber = data['sqlilineNumber']
                self.pointId = data['pointId']
                self.lineId = data['lineId']
                self.sqliOrdering = data['sqliOrdering']
                self.DirectionRef = data['DirectionRef']
                self.Direction = data['Direction']
                self.operator = data['operator']
                self.lineRef = data['lineRef']
                self.DirectionStations = data['DirectionStations']
                self.DirectionStationsSqli = data['DirectionStationsSqli']

        def __repr__(self):
            return(json.dumps({'ID':self.lineRef,'Name':self.DirectionStations,'parent':str(self.parent)},indent=4))

        def get_stops(self):
            url = 'https://api.rtm.fr/front/getStations/' + self.refNEtex
            content = eval(requests.get(url).text)['data']
            stops = []

            for i in content :
                stops.append(Schedules.Stop(i,parent=self))

            self.stops = stops
            return(stops)

    class Stop():
        def __init__(self,data,parent=None):
            self.Description = data['Description']
            self.Name = data['Name']
            self.sqlistationId=data['sqlistationId']
            self.parent=parent

        def __repr__(self):
            return(self.Name)

        def get_schedule(self,date=time.strftime("%Y-%m-%d", time.gmtime())):     #Ask for the next bus if no time specified
            url = "https://api.rtm.fr/front/lepilote/GetStopHours/json"                 #Time format must be yyyy-MM-dd or yyyy-MM-dd_HH-mm
            url += "?StopIds=" + self.sqlistationId
            url += "&DateTime=" + date
            url += "&LineId=" + self.parent.parent.lepiloteId
            url += "&Direction=" + self.parent.DirectionRef
            r = requests.get(url)
            content = eval(r.text)['Data']['Hours']
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

def get_lines(type='all'):
    """
    type=all|bus|metro|tram
    """
    if type == 'all':
        content = {
            "bus":eval(requests.get('https://api.rtm.fr/front/getLines/bus').text)['data'],
            "metro":eval(requests.get('https://api.rtm.fr/front/getLines/metro').text)['data'],
            "tram":eval(requests.get('https://api.rtm.fr/front/getLines/tram').text)['data']
        }

    else :
        content = eval(requests.get('https://api.rtm.fr/front/getLines/'+type).text)['data']

    return content




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
                self.AffectedLine.append(Line({'PublicCode':i['PublicCode']}))
            except Exception as e:
                print('cannot find',e)