#!/usr/bin/env python3
import requests
import datetime
import json

route = "CR-Newburyport"
departure = "Montserrat"
arrival = "Lynn"
api_url = f"https://api-v3.mbta.com/schedules?sort=arrival_time&include=stop%2Ctrip%2Cprediction&filter%5Broute%5D={route}"

# Compare to this URL to ensure that results are the same regardless of if places are defined
# api_url = "https://api-v3.mbta.com/schedules?sort=arrival_time&include=stop%2Ctrip%2Cprediction&filter%5Broute%5D=CR-Newburyport&filter%5Bstop%5D=place-GB-0198%2Cplace-ER-0115"


def main():
    # Final parsed data will go in here
    organized = {"departure->arrival": [], "arrival->departure": []}

    res = requests.get(api_url)
    res.raise_for_status()
    res_json = res.json()
    # Identify trips that contain at least a single designated stop
    departure_arrival_by_trip = {}
    for item in res_json['data']:
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

    # Finally, lets get predictions
    predictions_by_id = {}
    for item in res_json['included']:
        if item["type"] == "prediction" and item['relationships']['stop']['data']['id'] in [arrival, departure]:
            predictions_by_id[item["id"]] = item

    for direction_string, trips in organized.items():
        print(direction_string)
        stop_order = [arrival, departure] if direction_string == "arrival->departure" else [departure, arrival]
        for trip_no, trip in enumerate(trips):
            print(f"\tNext #{trip_no}")
            for stop_no, stop_name in enumerate(stop_order):
                print(f"\t\t{'On' if stop_no==0 else 'Off'} at [{stop_name}]: {trip[stop_name]}")
                prediction_data = trip[stop_name]['relationships']['prediction']['data']
                if prediction_data is not None:
                    print(f"\t\t\tRelated Prediction: {predictions_by_id[prediction_data['id']]}")
                    predicted_arrival = datetime.datetime.strptime(predictions_by_id[prediction_data['id']]['attributes']['arrival_time'], '%Y-%m-%dT%H:%M:%S-04:00')
                    scheduled_arrival = datetime.datetime.strptime(trip[stop_name]["attributes"]["arrival_time"], '%Y-%m-%dT%H:%M:%S-04:00')
                    diff = predicted_arrival - scheduled_arrival
                    days, seconds = diff.days, diff.seconds
                    hours = days * 24 + seconds // 3600
                    minutes = (seconds % 3600) // 60
                    seconds = seconds % 60
                    print(f"\t\t\tDelayed By[H:M:S]: {hours}:{minutes}:{seconds}")
        print("\n")

    print("\nAll Predictions - there may be more here because both stops may not be on the trip:")
    for prediction_id, prediction in predictions_by_id.items():
        print(prediction_id, prediction)
    return


if __name__ == "__main__":
    main()
