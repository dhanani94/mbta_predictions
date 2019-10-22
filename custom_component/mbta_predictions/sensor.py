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

MBTA_STOP_LOOKUP_DICT = {
    "ALEWIFE": "place-alfcl",
    "DAVIS": "place-davis",
    "PORTER": "place-portr",
    "HARVARD": "place-harsq",
    "CENTRAL": "place-cntsq",
    "KENDALLMIT": "place-knncl",
    "CHARLESMGH": "place-chmnl",
    "PARKSTREET": "place-pktrm",
    "DOWNTOWNCROSSING": "place-dwnxg",
    "SOUTHSTATION": "place-sstat",
    "BROADWAY": "place-brdwy",
    "ANDREW": "place-andrw",
    "JFKUMASS": "place-jfk",
    "SAVINHILL": "place-shmnl",
    "FIELDSCORNER": "place-fldcr",
    "SHAWMUT": "place-smmnl",
    "ASHMONT": "place-asmnl",
    "NORTHQUINCY": "place-nqncy",
    "WOLLASTON": "place-wlsta",
    "QUINCYCENTER": "place-qnctr",
    "QUINCYADAMS": "place-qamnl",
    "BRAINTREE": "place-brntn"
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
