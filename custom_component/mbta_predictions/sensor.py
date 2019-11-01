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


# noinspection PyUnusedLocal,SpellCheckingInspection
def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the MBTA sensor"""
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


def format_name(name):
    return name


def datetime_from_json(json_datatime):
    return datetime.datetime.strptime(json_datatime, '%Y-%m-%dT%H:%M:%S-04:00')


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


# def get_predictions_by_id(api_response, stops_to_extract=()):
#     predictions_by_id = {}
#     for item in [item for item in api_response['included'] if item["type"] == "prediction"]:
#         stop_name = item['relationships']['stop']['data']['id']
#         if not stops_to_extract or any(stop_name.lower() == stop.lower() for stop in stops_to_extract):
#             predictions_by_id[item["id"]] = item
#     return predictions_by_id


def organize_included_data(api_response):
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
        self._base_url = "https://api-v3.mbta.com/schedules"
        self._arrival_data = []

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
    def device_state_attributes(self):
        """Return the state attributes """
        logging.debug("returing attributes")
        return {"route": self._route,
                "depart_from": self._depart_from,
                "arrive_at": self._arrive_at,
                "delay": self._arrival_data[0]['delay'] if len(self._arrival_data) > 0 else None,
                "upcoming_departures": json.dumps(self._arrival_data[1:self._limit]) if len(self._arrival_data) > 0 else json.dumps([])}

    def update(self):
        """Get the latest data and update the state."""
        try:
            url = f"{self._base_url}?sort=arrival_time&include=stop%2Ctrip%2Cprediction&filter%5Broute%5D={self._route}"
            logging.debug(f"Requesting API to update {self._route} [{self._depart_from}]: {url}")
            resp = requests.get(url)
            if resp.status_code != 200:
                raise Exception('ERROR CODE: {}'.format(resp.status_code))
            logging.debug(f"Successfully retrieved data for {self._route} [{self._depart_from}]")
            resp_json = resp.json()
            if not resp_json["data"]:
                raise Exception("Route data was not found!")

            # Lets grab data in organized form
            included_data = organize_included_data(resp_json)

            # These don't need to be parsed as we will reference them by key
            predictions_by_id = included_data["prediction"]
            stop_name_by_id = {stop['attributes']['name']: stop['id'] for stop in included_data['stop']}

            stops_by_trip = get_stops_by_trip(resp_json, stops_to_extract=[stop_name_by_id[self._depart_from],
                                                                           stop_name_by_id[self._arrive_at]])

            current_time = datetime.datetime.now()
            # Now we're going to start parsing through the stops on trip and prediction data
            self._arrival_data = []
            for trip, stops in stops_by_trip.items():
                # If trip has both stops AND the trip has the depart_from stop before the arrive_at stop
                if len(stops) == 2 and stops[self._depart_from]["attributes"]["stop_sequence"] < stops[self._arrive_at]["attributes"]["stop_sequence"]:
                    scheduled_time = datetime_from_json(stops[self._depart_from]["attributes"]["departure_time"])
                    predicted_time = None  # Gotta figure out if predicted departure is accurate
                    prediction_data = stops[self._depart_from]['relationships']['prediction']['data']
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

        except Exception as e:
            logging.exception(f"Encountered Exception: {e}")
