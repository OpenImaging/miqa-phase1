
properties = {
    'data_root': {'type': 'string'},
    'sites': {
        'type': 'array',
        'items': {
            'type': 'object',
            'additionalProperties': False,
            'required': ['id'],
            'properties': {
                'id': {'type': 'string'},
            },
        },
    },
    'experiments': {
        'type': 'array',
        'items': {
            'type': 'object',
            'additionalProperties': False,
            'required': ['id'],
            'properties': {
                'id': {'type': 'string'},
                'note': {'type': 'string'},
            },
        },
    },
    'scans': {
        'type': 'array',
        'items': {
            'type': 'object',
            'additionalProperties': False,
            'required': [],
            'properties': {
                'experiment_id': {'type': 'string'},
                'site_id': {'type': 'string'},
                'path': {'type': 'string'},
                'images': {
                    'type': 'array',
                    'items': {'type': 'string'}
                },
                'id': {'type': 'string'},
                'type': {'type': 'string'},
                'decision': {'type': 'string'},
                'note': {'type': 'string'},
                'user_fields': {
                    'type': 'object',
                    'additional_properties': True,
                    'required': [],
                    r'\w.*': {'type': 'string'},
                },
            },
        },
    },
}

schema = {
    '$schema': 'http://json-schema.org/schema#',
    'title': 'MIQA data import schema',
    'type': 'object',
    'additionalProperties': False,
    'properties': properties,
}
