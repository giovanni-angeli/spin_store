
import jsonschema
from spin_store.settings import ugettext_lazy as _

validate = jsonschema.validate

example_schema = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "properties": {
        "spin":     {'type': 'boolean', 'description': _("the spin")},
        "charge":   {"type": "integer", 'description': _("the electric charge: 1 unit eqals 1/3 of electron's charge")},
        "color":    {"type": "string", 'description': _("the color")},
        "momentum": {"type": "number", 'description': _("the momentum")},
        "ki":       {"type": "array", 'description': _("the ki energy")},
        "do":       {"type": "object", 'description': _("the <b>way</b>")},
        "flavour": {
          "enum": [ "sweet", "bitter", "ginger" ],
          'description': _("tell me which flavour you <b>prefer</b>!")
        },
    },
    "required": ["spin", "charge", "color", "momentum"],
    "defaults": {
        "spin": False,
        "charge": 42,  
        "color":  "white",
        "momentum": 12.34,
        "ki": [1,2],
        "do": {"a":'A','b':list({1,2,3})},
    }
}

gauge_boson_schema = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "properties": {
        "spin":     {'type': 'integer', 'description': _("the spin")},
        "angular momentum": {"type": "number", 'description': _("the momentum")},
        "ki":       {"type": "array", 'description': _("the ki energy")},
        "do":       {"type": "object", 'description': _("the <b>way</b>")},
    },
    "required": ["spin", "charge", "color", "momentum"],
    "defaults": {
        "spin": 0,
        "angular momentum": 0,
        "ki": [1,2],
        "do": {"a":'A','b':list({1,2,3})},
    }
}

COMMAND_JSONSCHEMAS =  {
 'CHECK_MAB_PRESENCE': {'MAB_code': 100, 'visibility': -1,                    # CONTROLLO_PRESENZA_MACCHINA = 100,
    'description': "A dirty-shitty thing to reset the MAB command buffer. This is a legacy diagbehaviour of the MAB's fw",
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 'properties': {}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 'properties': {}}}},
    
 'RESET': {'MAB_code': 101, 'visibility': 3,                                 # RESET_MACCHINA = 101
    'description': 'Forces a machine reset. Puts the machine in stand-by mode',
    'in_params': {
        'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 
            'properties': {
                'mode': {'propertyOrder': 1, 'type': 'number', 'fmt': "B", 'description': "0: Cold reset, 1: Warm reset."}
            }
        },
        'example': {'mode': 0}
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'FW_VERSIONS': {'MAB_code': 113, 
    'visibility': 0, # not to be exposed on bus
    'description': 'ask the info about version of firmware running on the boards  (MAB and slaves)',
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 'properties': {}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},

 'INFO': {'MAB_code': 0xFF00 + 105, # Ugly, ugly, ugly tick to avoid code replication
    'visibility': 0, # not to be exposed on bus
    'description': 'DEPRECATED cmd to ask to the info about version of firmware running on the boards (MAB and slaves)',
    'in_params': {
        'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 
            'properties': { 
                # ~ 'page_nr': {'propertyOrder': 1, 'type': 'number',  'fmt': 'B',},
            }
        },
        # ~ 'example': {'page_nr': 1},
    },        
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},

 'DIAG_GET_LAST_DISPENSATION_PARAMS': {'MAB_code': 172, 
    'expected_answer': 'MACHINE_GET_LAST_DISPENSATION_PARAMS', # not to be exposed on bus
    'visibility': 0, # not to be exposed on bus
    'description': 'cmd to ask the effective params used in last dipensation, ',
    'in_params': {
        'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 
            'properties': { 
                # ~ 'circuit_ids': {'propertyOrder': 1, 'type': 'array',  'fmt': '6s', 'is_index_list': True, 'index_offset': 1},
                'circuit_id': {'propertyOrder': 1, 'type': 'number',  'fmt': 'B',},
            }
        },
        'example': {
            # ~ 'circuit_ids': [16],
            'circuit_id': 16,
        }, 
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},

 'DISPENSATION': {'MAB_code': 104,  'visibility': 1,                         # DISPENSAZIONE_COLORE_MACCHINA = 104
    'description': "Requests a full dispensation cycle directly to the MAB." 
            "CAVEAT: using this command directly, we have no info stored in SQL db, e.g.: no "
            "record added in DispensationQueue table, no update of colorant levels.",
    # ~ 'cycle_step_sequence': [11, 0],
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'in_params': {
        'example': {
            'ingredients':                [[3, 2.0]], 
            'force_negative_discharge':   False, 
            'filling_method':             1, 
            'max_simultaneous_colorants': 4, 
            'ignore_can_presence':        False        
        },
        'jsonschema': {
            '$schema': 'http://json-schema.org/draft-06/schema#',
            'properties': {
                'ingredients':                {'propertyOrder': 1, 'type': 'array'},
                'force_negative_discharge':   {'propertyOrder': 2, 'type': 'boolean', 'fmt': '?',
                    'description': 'Used ONLY in alfakiosk (aka Tester) where there is a specific container for purged material (called negative discharge)'}, 
                'filling_method':             {'propertyOrder': 3, 'type': 'number', 'fmt': "B"},
                'max_simultaneous_colorants': {'propertyOrder': 4, 'type': 'number', 'fmt': "B"},
                'ignore_can_presence':        {'propertyOrder': 5, 'type': 'boolean', 'fmt': '?'},
            },
        },
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'ENTER_DIAGNOSTIC': {'MAB_code': 106, 'visibility': 3,                      # DIAGNOSTICA_MACCHINA = 106
    'description': 'Puts the machine into diagnostic mode',
    'allowed_status_levels': ['IDLE', 'DIAGNOSTIC', 'STANDBY', 'RESET', 'ALARM'], 
    'target_status_levels': ['DIAGNOSTIC',], 
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 'properties': {}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
                  
 'UPDATE_CIRCUIT_CALIBRATION_CURVE': {'MAB_code': 108, 'visibility': 0,      # PAR_CURVA_CALIBRAZIONE_MACCHINA = 108
    'description': 'Updates the calibration curve for a single circuit',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',], 
    'cycle_step_sequence': [2, 0,],
    'cycle_step_failing': [3],
    'timeout': 20,
    # ~ 'time_to_wait': 1.,
    'in_params': {
        'example': {
            'circuit_id':       2,               
            'curve_id':         0,               
            'speed':            50,              
            'algorithm':        "symmetric-continuous", 
            'vol_min':          10.0,             
            'vol_max':          800.0,             
            'enable_back_step': False,           
            'n_step_back_step': 0,               
            'speed_back_step':  0,               
            'points':           [                
                [1, 0.0], 
                [10, 0.0276], 
                [20, 0.0417], 
                [30, 0.0658], 
                [50, 0.1166], 
                [120, 0.2794], 
                [350, 0.8613], 
                [600, 1.4579], 
                [850, 2.0745]
            ],
        },
        'jsonschema': {
            '$schema': 'http://json-schema.org/draft-06/schema#',
            'properties': {
                'circuit_id':       {'propertyOrder': 1, 'type': 'number',  'fmt': 'B'},
                'curve_id':         {'propertyOrder': 2, 'type': 'number',  'fmt': 'B'},
                'speed':            {'propertyOrder': 3, 'type': 'number',  'fmt': 'H'},
                'algorithm':        {'propertyOrder': 4, 'type': 'string',  'fmt': 'B', 'conversion_list': ["single-stroke", "double-stroke", "symmetric-continuous", "asymmetric-continuous"]},
                'vol_min':          {'propertyOrder': 5, 'type': 'number',  'fmt': 'I'},
                'vol_max':          {'propertyOrder': 6, 'type': 'number',  'fmt': 'I'},
                'enable_back_step': {'propertyOrder': 7, 'type': 'boolean', 'fmt': '?'},
                'n_step_back_step': {'propertyOrder': 8, 'type': 'number',  'fmt': 'H'},
                'speed_back_step':  {'propertyOrder': 9, 'type': 'number', 'fmt': 'H'},
                'points':           {'propertyOrder': 10, 'type': 'array'},
            },
        },
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'UPDATE_CIRCUIT_SETTINGS': {'MAB_code': 109, 'visibility': 0,               # PAR_CIRCUITO_COLORANTE_MACCHINA = 109
    'description': 'Updates low-level settings for a single circuit',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',], 
    'cycle_step_sequence': [2, 0],
    'cycle_step_failing': [3],
    'timeout': 20,
    # ~ 'time_to_wait': 5.,
    'in_params': {
        'example': {
            'index'                            :2, 
            'n_steps_stroke'                   :1400, 
            'n_steps_continuous_stop'          :1200, 
            'n_steps_home'                     :300, 
            'n_steps_backlash'                 :600, 
            'delay_EV_off'                     :0, 
            'max_stroke_volume'                :None, 
            'min_continuous_volume'            :10000,
            'suction_speed'                    :200, 
            'recirculation_speed'              :200, 
            'recirculation_duration'           :2, 
            'recirculation_pause'              :20, 
            'stirring_duration'                :30, 
            'stirring_PWM_pct'                 :100, 
            'recirc_cycles_before_dispensing'  :2, 
            'recirc_window'                    :3, 
            'stirring_window'                  :3
        },
        'jsonschema': {
            '$schema': 'http://json-schema.org/draft-06/schema#',
            'properties': {
                'index'                           : {'propertyOrder':  1, 'type': 'number', 'fmt': 'B'},   #(unsigned char )                0x0E,
                'n_steps_stroke'                  : {'propertyOrder':  2, 'type': 'number', 'fmt': 'H'},   #(unsigned short)                0x78,0x05,
                'n_steps_continuous_stop'         : {'propertyOrder':  3, 'type': 'number', 'fmt': 'H'},   #(unsigned short)                0x00,0x00,
                'n_steps_home'                    : {'propertyOrder':  4, 'type': 'number', 'fmt': 'H'},   #(unsigned short)                0x2C,0x01,
                'n_steps_backlash'                : {'propertyOrder':  5, 'type': 'number', 'fmt': 'H'},   #(unsigned short)                0x58,0x1B,
                'delay_EV_off'                    : {'propertyOrder':  6, 'type': 'number', 'fmt': 'H'},   #(unsigned short)                0x32,0x00,
                'max_stroke_volume'               : {'propertyOrder':  7, 'fmt': 'I', 'conversion_factor': 10000},   #(unsigned long )      0x00,0x00,0x00,0x00,
                'min_continuous_volume'           : {'propertyOrder':  8, 'fmt': 'I', 'conversion_factor': 10000},   #(unsigned long )      0x00,0x00,0xE1,0xF5,
                'suction_speed'                   : {'propertyOrder':  9, 'type': 'number', 'fmt': 'H'},   #(unsigned short)                0x05,0x2C,
                'recirculation_speed'             : {'propertyOrder': 10, 'type': 'number', 'fmt': 'H'},   #(unsigned short)                0x01,0xC8,
                'recirculation_duration'          : {'propertyOrder': 11, 'type': 'number', 'fmt': 'B'},   #(unsigned char )                0x00,
                'recirculation_pause'             : {'propertyOrder': 12, 'type': 'number', 'fmt': 'B'},   #(unsigned char )                0x1B,
                'stirring_duration'               : {'propertyOrder': 13, 'type': 'number', 'fmt': 'H'},   #(unsigned short)                0x32,0x14,
                'stirring_PWM_pct'                : {'propertyOrder': 14, 'type': 'number', 'fmt': 'B'},   #(unsigned char )                0x00,
                'recirc_cycles_before_dispensing' : {'propertyOrder': 15, 'type': 'number', 'fmt': 'B'},   #(unsigned char )                0x00,
                'recirc_window'                   : {'propertyOrder': 16, 'type': 'number', 'fmt': 'B'},   #(unsigned char )                0x00,
                'stirring_window'                 : {'propertyOrder': 17, 'type': 'number', 'fmt': 'B'},   #(unsigned char )                0x00,
            },
        }
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'SLAVE_CONFIGURATION': {'MAB_code': 110, 'visibility': 3,                   # PAR_SLAVES_CONFIGURATION = 110
    'description': 'Enable/Disable slaves presence',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [2, 0,],
    'cycle_step_failing': [3],
    'in_params': {
        'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 
            'properties': { 
                'slave_ids': {'propertyOrder': 1, 'type': 'array',  'fmt': '6s', 'is_index_list': True, 'index_offset': 1},
            }
        },
        'example': {'slave_ids': [0, 2, 3, 33, 34, 36]}, 
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'CAN_LIFTER_MOVEMENT': {'MAB_code': 111, 'visibility': 3, 'timeout': 5,     # CAN_LIFTER_MOV = 111
    'description': 'Move can lifter to target position',
    'allowed_status_levels': ['STANDBY',], 
    'target_status_levels': ['STANDBY',],     
    'in_params': {
        'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
            'properties': {
                'target_position': {
                    'propertyOrder': 1, 'type': 'number', 'fmt': 'I', 'conversion_factor': 10000, 
                    'description': "offset in (mm*0.0001). 0 means bottom position, 0xFFFFFFFF means top position"
                },
                'verify_can_presence': {'propertyOrder': 2, 'type': 'boolean', 'fmt': '?'},
                'extra_offset': {
                    'propertyOrder': 3, 'type': 'number', 'fmt': 'I', 'conversion_factor': 10000, 
                    'description': "extra displacement in (mm*0.0001) to move after the upper photosensor has been obscured"
                },
                'extra_offset_speed':  {'propertyOrder': 4, 'type': 'number', 'fmt': 'B', 'description': " ??? PWM % per la velocità bassa ??? "},
            },
        },
        'example': {
            'target_position': 500,   
            'verify_can_presence': True,
            'extra_offset':   0,    
            'extra_offset_speed': 0,
        },
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
        
 'DIAG_WITHDRAWAL_POSITIONING': {'MAB_code': 150, 'visibility': 0,           #  DIAG_POS_STAZIONE_PRELIEVO = 150
    'description': 'Move to withdrawal position',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [1, 0],
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {'container_id': {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'}}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'DIAG_FILLING_POSITIONING': {'MAB_code': 151, 'visibility': 0,              #  DIAG_POS_STAZIONE_RIEMPIMENTO = 151
    'description': 'Move to flling position',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [1, 0],
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {'container_id': {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'}}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'DIAG_CAPPING_POSITIONING': {'MAB_code': 152, 'visibility': 0,              #  DIAG_POS_STAZIONE_TAPPATURA = 152
    'description': 'Move to capping position',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [1, 0],
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {'station_id': {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'}}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'DIAG_DISCHARGE_POSITIONING': {'MAB_code': 153,  'visibility': 0,           #  DIAG_POS_STAZIONE_SCARICO = 153
    'description': 'Move to discharge position',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [1, 0],
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {
            'discharge_type': {'propertyOrder': 2, 'type': 'boolean', 'fmt': '?', 'description': "Discharge type: 0 = NEGATIVE, 1 = POSITIVE"}, 
            'station_id': {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'}
        }}
     },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},

 'DIAG_CAPPING': {'MAB_code': 154, 'visibility': 0,                          #  DIAG_TAPPATURA_COPERCHIO = 154
    'description': 'Execute capping',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
    'properties': {
        'pwm_duty_pct': {'propertyOrder': 2, 'type': 'number', 'fmt': 'B', 'description': "cover PWM duty cycle (unused)"}, 
        'station_id': {'propertyOrder': 1, 'type': 'number', 'fmt': 'B', 'description': "cover ID"}}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'DIAG_CONTAINER_WITHDRAWAL': {'MAB_code': 156, 'visibility': 0,             #  DIAG_PRELIEVO_CONTENITORE = 156
    'description': 'Execute container withdrawal',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {'n_step_rev1': {'propertyOrder': 2, 'type': 'number'},
            'station_id':   {'propertyOrder': 1, 'type': 'number', 'fmt': 'B', 'description': "/* container ID */"},
            'n_step_rev1':  {'propertyOrder': 2, 'type': 'number', 'fmt': 'H', 'description': "/* No steps rev. 1 (unused), 16 bits */"},
            'speed_rev1':   {'propertyOrder': 3, 'type': 'number', 'fmt': 'H', 'description': "/* Speed rev. 1 (unused), 16 bits */"},
            'n_step_rev2':  {'propertyOrder': 4, 'type': 'number', 'fmt': 'H', 'description': "/* No steps rev. 2 (unused), 16 bits */"},
            'speed_rev2':   {'propertyOrder': 5, 'type': 'number', 'fmt': 'H', 'description': "/* Speed rev. 2 (unused), 16 bits */"},   
            'n_step_rev3':  {'propertyOrder': 6, 'type': 'number', 'fmt': 'H', 'description': "/* No steps rev. 3 (unused), 16 bits */"},
            'speed_rev3':   {'propertyOrder': 7, 'type': 'number', 'fmt': 'H', 'description': "/* Speed rev. 3 (unused), 16 bits */"},
            'pause_rev':    {'propertyOrder': 8, 'type': 'number', 'fmt': 'B', 'description': "/* Pause after withdrawal (?) */"}}
        }
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
        
 'DIAG_CONTROL_STIRRING': {'MAB_code': 158,  'visibility': 0,                #  DIAG_ATTIVA_AGITAZIONE_CIRCUITI = 158
    'description': 'Enables/disables paint stirring, Specify circuit_ids as follows: [circuit_id_1, circuit_id_2, ...]',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [1, 0],
    'cycle_step_failing': [3],    
    'timeout': 10,
    'in_params': {
        'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
            'properties': {
                'cycle_command': {'propertyOrder': 1, 'type': 'boolean', 'fmt': '?'},
                'circuit_ids': {'propertyOrder': 2, 'type': 'array', 'is_index_list': True, 'fmt': '4s'}, 
            },
        }
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'DIAG_CONTROL_RECIRCULATION': {'MAB_code': 159, 'visibility': 0,            #  DIAG_ATTIVA_RICIRCOLO_CIRCUITI  = 159
    'description': 'Enables/disables recirculation, Specify circuit_ids as follows: [circuit_id_1, circuit_id_2, ...]',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [1, 0],
    'cycle_step_failing': [3],        
    'timeout': 10,
    'in_params': {
        'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
            'properties': {
                'cycle_command': {'propertyOrder': 1, 'type': 'boolean', 'fmt': '?'},
                'circuit_ids': {'propertyOrder': 2, 'type': 'array', 'is_index_list': True, 'fmt': '4s'}, 
            },
        }
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'DIAG_SETUP_CIRCUIT': {'MAB_code': 161, 'visibility': 0,                    #  DIAG_IMPOSTA_DISPENSAZIONE_CIRCUITI  = 161
    'description': 'Sets parameters up for a single circuit dispensation (diagnostic mode only)',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [1, 0],
    'timeout': 10,
    'in_params': {
        'example': {
            'circuit_id':             14,       # parseInt(params.pipe), //circuit_id
            'n_step_cycle':           1800,     # item.steps,
            'speed_cycle':            0,        # params.speed,
            'algorithm':              0,        # params.algorithm,
            'n_cycles_supply':        0,        # n_cycles_supply 
            'en_back_step':           0,        # params.en_back_step? 1 : 0,
            'n_step_back_step':       0,        # params.n_step_back_step,
            'speed_back_step':        150,      # params.speed_back_step,
            'delay_EV_off':           2400,     # params.delay_ev_off,
            'speed_suction':          1200,     # params.speed_suction,
            'n_step_stroke':          9220,     # params.n_step_stroke,
            'n_step_continuous_end':  9252      # params.n_step_continuous_end
        },
        'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
            'properties': {
                'circuit_id':           {'propertyOrder':  1, 'type': 'number', 'fmt': 'B'}, 
                'n_step_cycle':         {'propertyOrder':  2, 'type': 'number', 'fmt': 'I'}, 
                'speed_cycle':          {'propertyOrder':  3, 'type': 'number', 'fmt': 'H'}, 
                'algorithm':            {'propertyOrder':  4, 'type': 'number', 'fmt': 'B'}, 
                'n_cycles_supply':      {'propertyOrder':  5, 'type': 'number', 'fmt': 'H'}, 
                'en_back_step':         {'propertyOrder':  6, 'type': 'number', 'fmt': 'B'}, 
                'n_step_back_step':     {'propertyOrder':  7, 'type': 'number', 'fmt': 'H'}, 
                'speed_back_step':      {'propertyOrder':  8, 'type': 'number', 'fmt': 'H'}, 
                'delay_EV_off':         {'propertyOrder':  9, 'type': 'number', 'fmt': 'H'}, 
                'speed_suction':        {'propertyOrder': 10, 'type': 'number', 'fmt': 'H'}, 
                'n_step_stroke':        {'propertyOrder': 11, 'type': 'number', 'fmt': 'H'}, 
                'n_step_continuous_end':{'propertyOrder': 12, 'type': 'number', 'fmt': 'H'}, 
            },                                                                                
        }
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'DIAG_SETUP_RECIRCULATION': {'MAB_code': 162, 'visibility': 0,              #  DIAG_IMPOSTA_RICIRCOLO_CIRCUITI = 162
    'description': 'Sets parameters up for a single circuit recirculation',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [1, 0],
    'in_params': {
        'jsonschema': {
            '$schema': 'http://json-schema.org/draft-06/schema#',
            'properties': {
                'circuit_id':           {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'},
                'n_step_cycle':         {'propertyOrder': 2, 'type': 'number', 'fmt': 'H'},
                'speed_cycle':          {'propertyOrder': 3, 'type': 'number', 'fmt': 'H'},
                'n_cycles':             {'propertyOrder': 4, 'type': 'number', 'fmt': 'H'},
                'recirculation_pause':  {'propertyOrder': 5, 'type': 'number', 'fmt': 'H'},
            },
        }                                                                   
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'DIAG_START_CIRCUIT': {'MAB_code': 163, 'visibility': 0,                    #  DIAG_ATTIVA_DISPENSAZIONE_CIRCUITI = 163
    'description': 'Activate single circuit dispensation (diagnostic mode only)',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY'], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [1, 0,],
    'cycle_step_failing': [2],
    'timeout': 60,
    'in_params': {
        'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
            'properties': {
                'cycle_command': {'propertyOrder': 1, 'type': 'boolean', 'fmt': '?'},
                'circuit_ids':   {'propertyOrder': 2, 'type': 'array', 'is_index_list': True, 'fmt': '4s'}, 
            },
        }
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'DIAG_START_AXIS_MOTION': {'MAB_code': 164, 'visibility': 0,                #  DIAG_MOVIMENTAZIONE_ASSE_START = 164
    'description': 'Starts axis movement',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],         
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {
            'motion_axis': {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'},
            'speed_type': {'propertyOrder': 2, 'type': 'number', 'fmt': 'B'},
            'n_steps': {'propertyOrder': 3, 'type': 'number', 'fmt': 'H'},
            'speed': {'propertyOrder': 4, 'type': 'number', 'fmt': 'H'},
            'delay_v_up': {'propertyOrder': 5, 'type': 'number', 'fmt': 'H'},
            'delay_v_down': {'propertyOrder': 6, 'type': 'number', 'fmt': 'H'}}
        }
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'DIAG_STOP_AXIS_MOTION': {'MAB_code': 165, 'visibility': 0,                 #  DIAG_MOVIMENTAZIONE_ASSE_STOP = 165
    'description': 'Stops axis movement',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],         
    'in_params': {
        'jsonschema': {
            '$schema': 'http://json-schema.org/draft-06/schema#', 
            'properties': {'circuit_id': {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'}}, 
        }
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'DIAG_HOME_POSITIONING': {'MAB_code': 166,  'visibility': 0,                #  DIAG_POS_HOME_DA_SCARICO = 166
    'description': 'Moves to home position after discharge',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],         
    'cycle_step_sequence': [1, 0],
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {'discharge_type': {'propertyOrder': 1, 'type': 'boolean', 'fmt': '?'}}}
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'DIAG_SEARCH_HOME_POSITION': {'MAB_code': 167, 'visibility': 0,             #  DIAG_POS_SEARCH_HOMING = 167
    'description': 'Executes the homing procedure on x, y axes',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],         
    'cycle_step_sequence': [1, 0],
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 'properties': {}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
                               
 'DIAG_ADJUST_SINGLE_MOTION': {'MAB_code': 168, 'visibility': 0,             #  DIAG_CALIB_SINGLE_MOVEMENT = 168
    'description': 'Update adjustment parameters for single movements',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],         
    'cycle_step_sequence': [1, 0],
    'in_params': {
        'example': {
            'id_pos': 0x04,              
            'x_offset': 0x0123,          
            'y_offset': 0x89AB,          
        },
        'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
            'properties': {
                'id_pos': {
                    'propertyOrder': 1, 'type': 'number', 'fmt': 'B', 
                    'description': "<br/>".join(["",
                        "1 → POS1: I selettore contenitore   ",
                        "2 → POS2: II selettore contenitore  ",
                        "3 → POS3: III selettore contenitore,",
                        "4 → POS4: IV selettore contenitore, ",
                        "5 → POS5: posizione di erogazione   ",
                        "6 → POS6: I stazione tappatura,     ",
                        "7 → POS7: II stazione tappatura,    ",
                        "8 → POS8: n.u,                      ",
                        "9 → POS9: n.u,,                     ",
                        "10 → POS10: n.u,,                   ",
                        "11 → POSA: n.u,,                    ",
                        "12 → POSB: posizione prima di scendere in erogazione,       ",
                        "13 → POSC: posizione intermedia prima di andare in tappatura",
                        "14 → POSD: posizione per togliersi dall ingombro del perno dopo tappatura 1,",
                        "15 → POSE: posizione per togliersi dall ingombro del perno dopo tappatura 2",
                        "16 → POSF: posizione per scarico positivo,                       ",
                        "17 → POSG: posizione per scarico negativo/fine scarico positivo,",
                        "18 → POSH: posizione fine scarico negativo"
                    ]),
                },                                                                #     (unsigned char)
                'x_offset': {'propertyOrder': 2, 'type': 'number', 'fmt': 'H'},   #     (signed short) 
                'y_offset': {'propertyOrder': 3, 'type': 'number', 'fmt': 'H'}
            },  #     (signed short) 
        }
    },
   'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
           
 'DIAG_MOVE_AUTOCAP': {'MAB_code': 170, 'visibility': 0,                     #  DIAG_MOVIMENTAZIONE_AUTOCAP = 170
    'description': 'Allow to open-close the autocap and to put it in the purge position',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC', 'STANDBY',],              
    'in_params': {
        'jsonschema': {
            '$schema': 'http://json-schema.org/draft-06/schema#', 
            'properties': {
                'target_position': {'propertyOrder': 1, 'type': 'number', 'fmt': 'B', 'description': "0 = close, 1 = purge, 2 = dispense"}
            }, 
        },
        
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'DIAG_VOLUME_DISPENSATION': {'MAB_code': 171, 'visibility': 0,              #  DIAG_DISPENSATION_VOL = 171
    'description': 'Executes a single circuit dispensation with quantity specified in volume',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',], 
    'cycle_step_sequence': [1, 0],
    'cycle_step_failing': [3],    
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {
            'circuit_id': {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'}, 
            'volume_cc': {'propertyOrder': 2, 'type': 'number', 'fmt': 'I', 'conversion_factor': 10000} # (unsigned long )
        }}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'DIAG_SET_EV_CIRCUIT': {'MAB_code': 173, 'visibility': 0,                   #  DIAG_ATTIVA_EV_DISPENSAZIONE = 173
    'description': 'Controls the EV of given circuit',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',], 
    'cycle_step_sequence': [1, 0],
    'in_params': {
        'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
            'properties': {
                'cycle_command': {'propertyOrder': 1, 'type': 'boolean', 'fmt': '?'},
                'circuit_ids': {'propertyOrder': 2, 'type': 'array', 'is_index_list': True, 'fmt': '4s'} 
            }
        }
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'PAR_CAN_LIFTER_SETTINGS': {'MAB_code': 174, 'visibility': 0,               #  DIAG_SET_UP_CAN_LIFTER_PARAM = 174
    'description': 'Set up Can Lifter parameters',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [2, 0,],
    'cycle_step_failing': [3],
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {
            'pulse_to_mm': {'description': 'Encoder Resolution (val x 10000)', 'propertyOrder': 1, 'type': 'number', 'fmt': 'L'},
            'home_pos': {'description': 'Positioning at rest starting from the low position (val x 10000)', 'propertyOrder': 2, 'type': 'number', 'fmt': 'L'},
            'hi_speed': {'description': 'PWM% for High Speed ', 'propertyOrder': 3, 'type': 'number', 'fmt': 'B'},
            'lo_speed': {'description': 'PWM% for Low Speed ', 'propertyOrder': 4, 'type': 'number', 'fmt': 'B'}},
        }
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
      
 'DIAG_RESET_EEPROM': {'MAB_code': 175, 'visibility': 3,                     #  DIAG_RESET_EEPROM = 175
    'description': 'Reset EEprom memory on MAB',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['ALARM',],     
    'cycle_step_failing': [3],
    'timeout': 60,    
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 'properties': {}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
     
 'DIAG_MOVE_CAN_LIFTER': {'MAB_code': 176, 'visibility': 0,                  #  DIAG_MOV_CAN_LIFTER = 176
    'description': 'Starts a Can Lifter movement of a specified distance and direction',    
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {
            'direction': {'description': 'DC motor polarity', 'propertyOrder': 1, 'type': 'number', 'fmt': 'B'}, 
            'distance' : {'description': 'Move from the current position', 'propertyOrder': 2, 'type': 'number', 'fmt': 'H'}},
        }
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
 
 'DIAG_SET_HUMIDIFIER_PERIPHERALS': {'MAB_code': 178, 'visibility': 0,       #  DIAG_SET_HUMIDIFIER_PERIPHERALS = 178
    'description': 'Set up Humidifier 2.0 Peripherals',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [1, 0,],
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {
            'type': {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'},
            'action': {'propertyOrder': 2, 'type': 'number', 'fmt': 'B'}},
        }
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
 
 'DIAG_SETUP_HUMIDIFIER_TEMPERATURE_PROCESSES': {'MAB_code': 179, 'visibility': 0, # DIAG_SETUP_HUMIDIFIER_TEMPERATURE_PROCESSES = 179
    'description': 'Set up Humidifier and Temperature Controlled Erogation parameters.',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [2, 0,],
    'cycle_step_failing': [3],
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {
            'Humidifier_Enable': {'description': 'Boolean - Values: 0 Disable, 1 Enabled', 'propertyOrder': 1, 'type': 'number', 'fmt': '?'},
            'Humidifier_Type': {'description': 'unsigned char - Type of RH sensor, values: 0:SensirionSHT30, 1:...','propertyOrder': 2, 'type': 'number', 'fmt': 'B'},
            'Humidifier_Period': {'description': '2byte - Process period (sec). Default ‘300’','propertyOrder': 3, 'type': 'number', 'fmt': 'H'},
            'Humidifier_Multiplier': {'description': '2byte - Multiplier coefficient (val x 100). 0 <= Values <=  1000. Default ‘100’ (= 1)','propertyOrder': 4, 'type': 'number', 'fmt': 'H'},
            'AutocapOpen_Duration': {'description': '2byte - Nebulizers and Pump Activation Duration (sec) with AUTCAP OPEN', 'propertyOrder': 5, 'type': 'number', 'fmt': 'H'},
            'AutocapOpen_Period': {'description': '2byte - Nebulizers and Pump Activation Period (sec) with AUTCAP OPEN', 'propertyOrder': 6, 'type': 'number', 'fmt': 'H'},
            'Temp_Enable': {'description': 'Boolean - Values: 0 Disable, 1 Enabled','propertyOrder': 7, 'type': 'number', 'fmt': '?'},
            'Temp_Type': {'description': 'unsigned char - Type of Temperature sensor, values: 0:SensirionSHT30, 1:...','propertyOrder': 8, 'type': 'number', 'fmt': 'B'},
            'Temp_Period': {'description': '2byte - Process period (sec). Default ‘300’','propertyOrder': 9, 'type': 'number', 'fmt': 'H'},
            'Temp_T_LOW': {'description': '1byte - ‘LOW’ Temperature threshold value (°C). Default ‘10’','propertyOrder': 10, 'type': 'number', 'fmt': 'B'},
            'Temp_T_HIGH': {'description': '1byte - ‘HIGH’ Temperature threshold value (°C). Default ‘20’','propertyOrder': 11, 'type': 'number', 'fmt': 'B'},
            'Heater_Temp': {'description': '1byte - Heater ON Temperature threshold (°C). Default ‘20’','propertyOrder': 12, 'type': 'number', 'fmt': 'B'},
            'Heater_Hysteresis': {'description': '1byte - Hysteresis Interval on Heater (°C). Default ‘1’','propertyOrder': 13, 'type': 'number', 'fmt': 'B'}},
        }
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'DIAG_SETUP_HUMIDIFIER_PARAMETERS': {'MAB_code': 180, 'visibility': 1,      #  DIAG_SETUP_HUMIDIFIER_PARAMETERS = 180
    'description': 'Set up Humidifier 1.0 parameters ("old" humidifier)',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [2, 0,],
    'cycle_step_failing': [3],
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {
            'autocapopen_duration': {'propertyOrder': 3, 'type': 'number', 'fmt': 'H'},
            'autocapopen_period': {'propertyOrder': 4, 'type': 'number', 'fmt': 'H'},
            'humidifier_duration': {'propertyOrder': 1, 'type': 'number', 'fmt': 'H'},
            'humidifier_period': {'propertyOrder': 2, 'type': 'number', 'fmt': 'H'}}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},

 'DIAG_EEPROM_MANAGEMENT': {'MAB_code': 181, 'visibility': 0,               #  DIAG_EEPROM_MANAGEMENT = 181,
    'description': 'Erase a specific EEprom Sector',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [2, 0,],
    'cycle_step_failing': [3],
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {
            'EEprom_sector': {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'},
            'EEprom_action': {'propertyOrder': 2, 'type': 'number', 'fmt': 'B'}}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
                                                                             
 'DIAG_SETUP_PUMP_TYPE': {'MAB_code': 182, 'visibility': 1,                 # DIAG_SETUP_PUMP_TYPE = 182,
    'description': 'Set Type of Pumps associated withe each circuit',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',], 
    'cycle_step_sequence': [2, 0],
    'cycle_step_failing': [3],
    'timeout': 20,
    # ~ 'time_to_wait': 5.,
    'in_params': {
        'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 
            'properties': { 
                'pump_type0': {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'},
                'pump_type1': {'propertyOrder': 2, 'type': 'number', 'fmt': 'B'},
                'pump_type2': {'propertyOrder': 3, 'type': 'number', 'fmt': 'B'},
                'pump_type3': {'propertyOrder': 4, 'type': 'number', 'fmt': 'B'},
                'pump_type4': {'propertyOrder': 5, 'type': 'number', 'fmt': 'B'},
                'pump_type5': {'propertyOrder': 6, 'type': 'number', 'fmt': 'B'},
                'pump_type6': {'propertyOrder': 7, 'type': 'number', 'fmt': 'B'},
                'pump_type7': {'propertyOrder': 8, 'type': 'number', 'fmt': 'B'},
                'pump_type8': {'propertyOrder': 9, 'type': 'number', 'fmt': 'B'},
                'pump_type9': {'propertyOrder': 10, 'type': 'number', 'fmt': 'B'},
                'pump_type10': {'propertyOrder': 11, 'type': 'number', 'fmt': 'B'},
                'pump_type11': {'propertyOrder': 12, 'type': 'number', 'fmt': 'B'},
                'pump_type12': {'propertyOrder': 13, 'type': 'number', 'fmt': 'B'},
                'pump_type13': {'propertyOrder': 14, 'type': 'number', 'fmt': 'B'},
                'pump_type14': {'propertyOrder': 15, 'type': 'number', 'fmt': 'B'},
                'pump_type15': {'propertyOrder': 16, 'type': 'number', 'fmt': 'B'},
                'pump_type16': {'propertyOrder': 17, 'type': 'number', 'fmt': 'B'},
                'pump_type17': {'propertyOrder': 18, 'type': 'number', 'fmt': 'B'},
                'pump_type18': {'propertyOrder': 19, 'type': 'number', 'fmt': 'B'},
                'pump_type19': {'propertyOrder': 20, 'type': 'number', 'fmt': 'B'},
                'pump_type20': {'propertyOrder': 21, 'type': 'number', 'fmt': 'B'},
                'pump_type21': {'propertyOrder': 22, 'type': 'number', 'fmt': 'B'},
                'pump_type22': {'propertyOrder': 23, 'type': 'number', 'fmt': 'B'},
                'pump_type23': {'propertyOrder': 24, 'type': 'number', 'fmt': 'B'},
                'pump_type24': {'propertyOrder': 25, 'type': 'number', 'fmt': 'B'},
                'pump_type25': {'propertyOrder': 26, 'type': 'number', 'fmt': 'B'},
                'pump_type26': {'propertyOrder': 27, 'type': 'number', 'fmt': 'B'},
                'pump_type27': {'propertyOrder': 28, 'type': 'number', 'fmt': 'B'},
                'pump_type28': {'propertyOrder': 29, 'type': 'number', 'fmt': 'B'},
                'pump_type29': {'propertyOrder': 30, 'type': 'number', 'fmt': 'B'},
                'pump_type30': {'propertyOrder': 31, 'type': 'number', 'fmt': 'B'},
                'pump_type31': {'propertyOrder': 32, 'type': 'number', 'fmt': 'B'},
            }
        }, 
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},                                                                                     

 'DIAG_SETUP_TIMERS': {'MAB_code': 183, 'visibility': 0,                    # DIAG_SETUP_TIMERS = 183,
    'description': 'Set Type of Timers',
    'allowed_status_levels': ['IDLE', 'DIAGNOSTIC', 'STANDBY', 'RESET', 'ALARM'], 
    'in_params': {
        'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 
            'properties': { 
                'timer_type':  {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'},
                'timer_value': {'propertyOrder': 2, 'type': 'number', 'fmt': 'I'},
            }
        }, 
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},                                                                                     

 'DIAG_SETUP_SENSORS': {'MAB_code': 192, 'visibility': 0,                    # DIAG_SETUP_SENSORS = 192,
    'description': 'Enable / Disable Sensor Specified',
    'allowed_status_levels': ['IDLE', 'DIAGNOSTIC', 'STANDBY', 'RESET', 'ALARM'], 
    'in_params': {
        'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 
            'properties': { 
                'sensor_type':  {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'},
                'sensor_enable': {'propertyOrder': 2, 'type': 'number', 'fmt': 'B'},
            }
        }, 
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},                                                                                     

 'DIAG_ROTATING_TABLE_POSITIONING': {'MAB_code': 185, 'visibility': 5,      #  DIAG_ROTATING_TABLE_POSITIONING  = 185,
    'description': 'Rg table to a specific circuit with eventually a further rotation angle for refilling',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {
            'Id_color_circuit': {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'},
            'Refilling_angle':  {'propertyOrder': 2, 'type': 'number', 'fmt': 'H'},
            'Direction':        {'propertyOrder': 3, 'type': 'number', 'fmt': '?'}}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},

 'DIAG_ROTATING_TABLE_STEPS_POSITIONING': {'MAB_code': 191, 'visibility': 2,      #  DIAG_ROTATING_TABLE_STEPS_POSITIONING = 191,
    'description': 'Rotating table to a specific steps number',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [1, 0,],
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {
            'Rotation_Type': {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'},
            'Steps_N':       {'propertyOrder': 2, 'type': 'number', 'fmt': 'H'},
            'Direction':     {'propertyOrder': 3, 'type': 'number', 'fmt': '?'}}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},
    
 'DIAG_ROTATING_TABLE_SEARCH_POSITION_REFERENCE': {'MAB_code': 186, 'visibility': 2,      #  DIAG_ROTATING_TABLE_SEARCH_POSITION_REFERENCE = 186,
    'description': 'Rotating table towards reference position',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [1, 0,],
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 'properties': {}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},

 'ROTATING_TABLE_FIND_CIRCUITS_POSITION': {'MAB_code': 112, 'visibility': 2,      #  ROTATING_TABLE_FIND_CIRCUITS_POSITION = 112,
    'description': 'Find circuits position on Rotating Table',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [1, 0,],
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 'properties': {}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},

 'DIAG_ROTATING_TABLE_TEST': {'MAB_code': 190, 'visibility': 2,      #  ROTATING_TABLE_FIND_CIRCUITS_POSITION = 190,
    'description': 'Rotating table circuits position test',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [1, 0,],
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 'properties': {}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},

 'DIAG_COLORANT_CLEANING_SETTINGS': {'MAB_code': 187, 'visibility': 1,      #  DIAG_COLORANT_CLEANING_SETTINGS = 187,
    'description': 'Set up colorant Cleaning parameters on Rotating table',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [2, 0],
    'cycle_step_failing': [3],
    'timeout': 20,
    # ~ 'time_to_wait': 5.,    
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {
            'Id_color_circuit': {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'},
            'Cleaning_duration':{'propertyOrder': 2, 'type': 'number', 'fmt': 'H'},
            'Cleaning_pause':   {'propertyOrder': 3, 'type': 'number', 'fmt': 'H'}}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},

 'DIAG_COLORANT_ACTIVATION_CLEANING': {'MAB_code': 188, 'visibility': 2,     #  DIAG_COLORANT_ACTIVATION_CLEANING = 188,
    'description': 'Cleaning on/off activation of a specific circuit',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [1, 0],
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {
            'command':          {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'},            
            'Id_color_circuit': {'propertyOrder': 2, 'type': 'number', 'fmt': 'B'}}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},

 'DIAG_SET_TINTING_PERIPHERALS': {'MAB_code': 189, 'visibility': 2,     #  DIAG_SET_TINTING_PERIPHERALS  = 189,
    'description': 'Tinting peripheral on/off activation',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',],     
    'cycle_step_sequence': [1, 0],
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#',
        'properties': {
            'Type':   {'propertyOrder': 1, 'type': 'number', 'fmt': 'B'},            
            'Action': {'propertyOrder': 2, 'type': 'number', 'fmt': 'B'}}}},
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},


 'UPDATE_TINTING_PUMP_SETTINGS': {'MAB_code': 116, 'visibility': 1,     # UPDATE_TINTING_ PUMP_SETTINGS  = 116,
    'description': 'Update Tinting Pump parameters',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',], 
    'cycle_step_sequence': [2, 0],
    'cycle_step_failing': [3],
    'timeout': 20,
    # ~ 'time_to_wait': 5.,
    'in_params': {
        'example': {
            'Step_coupling'                    :2176, 
            'Step_engage'                      :482, 
            'Step_recovery'                    :248, 
            'Step_nut'                         :3110, 
            'Step_support_bellows'             :3200, 
            'Speed_coupling'                   :100, 
            'Speed_engage'                     :50, 
            'Speed_support_bellows'            :300,
            'Step_Valve_Open'                  :148, 
            'Step_Valve_Backstep'              :74, 
            'Speed_valve'                      :10,                                                 
            'N_steps_stroke'                   :1600, 
            'N_step_Backstep'                  :40, 
            'Speed_Backstep'                   :100, 
        },
        'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 
            'properties': { 
                'Step_coupling':  {'propertyOrder': 1, 'type': 'number', 'fmt': 'H'},
                'Step_engage':    {'propertyOrder': 2, 'type': 'number', 'fmt': 'H'},
                'Step_recovery':  {'propertyOrder': 3, 'type': 'number', 'fmt': 'H'},
                'Step_nut':       {'propertyOrder': 4, 'type': 'number', 'fmt': 'H'},
                'Step_support_bellows':  {'propertyOrder': 5, 'type': 'number', 'fmt': 'H'},
                'Speed_coupling': {'propertyOrder': 6, 'type': 'number', 'fmt': 'H'},
                'Speed_engage':   {'propertyOrder': 7, 'type': 'number', 'fmt': 'H'},
                'Speed_support_bellows': {'propertyOrder': 8, 'type': 'number', 'fmt': 'H'},
                'Step_Valve_Open':{'propertyOrder': 9, 'type': 'number', 'fmt': 'H'},
                'Step_Valve_Backstep':   {'propertyOrder': 10, 'type': 'number', 'fmt': 'H'},
                'Speed_valve':    {'propertyOrder': 11, 'type': 'number', 'fmt': 'H'},
                'N_steps_stroke' :{'propertyOrder': 12, 'type': 'number', 'fmt': 'H'},
                'N_step_Backstep':{'propertyOrder': 13, 'type': 'number', 'fmt': 'H'},
                'Speed_Backstep': {'propertyOrder': 14, 'type': 'number', 'fmt': 'H'},
            }
        }, 
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},                                                                                     

 'UPDATE_TINTING_TABLE_SETTINGS': {'MAB_code': 114, 'visibility': 1,    # UPDATE_TINTING_TABLE_SETTINGS  = 114,
    'description': 'Update Tinting Table parameters',
    'allowed_status_levels': ['DIAGNOSTIC', 'STANDBY',], 
    'target_status_levels': ['DIAGNOSTIC',], 
    'cycle_step_sequence': [2, 0],
    'cycle_step_failing': [3],
    'timeout': 20,
    # ~ 'time_to_wait': 5.,
    'in_params': {
        'example': {
            'Step_revolution'                  :6342, 
            'Step_tolerance_revolution'        :20, 
            'Step_reference'                   :42, 
            'Step_tolerance_reference'         :2, 
            'Step_circuit'                     :18, 
            'Step_tolerance_circuit'           :2, 
            'High_speed_rotating_table'        :200, 
            'Low_speed_rotating_table'         :20,
            'Steps_cleaning'                   :1000, 
        },
        'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 
            'properties': { 
                'Step_revolution':           {'propertyOrder': 1, 'type': 'number', 'fmt': 'H'},
                'Step_tolerance_revolution': {'propertyOrder': 2, 'type': 'number', 'fmt': 'H'},
                'Step_reference':            {'propertyOrder': 3, 'type': 'number', 'fmt': 'H'},
                'Step_tolerance_reference':  {'propertyOrder': 4, 'type': 'number', 'fmt': 'H'},
                'Step_circuit':              {'propertyOrder': 5, 'type': 'number', 'fmt': 'H'},
                'Step_tolerance_circuit':    {'propertyOrder': 6, 'type': 'number', 'fmt': 'H'},
                'High_speed_rotating_table': {'propertyOrder': 7, 'type': 'number', 'fmt': 'H'},
                'Low_speed_rotating_table':  {'propertyOrder': 8, 'type': 'number', 'fmt': 'H'},
                'Steps_cleaning':            {'propertyOrder': 9, 'type': 'number', 'fmt': 'H'},
            }
        }, 
    },
    'out_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#'}}},                                                                                     

         
 'MACHINE_STATUS': {'MAB_code': 200,                                        # STATO_MACCHINA = 200
    'comm_bus_db_expire_time_sec': 3,
    'direction': "MAB2MGB",
    'description': """This is the message that the MAB sends to the MGB, carrying all of the details about the status of the MAB.""",
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 'properties': {}}},
    'out_params': {
        'example': {
            'status_level'              : 'STANDBY',
            'cycle_step'                : 0x09,
            'protocol_version'          : 0x00,   
            'error_code'                : 0x00,   
            'cover_reserve'             : [], 
            'cover_availability'        : [],
            'cover_enabled'             : [], 
            'container_reserve'         : [],
            'container_availability'    : [],
            'container_enabled'         : [],
            'color_reserve'             : [],
            'container_presence'        : False,
            'autocap_status'            : False,
            'canlift_status'            : False,
            'doors_status'              : True,
            'clamp_position'            : 0x00, # "POS0",
            'recirculation_status'      : [9, 10, 12, 18], 
            'stirring_status'           : [],
            'slave_status'              : [9, 10, 12, 18],
            'can_on_plate'              : True,
            'can_lifter_current_height' : 249.0,
            'can_lifter_range'          : 400.0,
            'current_temperature'       : 25.1,
            'current_rel_humidity'      : 82.1,
            'water_level'               : False,
            'critical_temperature'      : False,
            'temperature'               : 25.1,
            'bases_carriage'            : False,
            'circuit_engaged'           : 0x0A,
            'table_steps_position'      : 0x0BB8,
            'table_cleaning_status'     : [0, 2, 3, 4],
            'panel_table_status'        : True,
        },
        'jsonschema': {
            '$schema': 'http://json-schema.org/draft-06/schema#',
            'properties': {
                # ~ 'cycle_step'             : {"type": "string", "propertyOrder":  2, 'fmt': 'B', 'conversion_list': ['INIT', 'CONTAINER', 'TO_FILLING', 'FILLING_L1', 'FILLING_L2', 'FILLING_L3', 'CAPPING', 'NEGATIVE_DISCHARGE', 'DISCARGE', 'COMPLETION']}, 
                # ~ 'protocol_version'       : {"type": "number", "propertyOrder":  3, 'fmt': 'B'}, 
                # ~ 'error_code'             : {"type": "number", "propertyOrder":  4, 'fmt': 'B'}, 
                # ~ enum {
                  # ~ /* 0 */ POWER_OFF_ST,
                  # ~ /* 1 */ INIT_ST,
                  # ~ /* 2 */ IDLE_ST,
                  # ~ /* 3 */ RESET_ST,
                  # ~ /* 4 */ COLOR_RECIRC_ST,
                  # ~ /* 5 */ COLOR_SUPPLY_ST,
                  # ~ /* 6 */ ALARM_ST,
                  # ~ /* 7 */ DIAGNOSTIC_ST,
                  # ~ /* 8 */ POSITIONING_ST,
                  # ~ /* 9 */ JUMP_TO_BOOT_ST,
                  # ~ /* 10*/ ROTATING_ST,
                  # ~ /* 11*/ N_STATUS
                # ~ };
                'status_level'              : {"type": "string" , "propertyOrder":  1, 'fmt': 'B', 'conversion_list': ['POWER_OFF', 'INIT', 'IDLE', 'RESET', 'STANDBY', 'DISPENSING', 'ALARM', 'DIAGNOSTIC', 'POSITIONING', 'JUMP_TO_BOOT_ST', 'ROTATING_ST']}, 
                'cycle_step'                : {"type": "number" , "propertyOrder":  2, 'fmt': 'B'}, 
                'error_code'                : {"type": "number" , "propertyOrder":  3, 'fmt': 'H'}, 
                'cover_reserve'             : {"type": "array"  , "propertyOrder":  4, 'fmt': '1s', 'is_index_list': True}, 
                'cover_availability'        : {"type": "array"  , "propertyOrder":  5, 'fmt': '1s', 'is_index_list': True}, 
                'cover_enabled'             : {"type": "array"  , "propertyOrder":  6, 'fmt': '1s', 'is_index_list': True}, 
                'container_reserve'         : {"type": "array"  , "propertyOrder":  7, 'fmt': '1s', 'is_index_list': True}, 
                'container_availability'    : {"type": "array"  , "propertyOrder":  8, 'fmt': '1s', 'is_index_list': True}, 
                'container_enabled'         : {"type": "array"  , "propertyOrder":  9, 'fmt': '1s', 'is_index_list': True}, 
                'color_reserve'             : {"type": "array"  , "propertyOrder": 10, 'fmt': '4s', 'is_index_list': True},  
                'container_presence'        : {"type": "boolean", "propertyOrder": 11, 'fmt': '?', 'description': "0: NOT present, 1: present"},
                'autocap_status'            : {"type": "boolean", "propertyOrder": 12, 'fmt': '?', 'description': "0: closed, 1: open"}, 
                'canlift_status'            : {"type": "boolean", "propertyOrder": 13, 'fmt': '?', 'description': "0: canlift NOT extended, 1: canlift extended"}, 
                'doors_status'              : {"type": "boolean", "propertyOrder": 14, 'fmt': '?', 'description': "0: closed, 1: open"},
                'clamp_position'            : {"type": "number" , "propertyOrder": 15, 'fmt': 'B', 'description': "meaningful only for Color Tester"},  
                'recirculation_status'      : {"type": "array"  , "propertyOrder": 16, 'fmt': '4s', 'is_index_list': True, 'description': "list of recirculating slave boards"}, 
                'stirring_status'           : {"type": "array"  , "propertyOrder": 17, 'fmt': '4s', 'is_index_list': True, 'description': "list of slave boards in stirring mode"}, 
                'slave_status'              : {"type": "array"  , "propertyOrder": 18, 'fmt': '6s', 'is_index_list': True, 'description': "list of active slave boards"},  
                'can_on_plate'              : {"type": "boolean", "propertyOrder": 19, 'fmt': '?', 'description': "0: can is NOT on plate, 1:can is on plate"},
                'can_lifter_current_height' : {"type": "number" , "propertyOrder": 20, 'fmt': 'I', 'conversion_factor': 1./10000,'description': "current position (height) in mm"}, 
                'can_lifter_range'          : {"type": "number" , "propertyOrder": 21, 'fmt': 'I', 'conversion_factor': 1./10000, 'description': "maximum extension ('position low'-'position high') calculated during Reset, in mm"}, 
                'current_temperature'       : {"type": "number" , "propertyOrder": 22, 'fmt': 'H', 'conversion_factor': 0.1, 'description': "T°C. If not configured: ‘3276.7’"},
                'current_rel_humidity'      : {"type": "number" , "propertyOrder": 23, 'fmt': 'H', 'conversion_factor': 0.1, 'description': "RH%. If not configured: ‘3276.7’"},
                'water_level'               : {"type": "boolean", "propertyOrder": 24, 'fmt': '?', 'description': "0: above minimal threshold (OK), 1:below minimal threshold (NOT OK)"},
                'critical_temperature'      : {"type": "boolean", "propertyOrder": 25, 'fmt': '?', 'description': "0: below critical threshold (OK), 1:above critical threshold (NOT OK)"}, 
                'temperature'               : {"type": "number" , "propertyOrder": 26, 'fmt': 'H', 'conversion_factor': 0.1, 'description': "T°C. If not configured: ‘3276.7’"},
                'bases_carriage'            : {"type": "boolean", "propertyOrder": 27, 'fmt': '?', 'description': "0: bases carriage inside, 1: bases carriage extracted (NOT OK)"},
                'circuit_engaged'           : {"type": "number",  "propertyOrder": 28, 'fmt': 'B', 'description': "circuit engaged on rotating table"},
                'table_steps_position'      : {"type": "number",  "propertyOrder": 29, 'fmt': 'I', 'description': "rotating table steps position with respect to reference"},
                'table_cleaning_status'     : {"type": "array",   "propertyOrder": 30, 'fmt': '4s', 'is_index_list': True, 'description': "list of cleaning colorants on rotating table"},
                'panel_table_status'        : {"type": "boolean", "propertyOrder": 31, 'fmt': '?', 'description': "0: table panel inside, 1: table panel open (NOT OK)"},
            }}}},
 'MACHINE_GET_LAST_DISPENSATION_PARAMS': {'MAB_code': 201,                  # MACHINE_GET_LAST_DISPENSATION_PARAMS 201                             
    'direction': "MAB2MGB",
    'description': 'This is the message that the MAB sends to the MGB, carrying info parameters of the last dispensation a pipe made.',
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 'properties': {}}},
    'out_params': {
        'example': {
            'circuit_id'    : 10,
            'n_step_cycle'  : 740,
            'speed_cycle'   : 200,
            'n_cycles'      : 10,
        },
        'jsonschema': {
            '$schema': 'http://json-schema.org/draft-06/schema#',
            'properties': {
                'circuit_id'    : {"type": "number", "propertyOrder":  1, 'fmt': 'B'}, 
                'n_step_cycle'  : {"type": "number", "propertyOrder":  2, 'fmt': 'I'}, 
                'speed_cycle'   : {"type": "number", "propertyOrder":  3, 'fmt': 'H'}, 
                'n_cycles'      : {"type": "number", "propertyOrder":  4, 'fmt': 'H'}, 
            }}}},
 'MACHINE_INFO': {'MAB_code': 105,                                          # MACHINE INFO 105                              
    'direction': "MAB2MGB",
    'description': 'This is the DEPRECATED message that the MAB sends to the MGB, carrying info about FW '
            'version running on the MAB and its slaves. It is paginated, there are 4 pages.'
            'THIS PACKET BREAKS THE PROTOCOL, SO IT IS SCHEMALESS. It is handled by a handler ad hoc.',
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 'properties': {}}},
    'out_params': {
        'example': {},
        'jsonschema': {
            '$schema': 'http://json-schema.org/draft-06/schema#',
            'properties': {}}}},
 'MACHINE_FW_VERSIONS': {'MAB_code': 213,                                   # MACHINE FW VERSION 213                              
    'direction': "MAB2MGB",
    'description': 'This is the message that the MAB sends to the MGB, carrying info about FW version running on the MAB and its slaves',
    'in_params': {'jsonschema': {'$schema': 'http://json-schema.org/draft-06/schema#', 'properties': {}}},
    'out_params': {
        'example': {
            "MAB_MGB_protocol": 0x01,
            "master"          : 0x010203,
            "slaves"          : [ 0x010203 for i in range(48) ],
        },
        'jsonschema': {
            '$schema': 'http://json-schema.org/draft-06/schema#',
            'properties': {
                "MAB_MGB_protocol": {"type": "number", "propertyOrder":  1, 'fmt': '1s'}, 
                "master"          : {"type": "number", "propertyOrder":  2, 'fmt': '3s'}, 
                "slaves"          : {"type": "array",   "propertyOrder":  3, 'fmt': '144s', 'description': "a sequence of 3*48 bytes coding the 3-bytes fw version running on the 48 slave boards."}, 
            }}}},
}

QUANTUMFIELD_JSONSCHEMAS = {
    'Generic': {
        'description': _("Generic's params"),
        'visibility': 1,
        'jsonschema': example_schema,
    },
    'Quark': {
        'description': _("Quark's params"),
        'visibility': 1,
        'jsonschema': example_schema,
    },
    'Lepton': {
        'description': _("Lepton's params"),
        'visibility': 1,
        'jsonschema': example_schema,
    },
    'ScalarBoson': {
        'description': _("ScalarBoson's params"),
        'visibility': 1,
        'jsonschema': example_schema,
    },
    'GaugeBoson': {
        'description': _("GaugeBoson's params"),
        'visibility': 1,
        'jsonschema': gauge_boson_schema,
    },
}
