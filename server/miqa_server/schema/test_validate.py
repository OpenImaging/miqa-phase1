import json
import os
import sys

from jsonschema import validate

from data_import import schema


if len(sys.argv) != 2:
    print('ERROR: Expects a single command line argument (absolute path to json file)')
    sys.exit(1)

json_file_path = sys.argv[1]
with open(json_file_path) as fd:
    json_data_object = json.load(fd)

print(json_data_object)
print('\n\nvalidating...\n\n')

validate(json_data_object, schema)
