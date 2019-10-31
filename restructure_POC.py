#!/usr/bin/env python3
import requests
import datetime
import json

route = "CR-Newburyport"
departure = "Montserrat"
arrival = "Lynn"
api_url = f"https://api-v3.mbta.com/schedules?sort=arrival_time&include=stop%2Ctrip%2Cprediction%2Croute&filter%5Broute%5D={route}"


def main():
    # Final parsed data will go in here
    organized = {"arrival->departure": [], "departure->arrival": []}

    res = requests.get(api_url)
    res.raise_for_status()

    # Identify trips that contain at least a single designated stop
    departure_arrival_by_trip = {}
    for item in res.json()['data']:
        stop_name = item['relationships']['stop']['data']['id']
        trip_name = item['relationships']['trip']['data']['id']
        if stop_name in [arrival, departure]:
            if trip_name not in departure_arrival_by_trip:
                departure_arrival_by_trip[trip_name] = {}
            departure_arrival_by_trip[trip_name][stop_name] = item

    # At this point, we have all trips and have extracted arrival and departure, if they exist.
    # We're going to prune trips where both do not exist. If they do, we're going to figure out direction, and determine
    # If they have not yet passed the initial stop. If they haven't, we'll add them to the organized data dict
    for trip, stops in departure_arrival_by_trip.items():
        if len(stops) == 2:  # If both stops are located on this trip
            now = datetime.datetime.now()
            if stops[arrival]["attributes"]["stop_sequence"] < stops[departure]["attributes"]["stop_sequence"]:
                first_stop = arrival
                direction = "arrival->departure"
            else:
                first_stop = departure
                direction = "departure->arrival"

            arrival_time = datetime.datetime.strptime(stops[first_stop]["attributes"]["arrival_time"],
                                                      '%Y-%m-%dT%H:%M:%S-04:00')
            if arrival_time >= now:
                organized[direction].append(stops)

    for direction, trips in organized.items():
        print(direction)
        for trip in trips:
            print("\t", trip)
    return


if __name__ == "__main__":
    main()
