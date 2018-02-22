
import jsonschema
from spin_store.settings import ugettext_lazy as _

validate = jsonschema.validate

example_schema = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "properties": {
        "spin":     {'type': 'boolean', 'description': _("spin")},
        "charge":   {"type": "string", 'description': _("charge")},
        "color":    {"type": "string", 'description': _("color")},
        "momentum": {"type": "integer", 'description': _("momentum")},
    },
    "defaults": {
        "spin": False,
        "charge": "e",  
        "color":  "white",
        "momentum": 0,
    }
}

JSONSCHEMAS = {
    'Generic': {
        'description': _("Quark's params"),
        'visibility': 1,
        'examples': {
            "restart": True,
            "name": "eth0",
            "address": "192.168.23.23",
            "source": "static",
        },
        'jsonschema': example_schema,
    },
    'Quark': {
        'description': _("Quark's params"),
        'visibility': 1,
        'examples': {
            "restart": True,
            "name": "eth0",
            "address": "192.168.23.23",
            "source": "static",
        },
        'jsonschema': example_schema,
    },
    'Lepton': {
        'description': _("Lepton's params"),
        'visibility': 1,
        'examples': {
            "restart": True,
            "name": "eth0",
            "address": "192.168.23.23",
            "source": "static",
        },
        'jsonschema': example_schema,
    },
    'ScalarBoson': {
        'description': _("ScalarBoson's params"),
        'visibility': 1,
        'examples': {
            "restart": True,
            "name": "eth0",
            "address": "192.168.23.23",
            "source": "static",
        },
        'jsonschema': example_schema,
    },
    'GaugeBoson': {
        'description': _("GaugeBoson's params"),
        'visibility': 1,
        'examples': {
            "restart": True,
            "name": "eth0",
            "address": "192.168.23.23",
            "source": "static",
        },
        'jsonschema': example_schema,
    },
}
