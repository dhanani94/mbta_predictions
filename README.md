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

## Commuter Rail

### Supported Stops on the `Fairmount` line

* Blue Hill Avenue
* Dedham Corp Center
* Fairmount
* Four Corners/Geneva
* Foxboro
* Morton Street
* Newmarket
* Readville
* South Station
* Talbot Avenue
* Uphams Corner

### Supported Stops on the `Fitchburg` line

* Ayer
* Belmont
* Brandeis/Roberts
* Concord
* Fitchburg
* Hastings
* Kendal Green
* Lincoln
* Littleton/Rte 495
* North Leominster
* North Station
* Porter
* Shirley
* Silver Hill
* South Acton
* Wachusett
* Waltham
* Waverley
* West Concord

### Supported Stops on the `Framingham/Worcester` line

* Ashland
* Auburndale
* Back Bay
* Boston Landing
* Framingham
* Grafton
* Lansdowne
* Natick Center
* Newtonville
* South Station
* Southborough
* Wellesley Farms
* Wellesley Hills
* Wellesley Square
* West Natick
* West Newton
* Westborough
* Worcester

### Supported Stops on the `Franklin Line/Foxboro` line

* Back Bay
* Dedham Corp Center
* Endicott
* Forge Park/495
* Foxboro
* Franklin
* Hyde Park
* Islington
* Norfolk
* Norwood Central
* Norwood Depot
* Plimptonville
* Readville
* Ruggles
* South Station
* Walpole
* Windsor Gardens

### Supported Stops on the `Greenbush` line

* Cohasset
* East Weymouth
* Greenbush
* JFK/UMass
* Nantasket Junction
* North Scituate
* Quincy Center
* South Station
* West Hingham
* Weymouth Landing/East Braintree

### Supported Stops on the `Haverhill` line

* Andover
* Ballardvale
* Bradford
* Greenwood
* Haverhill
* Lawrence
* Malden Center
* Melrose Cedar Park
* Melrose Highlands
* North Station
* North Wilmington
* Reading
* Wakefield
* Wyoming Hill

### Supported Stops on the `Kingston/Plymouth` line

* Abington
* Braintree
* Halifax
* Hanson
* JFK/UMass
* Kingston
* Plymouth
* Quincy Center
* South Station
* South Weymouth
* Whitman

### Supported Stops on the `Lowell` line

* Anderson/Woburn
* Lowell
* Mishawum
* North Billerica
* North Station
* Wedgemere
* West Medford
* Wilmington
* Winchester Center

### Supported Stops on the `Middleborough/Lakeville` line

* Braintree
* Bridgewater
* Brockton
* Campello
* Holbrook/Randolph
* JFK/UMass
* Middleborough/Lakeville
* Montello
* Quincy Center
* South Station

### Supported Stops on the `Needham` line

* Back Bay
* Bellevue
* Forest Hills
* Hersey
* Highland
* Needham Center
* Needham Heights
* Needham Junction
* Roslindale Village
* Ruggles
* South Station
* West Roxbury

### Supported Stops on the `Newburyport/Rockport` line

* Beverly
* Beverly Farms
* Chelsea
* Gloucester
* Hamilton/Wenham
* Ipswich
* Lynn
* Manchester
* Montserrat
* Newburyport
* North Beverly
* North Station
* Prides Crossing
* River Works
* Rockport
* Rowley
* Salem
* Swampscott
* West Gloucester

### Supported Stops on the `Providence/Stoughton` line

* Attleboro
* Back Bay
* Canton Center
* Canton Junction
* Hyde Park
* Mansfield
* Providence
* Route 128
* Ruggles
* Sharon
* South Attleboro
* South Station
* Stoughton
* TF Green Airport
* Wickford Junction

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
