# mbta_predictions
Home Assistant custom component for MBTA predictions. Adding this custom component allows adding sensors for specific routes to Home Assistant. After the sensors are set up, they can be visualised in LoveLace using the custom [mbta-card](https://github.com/dhanani94/mbta-card).

## Installation
The custom component source code is located [here](/custom_component/mbta_predictions). Copying the `custom_component` directory into the root directory (alongside the `configuration.yml` file) for users using HASSIO.

## Configuration
To enable this sensor, add the following lines to your `configuration.yaml` file:

```yaml
sensor:
  - platform: mbta_predictions
    predictions:
      - stop: STOP_NAME
        destination: DESTINATION_NAME
        route: ROUTE_NAME
```

example `configuration.yml`:

```yaml
# adds sensor info for MBTA Predictions
sensor:
  - platform: mbta_predictions
    predictions:
    - depart_from: JFK/UMass
      arrive_at: Alewife
      route: Red Line  # Subway
    - depart_from: Montserrat
      arrive_at: North Station
      route: Newburyport/Rockport Line  # Commuter Rail
      return_trips: True
    - depart_from: Timson St @ Brookline Ave
      arrive_at: Highland Ave @ Wyman Ave
      route: Salem Depot - Central Square, Lynn  # Bus
    - depart_from: Charlestown
      arrive_at: Long Wharf (South)
      route: Charlestown Ferry  # Ferry
```

### Configuration Variables
#### depart_from
> (string) (Required) the stop in which you will begin transit from (e.g. `JFK/UMass`)
#### arrive_at
> (string) (Required) the stop in which you will end your trip  (e.g. `Alewife`)
#### route
> (string) (Required) the route (e.g. `Red Line`, `Newburyport/Rockport Line`, `Salem Depot - Central Square, Lynn`)
#### name
> (string) (Optional) the name of the sensor (default: "mbta_DEPARTURE_TO_ARRIVAL")
#### return_trips
> (boolean) (Optional) when true, will generate a second entity with depart_from/arrive_at swapped (default: False)
#### offset_minutes
> (int) (Optional) the minimum minutes remaining before arrival (default: 0)
#### limit
> (int) (Optional) the maximum number of predictions to send back (default: 10)


## How To Find depart_from/arrive_at/route
As we're pulling these values from the MBTA API, the easiest method to find the values needed is to navigate to [MBTA Schedules Page](https://mbta.com/schedules). You'll see all of the routes available, so click the one you want to integrate.
At the top of the screen you'll see the route name, which should be used as the route in your configuration (excluding any numbers that might appear before the name). Below that, you'll either see a table or a list of stops. Use those stop names as depart_from and arrive_to values.

## Future Plans
* Create PR for custom component in the [Home Asistant Repo](https://github.com/home-assistant/home-assistant/tree/dev/homeassistant/components)
* Create custom component in HACS

* [Buy dhanani94 coffee?](https://www.buymeacoffee.com/dhanani94)
* [Buy MikeFez coffee?](https://www.buymeacoffee.com/MikeFez)

## Inspirations

* [Munich public transport departure card](https://community.home-assistant.io/t/lovelace-munich-public-transport-departure-card/59622)
* [RMV transport departures](https://community.home-assistant.io/t/rmv-transport-departures/63935)
* [MVG](https://www.home-assistant.io/integrations/mvglive)
