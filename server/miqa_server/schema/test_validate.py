import json
import os
import sys

from jsonschema import validate
from jsonschema.exceptions import ValidationError as JSONValidationError

from data_import import schema


if len(sys.argv) != 2:
    print('ERROR: Expects a single command line argument (absolute path to json file)')
    sys.exit(1)

json_file_path = sys.argv[1]
with open(json_file_path) as fd:
    json_data_object = json.load(fd)

print(json_data_object)
print('\n\nvalidating...\n\n')

try:
    valid_object = validate(json_data_object, schema)
    print(valid_object)
except JSONValidationError as inst:
    print('Damn: {0}'.format(inst.message))
    print(dir(inst))