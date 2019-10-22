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

* **Alewife**
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
* **Ashmont**
* North Quincy
* Wollaston
* Quincy Center
* Quincy Adams
* **Braintree**

### Supported Stops on the `Orange` line

* **Oak Grove**
* Malden Center
* Wellington
* Assembly
* Sullivan Square
* Community College
* North Station
* Haymarket
* State
* Downtown Crossing
* Chinatown
* Tufts Medical Center
* Back Bay
* Massachusetts Avenue
* Ruggles
* Roxbury Crossing
* Jackson Square
* Stony Brook
* Green Street
* **Forest Hills**

### Supported Stops on the `Blue` line

* **Wonderland**
* Revere Beach
* Beachmont
* Suffolk Downs
* Orient Heights
* Wood Island
* Airport
* Maverick
* Aquarium
* State
* Government Center
* **Bowdoin**

## Future Plans 

* Add support for the other lines (green and silver)
* Add support for buses 
* Create PR for custom component in the [Home Asistant Repo](https://github.com/home-assistant/home-assistant/tree/dev/homeassistant/components)
* Create custom compnent in HACS 
* [Buy me coffee?](https://www.buymeacoffee.com/dhanani94)

## Inspirations

* [Munich public transport departure card](https://community.home-assistant.io/t/lovelace-munich-public-transport-departure-card/59622)
* [RMV transport departures](https://community.home-assistant.io/t/rmv-transport-departures/63935)
* [MVG](https://www.home-assistant.io/integrations/mvglive)
