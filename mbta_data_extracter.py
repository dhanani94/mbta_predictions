#!/usr/bin/env python3
"""
This tool formats data for use with dhanani94/mbta_predictions.
It generated a dictionary of {routes:route_ids}, {stop:stop_ids}, and a markdown string for use with the readme
listing all of stop options per route.
"""

import requests
import json
from time import sleep
from os import makedirs


class RouteTypes:
    LightRail = 0
    HeavyRail = 1
    CommuterRail = 2
    Bus = 3
    Ferry = 4


def route_type_as_string(route_type):
    return ["LightRail", "HeavyRail", "CommuterRail", "Bus", "Ferry"][route_type]


def output_data(route_type):
    route_type_string = route_type_as_string(route_type)
    print(f"Getting all {route_type_string} routes")
    route_ids_by_name = get_route_ids_by_name(route_type)

    stop_data_per_route = {}
    for route_name, route_id in route_ids_by_name.items():
        sleep(5)  # Playing nice with their API
        print(f"Getting stops for {route_name}")
        stop_data_per_route[route_name] = get_stop_ids_by_name(route_id)

    markdown_string_array = []
    stop_ids_by_name = {}
    for route_name, route_id in route_ids_by_name.items():
        markdown_string_array.append(f"\n### Supported Stops on the `{route_name}` line\n")
        for stop_name, stop_id in stop_data_per_route[route_name].items():
            stop_ids_by_name[clean_stop_string(stop_name)] = stop_id
            markdown_string_array.append(f"* {stop_name}")

    makedirs("MBTA_DATA", exist_ok=True)
    with open("MBTA_DATA/route_ids_by_name.json", "w") as text_file:
        formatted_data = {clean_stop_string(route_name): route_id for route_name, route_id in route_ids_by_name.items()}
        print(json.dumps(formatted_data, indent=4, sort_keys=True), file=text_file)

    with open("MBTA_DATA/stop_ids_by_name.json", "w") as text_file:
        print(json.dumps(stop_ids_by_name, indent=4, sort_keys=True), file=text_file)

    with open("MBTA_DATA/readme_md_string.json", "w") as text_file:
        print("\n".join(markdown_string_array), file=text_file)
    return


def clean_stop_string(stop):
    stop = stop.replace(" ", "")
    stop = stop.replace("/", "")
    stop = stop.replace("_", "")
    stop = stop.upper()
    return stop


def get_route_ids_by_name(route_type):
    route_data = requests.get(f"https://api-v3.mbta.com/routes?filter%5Btype%5D={route_type}").json()
    data = {}
    for route in route_data["data"]:
        route_name = route["attributes"]["long_name"]
        route_id = route["id"]
        data[route_name] = route_id
    return data


def get_stop_ids_by_name(route_id):
    route_stops = requests.get(f"https://api-v3.mbta.com/stops?sort=name&filter%5Broute%5D={route_id}").json()
    data = {}
    for stop in route_stops["data"]:
        stop_name = stop["attributes"]["name"]
        stop_id = stop["id"]
        data[stop_name] = stop_id
    return data


def dict_to_file():
    """
    For quick deduping of stop key/id dict, I just pop it all in here and then save it to a file as dict will dedupe
    :return:
    """
    data = {}
    with open("CR_CONSOLIDATED.json", "w") as text_file:
        print(json.dumps(data, indent=4, sort_keys=True), file=text_file)
    return


if __name__ == "__main__":
    # Change RouteType here for extraction of that type
    output_data(RouteTypes.CommuterRail)
