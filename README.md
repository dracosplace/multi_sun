# Multi-Sun for Home Assistant

## Installation


## Configuration

# Example configuration.yaml entry
# Lat / Long or City
# Offset Days
# Offset Hours

sensor:

- platform: multi_sun

    - suns:

      - lat: -70.00
        long: 32.0012
        city: "Maputo"
        offset_date_units: "months"
        offset_date_values: 6
        offset_time_units: "hours"
        offset_time_values: 7

- platform: multi_sun

    - suns:
        
      - lat: -40.00
        long: 62.0012
        city: "Sydney"
        offset_date_units: "months"
        offset_date_values: 7
        offset_time_units: "hours"
        offset_time_values: 9