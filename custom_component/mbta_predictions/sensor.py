import datetime
import logging
from datetime import timedelta
import json
import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from dateutil.relativedelta import relativedelta
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

CONF_PREDICTIONS = "predictions"
CONF_STOP = "stop"
CONF_DIRECTION = "destination"
CONF_ROUTE = "route"
CONF_TIME_OFFSET = "offset_minutes"
CONF_LIMIT = "limit"

MBTA_COMMUTER_RAIL_LOOKUP_DICT = {
    "FAIRMOUNTLINE": "CR-Fairmount",
    "FITCHBURGLINE": "CR-Fitchburg",
    "FOXBOROEVENTSERVICE": "CR-Foxboro",
    "FRAMINGHAMWORCESTERLINE": "CR-Worcester",
    "FRANKLINLINEFOXBOROPILOT": "CR-Franklin",
    "GREENBUSHLINE": "CR-Greenbush",
    "HAVERHILLLINE": "CR-Haverhill",
    "KINGSTONPLYMOUTHLINE": "CR-Kingston",
    "LOWELLLINE": "CR-Lowell",
    "MIDDLEBOROUGHLAKEVILLELINE": "CR-Middleborough",
    "NEEDHAMLINE": "CR-Needham",
    "NEWBURYPORTROCKPORTLINE": "CR-Newburyport",
    "PROVIDENCESTOUGHTONLINE": "CR-Providence"
}

MBTA_STOP_LOOKUP_DICT = {
    "ABINGTON": "place-PB-0194",
    "AIRPORT": "place-aport",
    "ALEWIFE": "place-alfcl",
    "ANDERSONWOBURN": "place-NHRML-0127",
    "ANDOVER": "place-WR-0228",
    "ANDREW": "place-andrw",
    "AQUARIUM": "place-aqucl",
    "ASHLAND": "place-WML-0252",
    "ASHMONT": "place-asmnl",
    "ASSEMBLY": "place-astao",
    "ATTLEBORO": "place-NEC-1969",
    "AUBURNDALE": "place-WML-0102",
    "AYER": "place-FR-0361",
    "BACKBAY": "place-bbsta",
    "BALLARDVALE": "place-WR-0205",
    "BEACHMONT": "place-bmmnl",
    "BELLEVUE": "place-NB-0072",
    "BELMONT": "place-FR-0064",
    "BEVERLY": "place-ER-0183",
    "BEVERLYFARMS": "place-GB-0229",
    "BLUEHILLAVENUE": "place-DB-2222",
    "BOSTONLANDING": "place-WML-0035",
    "BOWDOIN": "place-bomnl",
    "BRADFORD": "place-WR-0325",
    "BRAINTREE": "place-brntn",
    "BRANDEISROBERTS": "place-FR-0115",
    "BRIDGEWATER": "place-MM-0277",
    "BROADWAY": "place-brdwy",
    "BROCKTON": "place-MM-0200",
    "CAMPELLO": "place-MM-0219",
    "CANTONCENTER": "place-SB-0156",
    "CANTONJUNCTION": "place-NEC-2139",
    "CENTRAL": "place-cntsq",
    "CHARLESMGH": "place-chmnl",
    "CHELSEA": "place-ER-0046",
    "CHINATOWN": "place-chncl",
    "COHASSET": "place-GRB-0199",
    "COMMUNITYCOLLEGE": "place-ccmnl",
    "CONCORD": "place-FR-0201",
    "DAVIS": "place-davis",
    "DEDHAMCORPCENTER": "place-FB-0118",
    "DOWNTOWNCROSSING": "place-dwnxg",
    "EASTWEYMOUTH": "place-GRB-0146",
    "ENDICOTT": "place-FB-0109",
    "FAIRMOUNT": "place-DB-2205",
    "FIELDSCORNER": "place-fldcr",
    "FITCHBURG": "place-FR-0494",
    "FORESTHILLS": "place-forhl",
    "FORGEPARK495": "place-FB-0303",
    "FOURCORNERSGENEVA": "place-DB-2249",
    "FOXBORO": "place-FS-0049",
    "FRAMINGHAM": "place-WML-0214",
    "FRANKLIN": "place-FB-0275",
    "GLOUCESTER": "place-GB-0316",
    "GOVERNMENTCENTER": "place-gover",
    "GRAFTON": "place-WML-0364",
    "GREENBUSH": "place-GRB-0276",
    "GREENSTREET": "place-grnst",
    "GREENWOOD": "place-WR-0085",
    "HALIFAX": "place-PB-0281",
    "HAMILTONWENHAM": "place-ER-0227",
    "HANSON": "place-PB-0245",
    "HARVARD": "place-harsq",
    "HASTINGS": "place-FR-0137",
    "HAVERHILL": "place-WR-0329",
    "HAYMARKET": "place-haecl",
    "HERSEY": "place-NB-0109",
    "HIGHLAND": "place-NB-0076",
    "HOLBROOKRANDOLPH": "place-MM-0150",
    "HYDEPARK": "place-NEC-2203",
    "IPSWICH": "place-ER-0276",
    "ISLINGTON": "place-FB-0125",
    "JACKSONSQUARE": "place-jaksn",
    "JFKUMASS": "place-jfk",
    "KENDALGREEN": "place-FR-0132",
    "KENDALLMIT": "place-knncl",
    "KINGSTON": "place-KB-0351",
    "LANSDOWNE": "place-WML-0025",
    "LAWRENCE": "place-WR-0264",
    "LINCOLN": "place-FR-0167",
    "LITTLETONRTE495": "place-FR-0301",
    "LOWELL": "place-NHRML-0254",
    "LYNN": "place-ER-0115",
    "MALDENCENTER": "place-mlmnl",
    "MANCHESTER": "place-GB-0254",
    "MANSFIELD": "place-NEC-2040",
    "MASSACHUSETTSAVENUE": "place-masta",
    "MAVERICK": "place-mvbcl",
    "MELROSECEDARPARK": "place-WR-0067",
    "MELROSEHIGHLANDS": "place-WR-0075",
    "MIDDLEBOROUGHLAKEVILLE": "place-MM-0356",
    "MISHAWUM": "place-NHRML-0116",
    "MONTELLO": "place-MM-0186",
    "MONTSERRAT": "place-GB-0198",
    "MORTONSTREET": "place-DB-2230",
    "NANTASKETJUNCTION": "place-GRB-0183",
    "NATICKCENTER": "place-WML-0177",
    "NEEDHAMCENTER": "place-NB-0127",
    "NEEDHAMHEIGHTS": "place-NB-0137",
    "NEEDHAMJUNCTION": "place-NB-0120",
    "NEWBURYPORT": "place-ER-0362",
    "NEWMARKET": "place-DB-2265",
    "NEWTONVILLE": "place-WML-0081",
    "NORFOLK": "place-FB-0230",
    "NORTHBEVERLY": "place-ER-0208",
    "NORTHBILLERICA": "place-NHRML-0218",
    "NORTHLEOMINSTER": "place-FR-0451",
    "NORTHQUINCY": "place-nqncy",
    "NORTHSCITUATE": "place-GRB-0233",
    "NORTHSTATION": "place-north",
    "NORTHWILMINGTON": "place-WR-0163",
    "NORWOODCENTRAL": "place-FB-0148",
    "NORWOODDEPOT": "place-FB-0143",
    "OAKGROVE": "place-ogmnl",
    "OAKGROVEBUSWAY": "place-ogmnl",
    "ORIENTHEIGHTS": "place-orhte",
    "PARKSTREET": "place-pktrm",
    "PLIMPTONVILLE": "place-FB-0177",
    "PLYMOUTH": "place-PB-0356",
    "PORTER": "place-portr",
    "PRIDESCROSSING": "place-GB-0222",
    "PROVIDENCE": "place-NEC-1851",
    "QUINCYADAMS": "place-qamnl",
    "QUINCYCENTER": "place-qnctr",
    "READING": "place-WR-0120",
    "READVILLE": "place-DB-0095",
    "REVEREBEACH": "place-rbmnl",
    "RIVERWORKS": "place-ER-0099",
    "ROCKPORT": "place-GB-0353",
    "ROSLINDALEVILLAGE": "place-NB-0064",
    "ROUTE128": "place-NEC-2173",
    "ROWLEY": "place-ER-0312",
    "ROXBURYCROSSING": "place-rcmnl",
    "RUGGLES": "place-rugg",
    "SALEM": "place-ER-0168",
    "SAVINHILL": "place-shmnl",
    "SHARON": "place-NEC-2108",
    "SHAWMUT": "place-smmnl",
    "SHIRLEY": "place-FR-0394",
    "SILVERHILL": "place-FR-0147",
    "SOUTHACTON": "place-FR-0253",
    "SOUTHATTLEBORO": "place-NEC-1919",
    "SOUTHBOROUGH": "place-WML-0274",
    "SOUTHSTATION": "place-sstat",
    "SOUTHWEYMOUTH": "place-PB-0158",
    "STATE": "place-state",
    "STONYBROOK": "place-sbmnl",
    "STOUGHTON": "place-SB-0189",
    "SUFFOLKDOWNS": "place-sdmnl",
    "SULLIVANSQUARE": "place-sull",
    "SWAMPSCOTT": "place-ER-0128",
    "TALBOTAVENUE": "place-DB-2240",
    "TFGREENAIRPORT": "place-NEC-1768",
    "TUFTSMEDICALCENTER": "place-tumnl",
    "UPHAMSCORNER": "place-DB-2258",
    "WACHUSETT": "place-FR-3338",
    "WAKEFIELD": "place-WR-0099",
    "WALPOLE": "place-FB-0191",
    "WALTHAM": "place-FR-0098",
    "WAVERLEY": "place-FR-0074",
    "WEDGEMERE": "place-NHRML-0073",
    "WELLESLEYFARMS": "place-WML-0125",
    "WELLESLEYHILLS": "place-WML-0135",
    "WELLESLEYSQUARE": "place-WML-0147",
    "WELLINGTON": "place-welln",
    "WELLINGTONSTATIONBUSWAY": "place-welln",
    "WESTBOROUGH": "place-WML-0340",
    "WESTCONCORD": "place-FR-0219",
    "WESTGLOUCESTER": "place-GB-0296",
    "WESTHINGHAM": "place-GRB-0162",
    "WESTMEDFORD": "place-NHRML-0055",
    "WESTNATICK": "place-WML-0199",
    "WESTNEWTON": "place-WML-0091",
    "WESTROXBURY": "place-NB-0080",
    "WEYMOUTHLANDINGEASTBRAINTREE": "place-GRB-0118",
    "WHITMAN": "place-PB-0212",
    "WICKFORDJUNCTION": "place-NEC-1659",
    "WILMINGTON": "place-NHRML-0152",
    "WINCHESTERCENTER": "place-NHRML-0078",
    "WINDSORGARDENS": "place-FB-0166",
    "WOLLASTON": "place-wlsta",
    "WONDERLAND": "place-wondl",
    "WOODISLAND": "place-wimnl",
    "WORCESTER": "place-WML-0442",
    "WYOMINGHILL": "place-WR-0062"
}

SCAN_INTERVAL = timedelta(seconds=30)
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_PREDICTIONS): [
            {
                vol.Required(CONF_STOP): cv.string,
                vol.Required(CONF_DIRECTION): cv.string,
                vol.Required(CONF_ROUTE): cv.string,
                vol.Optional(CONF_TIME_OFFSET, default=0): cv.positive_int,
                vol.Optional(CONF_LIMIT, default=10): cv.positive_int
            }
        ]
    }
)


# noinspection PyUnusedLocal,SpellCheckingInspection
def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the MBTA sensor"""
    sensors = []
    for next_train in config.get(CONF_PREDICTIONS):
        stop = next_train.get(CONF_STOP)
        direction = next_train.get(CONF_DIRECTION)
        route = next_train.get(CONF_ROUTE)
        time_offset_min = next_train.get(CONF_TIME_OFFSET)
        limit = next_train.get(CONF_LIMIT)
        name = next_train.get(CONF_NAME)
        sensors.append(MBTASensor(stop, direction, route, time_offset_min, limit, name))
    add_entities(sensors, True)


# HELPER Function
def convert_rel_date_to_eta_string(rd):
    """
    converts relative time object to a string like "3m 5s" for predictions
    :param rd: relativedelta object
    :return: string
    """
    out_str = ""
    if rd.years:
        out_str += f" {rd.years}yrs"
    if rd.months:
        out_str += f" {rd.months}months"
    if rd.days:
        out_str += f" {rd.days}days"
    if rd.hours:
        out_str += f" {rd.hours}h"
    if rd.minutes:
        out_str += f" {rd.minutes}m"
    if rd.seconds:
        out_str += f" {rd.seconds}s"
    return out_str.lstrip()


# HELPER Function
def clean_stop_string(stop):
    stop = stop.replace(" ", "")
    stop = stop.replace("/", "")
    stop = stop.replace("_", "")
    stop = stop.upper()
    return stop


class MBTASensor(Entity):
    """Implementation of an MBTA sensor"""

    def __init__(self, stop, direction, route, time_offset_min, limit, name):
        """Initialize the sensor"""
        self._stop = stop
        self._direction = direction
        if clean_stop_string(route) in MBTA_COMMUTER_RAIL_LOOKUP_DICT:
            self._route = MBTA_COMMUTER_RAIL_LOOKUP_DICT[clean_stop_string(route)]
        else
            self._route = f"{route[0].upper()}{route[1:].lower()}"
        self._time_offset_sec = time_offset_min * 60
        self._limit = limit
        if name:
            self._name = name
        else:
            self._name = f"mbta_{self._stop}"
        self._stop_id = MBTA_STOP_LOOKUP_DICT.get(clean_stop_string(self._stop), None)
        self._base_url = "https://api-v3.mbta.com/predictions"
        self._arrival_times = []

    @property
    def name(self):
        """Return the name of the sensor"""
        return self._name

    @property
    def state(self):
        """Return the next arrival times"""
        predictions = []
        logging.debug(f"creating predictions from {len(self._arrival_times)} arrival_times")
        for arrival_time in self._arrival_times:
            current_time = datetime.datetime.now()
            if (arrival_time - current_time).total_seconds() > self._time_offset_sec:
                rd = relativedelta(arrival_time, current_time)
                predictions.append(convert_rel_date_to_eta_string(rd))
            if self._limit and len(predictions) == self._limit:
                return predictions

        if len(predictions) == 0:
            logging.debug("no valid predictions, returning empty list")
            return ["--"]

        return json.dumps(predictions)

    @property
    def device_state_attributes(self):
        """Return the state attributes """
        logging.debug("returing attributes")
        return {"route": self._route, "stop": self._stop, "direction": self._direction}

    def update(self):
        """Get the latest data and update the state."""
        try:
            if self._stop_id is None:
                raise Exception(f"invalid stop: {self._stop}")
            url = f"{self._base_url}?include=trip&filter[route]={self._route}&filter[stop]={self._stop_id}"
            logging.debug("attempting to update the arrival times")
            logging.debug(f"connecting to API: {url}")
            resp = requests.get(url)
            if resp.status_code != 200:
                raise Exception('ERROR CODE: {}'.format(resp.status_code))

            logging.debug("successfully retrieved data")
            resp_json = resp.json()
            if not resp_json["data"]:
                raise Exception("stop not found on route!")

            logging.debug("parsing direction IDs from API")
            dir_to_name = {}
            for incl in resp_json["included"]:
                dir_id = incl['attributes']['direction_id']
                sign = incl['attributes']['headsign']
                if dir_id in dir_to_name:
                    if sign.lower() in dir_to_name[dir_id].lower():
                        pass
                    else:
                        dir_to_name[dir_id] = "{} or {}".format(dir_to_name[dir_id], sign)
                else:
                    dir_to_name[dir_id] = sign

            logging.debug("parsing arrival times")
            self._arrival_times = []
            for data in resp_json["data"]:
                # departure_time = data["attributes"]["departure_time"]
                arrival_time = data["attributes"]["arrival_time"]
                direction_id = data["attributes"]["direction_id"]
                direction = dir_to_name[direction_id]
                if self._direction.lower() not in direction.lower():
                    continue
                if arrival_time:
                    arrival_time = datetime.datetime.strptime(arrival_time, '%Y-%m-%dT%H:%M:%S-04:00')
                    self._arrival_times.append(arrival_time)
        except Exception as e:
            logging.exception(f"not sure what must be done here: {e}")
