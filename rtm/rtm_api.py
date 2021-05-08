import requests
import json
import time

null = None #simplify json responses
false = False
true = True

class Line():
    def __init__(self,data) :
        base_informations = ['name', 'id', 'Carrier', 'Operator', 'PublicCode', 'TypeOfLine', 'VehicleType', 'night', 'lepiloteId', 'color', 'sqliType']
        self.id = ''
        self.lepiloteId = ''
        self.PublicCode = ''
        if 'id' in data.keys():
            self.id = data['id']
        elif 'lepiloteId' in data.keys():
            self.lepiloteId = data['lepiloteId']
        elif 'PublicCode' in data.keys():
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
                self.id = ''
                self.refNEtex = ''
                self.sqlistationId = ''
                self.DirectionRef = ''
                self.Direction = ''
                self.DirectionStations = ''

                if 'id' in data :
                    self.id = data['id']
                elif 'refNEtex' in data:
                    self.refNEtex = data['refNEtex']
                elif 'sqlistationId' in data:
                    self.sqlistationId = data['sqlistationId']
                elif 'DirectionRef' in data:
                    self.DirectionRef = data['DirectionRef']
                elif 'Direction' in data:
                    self.Direction = data['Direction']
                elif 'DirectionStations' in data:
                    self.DirectionStations = data['DirectionStations']

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
                stops.append(Schedules.Stop(i,self))
            self.stops = stops
            return(stops)

    class Stop():
        def __init__(self,data,parent):
            self.parent = parent
            base_informations = ['id', 'refNEtex', 'sqlistationId', 'sqlilineNumber', 'pointId', 'lineId', 'operator', 'lineRef', 'Name', 'Description', 'StopRef', 'type', 'postCode', 'Longitude', 'Latitude', 'sqliLepiloteId', 'pmr', 'code3l', 'PdfNameHoraire']
            if False in [False for i in base_informations if i not in data.keys()]:
                self.id = ''
                self.refNEtex = ''
                self.sqlistationId = ''
                self.pointId = ''
                self.Name = ''
                self.StopRef = ''
                self.Longitude = None
                self.Latitude = None
                self.sqliLepiloteId = ''

                if 'id' in data.keys() :
                    self.id = data['id']
                elif 'refNEtex' in data.keys():         # Un seul des identifiants est nécessaire pour
                    self.refNEtex = data['refNEtex']    # Identifier l'arrêt, donc on n'en acceptera qu'un
                elif 'sqlistationId' in data.keys():    # seul dans des soucis d'optimisation
                    self.sqlistationId = data['sqlistationId']
                elif 'pointId' in data.keys():
                    self.pointId = data['pointId']
                elif 'Name' in data.keys():
                    self.Name = data['Name']
                elif 'StopRef' in data.keys():
                    self.StopRef = data['StopRef']
                elif 'sqliLepiloteId' in data.keys():
                    self.sqliLepiloteId = data['sqliLepiloteId']
                elif 'Longitude' in data.keys() and 'Latitude' in data.keys():
                    self.Longitude = data['Longitude']
                    self.Latitude = data['Latitude']

                url = 'https://api.rtm.fr/front/getStations/' + self.parent.refNEtex
                content = eval(requests.get(url).text)['data']

                for i in content :
                    if (
                        i['id'] == self.id or
                        i['refNEtex'] == self.refNEtex or
                        i['sqlistationId'] == self.sqlistationId or
                        i['pointId'] == self.pointId or
                        i['Name'] == self.Name or
                        i['StopRef'] == self.StopRef or
                        i['sqliLepiloteId'] == self.sqliLepiloteId or
                        (i['Longitude'] == self.Longitude and i['Latitude'] == self.Latitude and self.Latitude != '')) :
                        
                        self.id = i['id']
                        self.refNEtex = i['refNEtex']
                        self.sqlistationId = i['sqlistationId']
                        self.sqlilineNumber = i['sqlilineNumber']
                        self.pointId = i['pointId']
                        self.lineId = i['lineId']
                        self.operator = i['operator']
                        self.lineRef = i['lineRef']
                        self.Name = i['Name']
                        self.Description = i['Description']
                        self.StopRef = i['StopRef']
                        self.type = i['type']
                        self.postCode = i['postCode']
                        self.Longitude = i['Longitude']
                        self.Latitude = i['Latitude']
                        self.sqliLepiloteId = i['sqliLepiloteId']
                        self.pmr = i['pmr']
                        self.code3l = i['code3l']
                        self.PdfNameHoraire = i['PdfNameHoraire']
                        break
                
            else :
                self.id = data['id']
                self.refNEtex = data['refNEtex']
                self.sqlistationId = data['sqlistationId']
                self.sqlilineNumber = data['sqlilineNumber']
                self.pointId = data['pointId']
                self.lineId = data['lineId']
                self.operator = data['operator']
                self.lineRef = data['lineRef']
                self.Name = data['Name']
                self.Description = data['Description']
                self.StopRef = data['StopRef']
                self.type = data['type']
                self.postCode = data['postCode']
                self.Longitude = data['Longitude']
                self.Latitude = data['Latitude']
                self.sqliLepiloteId = data['sqliLepiloteId']
                self.pmr = data['pmr']
                self.code3l = data['code3l']
                self.PdfNameHoraire = data['PdfNameHoraire']

        def __repr__(self):
            return(self.Name)

        def get_schedule(self,date=time.strftime("%Y-%m-%d", time.gmtime())):     #Ask for the next bus if no time specified
            url = "https://api.rtm.fr/front/lepilote/GetStopHours/json"                 #Time format must be yyyy-MM-dd or yyyy-MM-dd_HH-mm
            url += "?StopIds=" + self.sqlistationId
            url += "&DateTime=" + date
            url += "&LineId=" + self.parent.parent.lepiloteId
            url += "&Direction=" + self.parent.DirectionRef
            r = requests.get(url)
            data = eval(r.text)['Data']
            if str(type(data)) == "<class 'dict'>" :
                hours = data['Hours']
                self.schedules = [Schedules.Hour(dt,parent=self) for dt in hours]
            else :
                self.schedules = []
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
        if 'AlertesComing' in content :
            AlertesComing = [Alert(data) for data in content['AlertesComing']]
        else :
            AlertesComing = []
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