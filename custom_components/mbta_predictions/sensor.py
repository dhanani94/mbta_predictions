from datetime import datetime, timezone, timedelta
import logging
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
CONF_DEPART_FROM = "depart_from"
CONF_ARRIVE_AT = "arrive_at"
CONF_ROUTE = "route"
CONF_RETURN_TRIPS = "return_trips"
CONF_TIME_OFFSET = "offset_minutes"
CONF_LIMIT = "limit"

SCAN_INTERVAL = timedelta(seconds=30)
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_PREDICTIONS): [
            {
                vol.Required(CONF_DEPART_FROM): cv.string,
                vol.Required(CONF_ARRIVE_AT): cv.string,
                vol.Required(CONF_ROUTE): cv.string,
                vol.Optional(CONF_RETURN_TRIPS, default=False): cv.boolean,
                vol.Optional(CONF_TIME_OFFSET, default=0): cv.positive_int,
                vol.Optional(CONF_LIMIT, default=10): cv.positive_int
            }
        ]
    }
)

BASE_URL = "https://api-v3.mbta.com"
ROUTE_DATA_BY_NAME = {}
ROUTE_TYPES = {
    0: "LightRail",
    1: "HeavyRail",
    2: "CommuterRail",
    3: "Bus",
    4: "Ferry"
}


# noinspection PyUnusedLocal,SpellCheckingInspection
def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the MBTA sensor"""
    populate_global_route_data_by_name()

    sensors = []
    for next_train in config.get(CONF_PREDICTIONS):
        depart_from = next_train.get(CONF_DEPART_FROM)
        arrive_at = next_train.get(CONF_ARRIVE_AT)
        route = next_train.get(CONF_ROUTE)
        time_offset_min = next_train.get(CONF_TIME_OFFSET)
        limit = next_train.get(CONF_LIMIT)
        name = next_train.get(CONF_NAME)

        sensors.append(MBTASensor(depart_from, arrive_at, route, time_offset_min, limit, name))
        # If a return trip was specified, lets grab the reverse
        if next_train.get(CONF_RETURN_TRIPS):
            sensors.append(MBTASensor(arrive_at, depart_from, route, time_offset_min, limit, name))
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


def datetime_from_json(json_datatime):
    return datetime.fromisoformat(json_datatime)


def get_current_time():
    return datetime.now(timezone.utc).astimezone()


def populate_global_route_data_by_name():
    global ROUTE_DATA_BY_NAME
    res = requests.get(f"{BASE_URL}/routes?include=stop")  # Doesn't actually seem to include stops
    res.raise_for_status()
    res_json = res.json()
    for route in res_json['data']:
        ROUTE_DATA_BY_NAME[route['attributes']['long_name']] = {
            'id': route['id'],
            'color': route['attributes']['color'],
            'type': ROUTE_TYPES[route['attributes']['type']]
        }
    return


def get_stops_by_trip(api_response, stops_to_extract=()):
    # Organize stops the user wants by trip. Not all trips may have both stops which we'll handle later
    stops_by_trip = {}
    for item in api_response['data']:
        stop_name = item['relationships']['stop']['data']['id']
        trip_name = item['relationships']['trip']['data']['id']
        if not stops_to_extract or any(stop_name.lower() == stop.lower() for stop in stops_to_extract):
            if trip_name not in stops_by_trip:
                stops_by_trip[trip_name] = {}
            stops_by_trip[trip_name][stop_name] = item
    return stops_by_trip


def organize_included_data_by_type(api_response):
    organized = {}
    for item in api_response['included']:
        item_type = item["type"]
        item_id = item["id"]
        if item_type not in organized:
            organized[item_type] = {}
        organized[item_type][item_id] = item
    return organized


class MBTASensor(Entity):
    """Implementation of an MBTA sensor"""

    def __init__(self, depart_from, arrive_at, route, time_offset_min, limit, name):
        """Initialize the sensor"""
        self._depart_from = depart_from
        self._arrive_at = arrive_at
        self._route = route
        self._time_offset_sec = time_offset_min * 60
        self._limit = limit
        self._name = name if name else f"mbta_{self._depart_from}_to_{self._arrive_at}".replace(' ', '_')
        self._transit_color = ROUTE_DATA_BY_NAME[self._route]['color']
        self._transit_type = ROUTE_DATA_BY_NAME[self._route]['type']
        self._arrival_data = []
        self._direction = None

    @property
    def name(self):
        """Return the name of the sensor"""
        return self._name

    @property
    def state(self):
        """Return the next arrival time"""
        if len(self._arrival_data) == 0:
            logging.debug("no valid predictions, returning empty list")
            return "Nothing Scheduled"
        else:
            return self._arrival_data[0]['departure']

    @property
    def extra_state_attributes(self):
        """Return the state attributes """
        logging.debug("returing attributes")
        return {
            "route": self._route,
            "depart_from": self._depart_from,
            "arrive_at": self._arrive_at,
            "delay": self._arrival_data[0]['delay'] if len(self._arrival_data) > 0 else None,
            "upcoming_departures": json.dumps(self._arrival_data[1:self._limit]) if len(self._arrival_data) > 0 else json.dumps([]),
            "route_type": self._transit_type,
            "route_color": self._transit_color,
            "direction": self._direction
        }

    def update(self):
        """Get the latest data and update the state."""
        try:
            route_id = ROUTE_DATA_BY_NAME[self._route]['id']
            url = f"{BASE_URL}/schedules?sort=arrival_time&include=stop%2Ctrip%2Cprediction&filter%5Broute%5D={route_id}"

            logging.debug(f"Requesting API to update {self._route} [{self._depart_from}]: {url}")
            resp = requests.get(url)
            if resp.status_code != 200:
                raise Exception('ERROR CODE: {}'.format(resp.status_code))
            logging.debug(f"Successfully retrieved data for {self._route} [{self._depart_from}]")
            resp_json = resp.json()
            if not resp_json["data"]:
                raise Exception("Route data was not found!")

            # Lets grab data in organized form
            included_data = organize_included_data_by_type(resp_json)


            # These don't need to be parsed as we will reference them by key
            predictions_by_id = included_data["prediction"] if "prediction" in included_data else {}

            stop_ids_by_name = {}
            for _, stop in included_data['stop'].items():
                name = stop['attributes']['name']
                stop_ids_by_name.setdefault(name, {})[stop['id']] = stop
            try:
                depart_from_ids = stop_ids_by_name[self._depart_from]
                arrive_at_ids   = stop_ids_by_name[self._arrive_at]
            except KeyError:
                logging.debug(f"No trips invovling {self._depart_from} and {self._arrive_at}")
                return

            stops_by_trip = get_stops_by_trip(resp_json, stops_to_extract=[*depart_from_ids.keys(), *arrive_at_ids.keys()])

            current_time = get_current_time()
            # Now we're going to start parsing through the stops on trip and prediction data
            self._arrival_data = []
            for trip, stops in stops_by_trip.items():

                if len(stops) == 2:
                    # Work out which stop is which
                    (depart_id, arrive_id) = stops.keys()
                    if (arrive_id in depart_from_ids):
                        (depart_id, arrive_id) = (arrive_id, depart_id)

                    arrive_stop = stops[arrive_id]
                    depart_stop = stops[depart_id]

                    # If trip has both stops AND the trip has the depart_from stop before the arrive_at stop
                    if depart_stop["attributes"]["stop_sequence"] < arrive_stop["attributes"]["stop_sequence"]:
                        scheduled_time = datetime_from_json(depart_stop["attributes"]["departure_time"])
                        predicted_time = None  # Gotta figure out if predicted departure is accurate
                        prediction_data = depart_stop['relationships']['prediction']['data']

                        if prediction_data is not None and prediction_data['id'] in predictions_by_id:
                            predicted_time = datetime_from_json(predictions_by_id[prediction_data['id']]['attributes']['departure_time'])

                        # Use prediction might not be available, or scheduled time if not.
                        accurate_departure = predicted_time if predicted_time is not None else scheduled_time

                        if (accurate_departure - current_time).total_seconds() > self._time_offset_sec:
                            time_until_arrival = convert_rel_date_to_eta_string(relativedelta(accurate_departure, current_time))
                            delay = None
                            # If there is a prediction, and the prediction isn't the actual scheduled arrival time
                            if predicted_time is not None and predicted_time != scheduled_time:
                                delay = convert_rel_date_to_eta_string(relativedelta(predicted_time, scheduled_time))

                            self._arrival_data.append({
                                "departure": time_until_arrival,
                                "delay": delay
                            })

                            self._direction = depart_stop["attributes"]["direction_id"]

        except Exception as e:
            logging.exception(f"Encountered Exception: {e}")
