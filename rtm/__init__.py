import json
import time
from typing import List, Dict, Set
from xml.etree import ElementTree
from functools import cache

import requests

__version__ = (1, 0, 43)

# Setting custom headers
headers = {'User-Agent': 'RTM API Python Client', 'From': 'https://github.com/augustin64/lepilote'}

# Max consecutive requests
MAX_REQUESTS: int = 3


class GatewayTimeoutError(Exception):
    """
    Exception raised in case of a 504 Gateway Timeout response.
    """
    pass


class Line:
    BASE_INFORMATION: Set[str] = {
        'name',
        'id',
        'Carrier',
        'Operator',
        'PublicCode',
        'TypeOfLine',
        'VehicleType',
        'night',
        'lepiloteId',
        'color',
        'sqliType',
    }

    def __init__(self, data: Dict):
        self.routes = None
        self.id = data.get('id', '')
        self.lepiloteId = data.get('lepiloteId', '')
        self.PublicCode = data.get('PublicCode', '')
        if not any((self.id, self.lepiloteId, self.PublicCode)):
            raise ValueError(
                'You must give id, lepiloteId or PublicCode to identify the line'
            )

        if not all(k in data for k in self.BASE_INFORMATION):
            # We don't have all the base information needed: let's retrieve it!
            # First, let's get the lines information
            lines_dict = (
                get_lines(data['sqliType'])
                if 'sqliType' in data
                else get_lines("all")
            )
            # Then we "flatten" the lines dictionary
            lines_dict = {
                line_id: line_info
                for lines_list in lines_dict.values()
                for line_id, line_info in lines_list.items()
            }

            for line_id in lines_dict:
                if (
                    lines_dict[line_id]['id'] == self.id
                    or lines_dict[line_id]['lepiloteId'] == self.lepiloteId
                    or lines_dict[line_id]['PublicCode'] == self.PublicCode
                ):
                    # That's the line we're looking for, let's set the attributes
                    data = lines_dict[line_id]
                    break
            else:
                raise Exception(
                    f"We could not get the line we were looking for! | "
                    f"RTM ID: '{self.id if self.id else 'None'}' / "
                    f"lepilote ID: '{self.lepiloteId if self.lepiloteId else 'None'}' / "
                    f"public code: '{self.PublicCode if self.PublicCode else 'None'}'"
                )

        # At that point, we have all the information needed
        self._set_attributes(data)

    @classmethod
    def from_public_code(cls, public_code: str):
        return cls(data={'PublicCode': public_code})

    @classmethod
    def from_lepilote_id(cls, lepilote_id: str):
        return cls(data={'lepiloteId': lepilote_id})

    @classmethod
    def from_rtm_id(cls, rtm_id: str):
        return cls(data={'id': rtm_id})

    def _set_attributes(self, data: Dict):
        """
        Helper function to set the attributes of the `Line` object

        @param data: The line data, as a dict
        """
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

    def get_routes(self, refresh_list: bool = True) -> List['Schedules.Direction']:
        if self.routes is None or refresh_list:
            url = "https://api.rtm.fr/front/getRoutes/" + self.id
            content: Dict = json.loads(requests.get(url, headers=headers).text)['data']
            self.routes = [
                Schedules.Direction(_dir, parent=self) for _dir in content.values()
            ]
        return self.routes


class Schedules:
    def __init__(self):
        """Just a superclass"""
        pass

    class Direction:
        BASE_INFORMATION: Set[str] = {
            'id',
            'refNEtex',
            'sqlistationId',
            'sqlilineNumber',
            'pointId',
            'lineId',
            'sqliOrdering',
            'DirectionRef',
            'Direction',
            'operator',
            'lineRef',
            'DirectionStations',
            'DirectionStationsSqli',
        }

        def __init__(self, data: Dict, parent=None):
            self.parent = parent
            self.stops = None
            if self.parent is not None and self.parent.id is not None:
                self.lineRef = self.parent.id
            elif 'lineRef' in data and data['lineRef'] is not None:
                self.lineRef = data['lineRef']
            else:
                self.lineRef = Line(data).id

            if self.lineRef is None:
                raise ValueError(
                    'You must specify at least the parent or lineRef'
                )

            if not all(k in data for k in self.BASE_INFORMATION):
                # We don't have all the base information needed: let's retrieve it!
                # First, let's get the lines information
                self.id = data.get('id', '')
                self.refNEtex = data.get('refNEtex', '')
                self.sqlistationId = data.get('sqlistationId', '')
                self.DirectionRef = data.get('DirectionRef', '')
                self.Direction = data.get('Direction', '')
                self.DirectionStations = data.get('DirectionStations', '')
                if not any(
                    (
                        self.id,
                        self.refNEtex,
                        self.sqlistationId,
                        self.DirectionRef,
                        self.Direction,
                        self.DirectionStations,
                    )
                ):
                    raise ValueError('You must specify at least one information')

                r: Dict = json.loads(
                    requests.get(
                        'https://api.rtm.fr/front/getRoutes/' + self.lineRef,
                        headers=headers
                    ).text
                )['data']

                for route in r.values():
                    if (
                        route['id'] == self.id
                        or route['refNEtex'] == self.refNEtex
                        or route['sqlistationId'] == self.sqlistationId
                        or route['DirectionStations'] == self.DirectionStations
                        or route['DirectionRef'] == self.DirectionRef
                        or route['Direction'] == self.Direction
                    ):
                        data: Dict = route
                        break
                else:
                    raise Exception(
                        f"We could not get the route/direction we were looking for! | "
                        f"RTM ID: '{self.id if self.id else 'None'}' / "
                        f"refNEtex: '{self.refNEtex if self.refNEtex else 'None'}' / "
                        f"sqlistationId: '{self.sqlistationId if self.sqlistationId else 'None'}' / "
                        f"DirectionStations: '{self.DirectionStations if self.DirectionStations else 'None'}' / "
                        f"DirectionRef: '{self.DirectionRef if self.DirectionRef else 'None'}' / "
                        f"Direction: '{self.Direction if self.Direction else 'None'}'"
                    )

            # At that point, we have all the information needed
            self._set_attributes(data)

        def __repr__(self):
            return json.dumps(
                {
                    'ID': self.lineRef,
                    'Name': self.DirectionStations,
                    'parent': str(self.parent)
                },
                indent=4
            )

        def _set_attributes(self, data: Dict):
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

        def get_stops(self, refresh_list: bool = True) -> List['Schedules.Stop']:
            if self.stops is None or refresh_list:
                url = 'https://api.rtm.fr/front/getStations/' + self.refNEtex
                content: List = json.loads(requests.get(url, headers=headers).text)['data']
                self.stops = [Schedules.Stop(stop, self) for stop in content]
            return self.stops

    class Stop:
        BASE_INFORMATION: Set[str] = {
            'id',
            'refNEtex',
            'sqlistationId',
            'sqlilineNumber',
            'pointId',
            'lineId',
            'operator',
            'lineRef',
            'Name',
            'Description',
            'StopRef',
            'type',
            'postCode',
            'Longitude',
            'Latitude',
            'sqliLepiloteId',
            'pmr',
            'code3l',
            'PdfNameHoraire',
        }

        def __init__(self, data: Dict, parent):
            self.parent = parent
            self.schedules = None
            if not all(k in data for k in self.BASE_INFORMATION):
                self.id = data.get('id', '')
                self.refNEtex = data.get('refNEtex', '')
                self.sqlistationId = data.get('sqlistationId', '')
                self.pointId = data.get('pointId', '')
                self.Name = data.get('Name', '')
                self.StopRef = data.get('StopRef', '')
                self.Longitude = data.get('Longitude', '')
                self.Latitude = data.get('Latitude', '')
                self.sqliLepiloteId = data.get('sqliLepiloteId', '')

                url = 'https://api.rtm.fr/front/getStations/' + self.parent.refNEtex
                content = json.loads(requests.get(url, headers=headers).text)['data']

                for stop in content:
                    if (
                        stop['id'] == self.id
                        or stop['refNEtex'] == self.refNEtex
                        or stop['sqlistationId'] == self.sqlistationId
                        or stop['pointId'] == self.pointId
                        or stop['Name'] == self.Name
                        or stop['StopRef'] == self.StopRef
                        or stop['sqliLepiloteId'] == self.sqliLepiloteId
                        or (
                            stop['Longitude'] == self.Longitude
                            and stop['Latitude'] == self.Latitude
                        )
                    ):
                        data = stop
                        break
                else:
                    raise Exception(
                        f"We could not get the stop we were looking for! | "
                        f"RTM ID: '{self.id if self.id else 'None'}' / "
                        f"refNEtex: '{self.refNEtex if self.refNEtex else 'None'}' / "
                        f"sqlistationId: '{self.sqlistationId if self.sqlistationId else 'None'}' / "
                        f"pointId: '{self.pointId if self.pointId else 'None'}' / "
                        f"Name: '{self.Name if self.Name else 'None'}' / "
                        f"StopRef: '{self.StopRef if self.StopRef else 'None'}' / "
                        f"sqliLepiloteId: '{self.sqliLepiloteId if self.sqliLepiloteId else 'None'}' / "
                        f"Longitude: '{self.Longitude if self.Longitude else 'None'}' / "
                        f"Latitude: '{self.Latitude if self.Latitude else 'None'}' / "
                    )
            # We have all the info needed
            self._set_attributes(data)

        def __repr__(self):
            return self.Name

        def _set_attributes(self, data: Dict):
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

        def get_theoric_schedule(
            self, date=time.strftime("%Y-%m-%d", time.gmtime())
        ):
            # Ask for the next bus if no time specified
            # Time format must be yyyy-MM-dd or yyyy-MM-dd_HH-mm
            url = "https://api.rtm.fr/front/lepilote/GetStopHours/json"
            url += "?StopIds=" + self.sqlistationId
            url += "&DateTime=" + date
            url += "&LineId=" + self.parent.parent.lepiloteId
            url += "&Direction=" + self.parent.DirectionRef
            r = requests.get(url, headers=headers)
            data = json.loads(r.text)['Data']
            if isinstance(data, dict):
                hours = data['Hours']
                self.schedules = [Schedules.Hour(dt, parent=self) for dt in hours]
            else:
                self.schedules = []

            return self.schedules

        def get_realtime_schedule(
            self, date=time.strftime("%Y-%m-%d", time.gmtime())
        ):
            assert (
                MAX_REQUESTS > 0
            ), f"MAX_REQUESTS must be at least 1 (current value: {MAX_REQUESTS})"
            for i in range(MAX_REQUESTS):
                # On effectue jusqu'à `MAX_REQUESTS` requêtes,
                # avant de renvoyer à notre tour une réponse invalide
                url = (
                    "https://api.rtm.fr/front/spoti/getStationDetails?nomPtReseau="
                    + self.refNEtex[-5:]
                )
                response = requests.get(url)
                value = response.text
                if '504 Gateway Time-out' not in value:
                    break
            else:
                # Nombre maximum de requêtes consécutives atteint
                raise GatewayTimeoutError(f"We got {MAX_REQUESTS} consecutive invalid responses")

            tree = ElementTree.fromstring(response.content)

            schedule_list = []

            for i in tree:
                if len(i) == 4:
                    t = time.strptime(i[1].text, "%H:%M")
                    element = {
                        'AimedArrivalTime': None,
                        'AimedDepartureTime': None,
                        'FrequencyId': None,
                        'IsCancelled': False,
                        'LineId': self.parent.id,
                        'Order': 1,
                        'PredictedArrivalTime': None,
                        'PredictedDepartureTime': None,
                        'RealArrivalTime': None,
                        'RealDepartureTime': t.tm_hour * 60 + t.tm_min,
                        'RealTimeStatus': 1,
                        'Restriction': 0,
                        'StopId': self.id,
                        'TheoricArrivalTime': None,
                        'TheoricDepartureTime': None,
                        'VehicleJourneyId': None
                    }
                    if self.parent.parent.PublicCode == i[0].text:  # if line name is the same as line
                        schedule_list.append(Schedules.Hour(element, parent=self))

            self.schedules = schedule_list
            return self.schedules

    class Hour:
        def __init__(self, data: Dict, parent=None):
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


def get_alerts(period='today', LNE: str = None) -> Dict:  # NOQA Argument name should be lower case
    """
    period=today|coming|all
    LNE=bus/metro/tram id
    """
    url = f"https://api.rtm.fr/front/getAlertes/FR/{'All' if LNE is None else LNE}"
    content = json.loads(requests.get(url, headers=headers).text)['data']
    alerts = {}
    if period in ['today', 'all']:
        alerts['AlertesToday'] = (
            [Alert(data) for data in content['AlertesToday']]
            if LNE is None
            else [Alert(data) for data in content['Alertes']]
        )
    if period in ['coming', 'all']:
        alerts['AlertesComing'] = (
            [Alert(data) for data in content.get('AlertesComing', [])]
            if LNE is None
            else []
        )
    return alerts


@cache
def get_lines(line_type: str = 'all') -> Dict[str, Dict]:
    """
    line_type=all|bus|metro|tram
    # TODO Use a better caching technique to reduce redundancy
    """
    assert line_type in ["bus", "metro", "tram", "all"], f"Invalid line type '{line_type}'"
    _lines = ["bus", "metro", "tram"] if line_type == "all" else [line_type]
    return {
        line: json.loads(
            requests.get(f'https://api.rtm.fr/front/getLines/{line}', headers=headers).text
        )['data']
        for line in _lines
    }


class Alert:
    def __init__(self, data):
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
        for i in data['AffectedLine']:
            try:
                self.AffectedLine.append(Line({'PublicCode': i['PublicCode']}))
            except Exception:  # NOQA Too broad exception clause
                print(f"[ERROR] Cannot find line with PublicCode '{i['PublicCode']}'")
