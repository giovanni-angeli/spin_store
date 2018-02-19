
import jsonschema
from spin_store.settings import ugettext_lazy as _

validate = jsonschema.validate


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
        'jsonschema': {
            "$schema": "http://json-schema.org/draft-06/schema#",
            "properties": {
                "restart": {'type': 'boolean', 'description': _("if True, the interface is restarted after setting it. optional, default True")},
                "name": {"type": "string", 'description': _("name of the interface e.g. eth0, required.")},
                "address": {"type": "string", 'description': _("ip4 address.")},
                "source": {"type": "string", 'pattern': '(^static$|^dhcp$)', 'description': _("'dhcp' or 'static', optional, default static.")},
            },
            "defaults": {
                "name": None,
                "address": "",
                "source": "static",
                "restart": True,
            },
        },
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
        'jsonschema': {
            "$schema": "http://json-schema.org/draft-06/schema#",
            "properties": {
                "restart": {'type': 'boolean', 'description': _("if True, the interface is restarted after setting it. optional, default True")},
                "name": {"type": "string", 'description': _("name of the interface e.g. eth0, required.")},
                "address": {"type": "string", 'description': _("ip4 address.")},
                "source": {"type": "string", 'pattern': '(^static$|^dhcp$)', 'description': _("'dhcp' or 'static', optional, default static.")},
            },
            "defaults": {
                "name": None,
                "address": "",
                "source": "static",
                "restart": True,
            },
        },
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
        'jsonschema': {
            "$schema": "http://json-schema.org/draft-06/schema#",
            "properties": {
                "restart": {'type': 'boolean', 'description': _("if True, the interface is restarted after setting it. optional, default True")},
                "name": {"type": "string", 'description': _("name of the interface e.g. eth0, required.")},
                "address": {"type": "string", 'description': _("ip4 address.")},
                "source": {"type": "string", 'pattern': '(^static$|^dhcp$)', 'description': _("'dhcp' or 'static', optional, default static.")},
            },
            "defaults": {
                "name": None,
                "address": "",
                "source": "static",
                "restart": True,
            },
        },
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
        'jsonschema': {
            "$schema": "http://json-schema.org/draft-06/schema#",
            "properties": {
                "restart": {'type': 'boolean', 'description': _("if True, the interface is restarted after setting it. optional, default True")},
                "name": {"type": "string", 'description': _("name of the interface e.g. eth0, required.")},
                "address": {"type": "string", 'description': _("ip4 address.")},
                "source": {"type": "string", 'pattern': '(^static$|^dhcp$)', 'description': _("'dhcp' or 'static', optional, default static.")},
            },
            "defaults": {
                "name": None,
                "address": "",
                "source": "static",
                "restart": True,
            },
        },
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
        'jsonschema': {
            "$schema": "http://json-schema.org/draft-06/schema#",
            "properties": {
                "restart": {'type': 'boolean', 'description': _("if True, the interface is restarted after setting it. optional, default True")},
                "name": {"type": "string", 'description': _("name of the interface e.g. eth0, required.")},
                "address": {"type": "string", 'description': _("ip4 address.")},
                "source": {"type": "string", 'pattern': '(^static$|^dhcp$)', 'description': _("'dhcp' or 'static', optional, default static.")},
            },
            "defaults": {
                "name": None,
                "address": "",
                "source": "static",
                "restart": True,
            },
        },
    },
}
