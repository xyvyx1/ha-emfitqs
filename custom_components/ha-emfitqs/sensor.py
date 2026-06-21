import logging
import datetime
from datetime import timedelta
import requests
import voluptuous as vol
import time
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorStateClass
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (ATTR_ATTRIBUTION, CONF_HOST, CONF_SCAN_INTERVAL, CONF_RESOURCES)
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

__version__ = '1.1'

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=10)
CONF_ATTRIBUTION = "Data provided by Emfit QS"
DATA_ARLO = 'data_emfitqs'
DEFAULT_BRAND = 'Emfit'
DOMAIN = 'emfitqs'

INTERVAL = 10
HOST = '192.168.1.40'

SENSOR_PREFIX = 'EmfitQS '

SENSOR_TYPES = {
    'heart_rate': ['Heart Rate', 'bpm', 'mdi:heart','hr', SensorStateClass.MEASUREMENT],
    'respiratory_rate': ['Respiratory Rate', 'bpm', 'mdi:pinwheel','rr', SensorStateClass.MEASUREMENT],
    'activity_level': ['Activity', '', 'mdi:vibrate','act', SensorStateClass.MEASUREMENT],
    'seconds_in_bed': ['Seconds in Bed', 's', 'mdi:timer', '', SensorStateClass.TOTAL]
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_RESOURCES, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    scan_interval = config.get(CONF_SCAN_INTERVAL)
    host = config.get(CONF_HOST)

    try:
        data = EmfitQSData(host)
        data.update()
        sensors = []

        for resource in config[CONF_RESOURCES]:
            sensor_type = resource.lower()
            if sensor_type == 'seconds_in_bed':
                sensors.append(EmfitQSTimeInBedSensor(data.data['ser'], data, sensor_type))
            else:
                sensors.append(EmfitQSSensor(data.data['ser'], data, sensor_type))

        add_entities(sensors)
        return True
    except Exception as e:
        _LOGGER.error("Error ocurred: " + repr(e))
        return False

class EmfitQSData(object):    

    def __init__(self, host):       
        self._host = host
        self.data = None
    
    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):      
        entries = {}
        try:
            r = requests.get('http://{0}/dvmstatus.htm'.format(self._host), timeout=10)       
            if r.status_code == 200:
                elements = r.text.replace("<br>",'').lower().split('\r\n')
                filtered = list(filter(None, elements))
                for f in filtered:
                    entry = f.split("=")
                    entry_name = entry[0].replace(':', '').replace(' ', '_').replace(',', '')
                    entry_value = entry[1]
                    entries[entry_name] = entry_value
            requests.session().close()
        except Exception as e:
            _LOGGER.error("Error ocurred: " + repr(e))

        self.data = entries
        _LOGGER.debug("Data = %s", self.data)

class EmfitQSTimeInBedSensor(Entity):    

    def __init__(self, serial, data, sensor_type):
        self.last_presence_change = datetime.datetime.now()
        self.data = data
        self.type = sensor_type
        self._attr_name = SENSOR_PREFIX + serial + ' ' + SENSOR_TYPES[self.type][0]
        self._attr_unit_of_measurement = SENSOR_TYPES[self.type][1]
        self._attr_icon = SENSOR_TYPES[self.type][2]
        self._attr_state_class = SENSOR_TYPES[self.type][4]
        self._attr_state = None
        self._resource = SENSOR_TYPES[self.type][3]  # needed for update method
        self._attr_device_state_attributes = {
            ATTR_ATTRIBUTION: CONF_ATTRIBUTION
        }

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        try:
            old_presence = self.data.data['pres']
            self.data.update()
            data = self.data.data  
            new_presence = self.data.data['pres']
            if new_presence == "1":            
                new_ts = datetime.datetime.now() - self.last_presence_change 
                self._attr_state = round(new_ts.total_seconds())
            else:
                self.last_presence_change = datetime.datetime.now()            
                self._attr_state = 0
        except Exception as e:
            _LOGGER.error("Error ocurred: " + repr(e))

class EmfitQSSensor(Entity):

    def __init__(self, serial, data, sensor_type):
        self.data = data
        self.type = sensor_type
        self._attr_name = SENSOR_PREFIX + serial + ' ' + SENSOR_TYPES[self.type][0]
        self._attr_unit_of_measurement = SENSOR_TYPES[self.type][1]
        self._attr_icon = SENSOR_TYPES[self.type][2]
        self._attr_state_class = SENSOR_TYPES[self.type][4]
        self._attr_state = None
        self._resource = SENSOR_TYPES[self.type][3]  # needed for update method
        self._attr_device_state_attributes = {
            ATTR_ATTRIBUTION: CONF_ATTRIBUTION
        }

    def update(self):
        try:
            self.data.update()
            data = self.data.data
            self._attr_state = data[self._resource]
        except Exception as e:
            _LOGGER.error("Error ocurred: " + repr(e))
