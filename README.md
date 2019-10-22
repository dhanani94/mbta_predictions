# mbta_predictions
Home Assistant custom component for MBTA predictions. Adding this custom component allows adding sensors for specific routes to Home Assistant. 

## Installation 
The custom component source code is located [here](/custom_component/mbta_predictions). Copying the `custom_component` directory into the root directory (alongside the `configuration.yml` file) for users using HASSIO. 

## Configuration 
To enable this sensor, add the following lines to your configuration.yaml file:

```
sensor:
  - platform: mbta_predictions
    predictions:
      - stop: STOP_NAME
        destination: DESTINATION_NAME
        route: ROUTE_NAME
```

example `configuration.yml`:
```
# adds sensor info for MBTA Predictions
sensor:
  - platform: mbta_predictions
    predictions:
     - stop: JFK/UMass
       destination: Alewife
       route: Red
     - stop: Savin Hill
       destination: Alewife
       route: Red
     - stop: South Station
       destination: Ashmont
       route: Red
```

### Configuration Variables
#### stop
> (string) (Required) the stop name (e.g. Harvard)
#### destination
> (string) (Required) the file stop for the train (e.g. `Braintree`)
#### route
> (string) (Required) the route (e.g. `Red`)
#### name
> (string) (Optional) the name of the sensor (default: "mbta_STOP_NAME")
#### offset_minutes
> (int) (Optional) the minimum minutes remaining before arrival (default: 0)
#### limit
> (int) (Optional) the maximum number of predictions to send back (default: 10)


### Supported Stops on the `Red` line

* Alewife
* Davis
* Porter
* Harvard
* Central
* Kendall/MIT
* Charles/MGH
* Park Street
* Downtown Crossing
* South Station
* Broadway
* Andrew
* JFK/UMass
* Savin Hill
* Fields Corner
* Shawmut
* Ashmont
* North Quincy
* Wollaston
* Quincy Center
* Quincy Adams
* Braintree

## Future Plans 

* Add support for the other lines (orange, blue, green, silver)
* Add support for buses 
* Create PR for custom component in the [Home Asistant Repo](https://github.com/home-assistant/home-assistant/tree/dev/homeassistant/components)
* Create custom compnent in HACS 
* [Buy me coffee?](https://www.buymeacoffee.com/dhanani94)

