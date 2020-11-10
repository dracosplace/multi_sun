# Multi-Sun for Home Assistant

## Installation


## Configuration

# Example configuration.yaml entry
# Lat / Long or City
# Offset Days
# Offset Hours



```
sensor:
  - platform: multi_sun
    suns:
      - city: "Maputo"
        name: "Mozambique Sun"
        days_offset: months
        days_offset_value: 6
        time_offset: hours
        time_offset_value: 7
        
      - city: "Sydney"
        name: "Sydney Sun"
        days_offset: months
        days_offset_value: 7
        time_offset: hours
        time_offset_value: 9        
```
