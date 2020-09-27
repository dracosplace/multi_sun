"""MultiSun sensor platform."""
import logging
import re
from astral import LocationInfo
from astral.geocoder import database, lookup
from astral.sun import sun
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from typing import Any, Callable, Dict, Optional
from urllib import parse

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_NAME,
    CONF_NAME,
    CONF_PATH,
    CONF_URL,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)

from .const import (
    ATTR_SUNS,
    ATTR_CITY,
    ATTR_OFFSET_DATE_UNITS,
    ATTR_OFFSET_DATE_VALUE,
    ATTR_OFFSET_TIME_UNITS,
    ATTR_OFFSET_TIME_VALUE,
    DEFAULT_OFFSET_DATE_UNIT,
    DEFAULT_OFFSET_TIME_UNIT,
    DEFAULT_SCAN_INTERVAL
)


_LOGGER = logging.getLogger(__name__)
# Time between updating data 
SCAN_INTERVAL = timedelta(minutes=DEFAULT_SCAN_INTERVAL)

CONF_SUNS = "suns"

SUN_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(ATTR_CITY): cv.string, 
        vol.Optional(ATTR_OFFSET_DATE_UNITS, default=DEFAULT_OFFSET_DATE_UNIT): vol.In(["months", "weeks", "days"]),
        vol.Optional(ATTR_OFFSET_DATE_VALUE): cv.small_float,
        vol.Optional(ATTR_OFFSET_TIME_UNITS, default=DEFAULT_OFFSET_TIME_UNIT): vol.In(["hours", "minutes", "seconds"]),
        vol.Optional(ATTR_OFFSET_TIME_VALUE): cv.small_float,
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SUNS): vol.All(cv.ensure_list, [SUN_SCHEMA]),
    }
)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    session = async_get_clientsession(hass)
    sensors = [MultiSunSensor(current_sun) for current_sun in config[CONF_SUNS]]
    async_add_entities(sensors, update_before_add=True)


class MultiSunSensor(Entity):
    """Representation of a MultiSun sensor."""

    def __init__(self, current_sun: Dict[str, str]):
        super().__init__()
        self.current_sun = current_sun["name"]
        self.attrs: Dict[str, Any] = {ATTR_PATH: self.current_sun}
        self._name = current_sun.get("name", self.current_sun)
        self._city = current_sun.get("city", self.current_sun)
        self._date_units = current_sun.get(ATTR_OFFSET_DATE_UNITS, self.current_sun)
        self._date_value = current_sun.get(ATTR_OFFSET_DATE_VALUE, self.current_sun)
        self._time_units = current_sun.get(ATTR_OFFSET_TIME_UNITS, self.current_sun)
        self._time_value = current_sun.get(ATTR_OFFSET_TIME_VALUE, self.current_sun)
        self._state = None
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return self.current_sun

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        return self.attrs

    async def async_update(self):
        try:
            #repo_url = f"/repos/{self.repo}"
            #repo_data = await self.github.getitem(repo_url)
            date_offset = date.today() + relativedelta(**{self._date_units: self._date_value})
            city = lookup(self._city, database())
            #sixmonthDay = six_months.day
            #sixmonthMonth = six_months.month
            s2 = sun(city.observer, date=date_offset)
            time_offset = relativedelta(**{self._time_units: self._time_value})
            #fivehourshiftsunrise = s2["sunrise"] + relativedelta(hours=+7) 
            #fivehourshiftsunset = s2["sunset"] + relativedelta(hours=+7)
            #diff = fivehourshiftsunset - fivehourshiftsunrise
            #diff_hours = diff.seconds / 3600
            self.attrs[ATTR_SUNRISE] = s2["sunrise"] + time_offset
            self.attrs[ATTR_SUNSET] = s2["sunset"] + time_offset            

            self._available = True
        except (ClientError, gidgethub.GitHubException):
            self._available = False
            _LOGGER.exception("Error calculating multisun data.")
