# -*- coding: utf-8 -*-

import re
import os
import json
from string import Template
import configparser

# Read config

config = configparser.ConfigParser()
config.optionxform = str
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

flow_json_dir = config['Directory']['CLASSIFIED_DIR']
template_dir = config['Directory']['TEMPLATE_DIR']
config_json_dir = config['Directory']['CONFIG_JSON_DIR']
output_dir = config['Directory']['OUTPUT_DIR']

# Main Code

class HTMLTemplate(Template):
    delimiter = '{%'
    pattern = r'''
    \{%(?:
      (?P<escaped>$^) |   # Escape nothing
      \ *(?P<named>[_a-z][_a-z0-9]*)\ *%\}      |   # delimiter and a Python identifier
      \b\B(?P<braced>[_a-z][_a-z0-9]*)   |   # disable braced identifier
      (?P<invalid>)              # Other ill-formed delimiter exprs
    )
    '''

def get_gradate_color(val: int) -> list:
    ret = [0 for _ in range(3)]
    if val < 50:
        ret[0] = round(0x29 + (0xff - 0x29) * max(val, 0) / 50)
    else:
        ret[0] = 0xff
    if val > 50:
        ret[1] = round(0xff - (0xff - 0x29) * min(val - 50, 50) / 50)
    else:
        ret[1] = 0xff
    ret[2] = 0x29
    return ret

def get_color(val: int) -> list:
    if val < 20:
        return [0x29, 0xff, 0x29]
    elif val < 60:
        return [0xff, 0xff, 0x29]
    else:
        return [0xff, 0x29, 0x29]

# Read JSONs

with open(os.path.join(flow_json_dir, 'flow_avg.json'), 'r') as f:
    jsonstr = f.read()
flow_data = json.loads(jsonstr)

with open(os.path.join(flow_json_dir, 'flow_avg_port.json'), 'r') as f:
    jsonstr = f.read()
flow_port_data = json.loads(jsonstr)

with open(os.path.join(config_json_dir, 'relations.json'), 'r') as f:
    jsonstr = f.read()
relation = json.loads(jsonstr)

with open(os.path.join(config_json_dir, 'coordinates.json'), 'r') as f:
    jsonstr = f.read()
coordinates = json.loads(jsonstr)

# Read HTML templates

with open(os.path.join(template_dir, 'floor.template'), 'r') as f:
    html_template = f.read()
floor = HTMLTemplate(html_template)

with open(os.path.join(template_dir, 'floor_partial.template'), 'r') as f:
    html_template = f.read()
floor_partial = HTMLTemplate(html_template)

with open(os.path.join(template_dir, 'port_partial.template'), 'r') as f:
    html_template = f.read()
port_partial = HTMLTemplate(html_template)

with open(os.path.join(template_dir, 'building.template'), 'r', encoding = 'utf-8') as f:
    html_template = f.read()
html = HTMLTemplate(html_template)

# Fill in data

for i in flow_data:
    total = mx = 0

    if i == 'time_stamp':
        continue

    floor_data = ""
    port_data = ""

    for j in range(len(flow_data[i]) + 5, 0, -1):

        if f'{j}F' not in flow_data[i]:
            continue

        floor_current = flow_data[i][f'{j}F']['current']
        floor_mx = flow_data[i][f'{j}F']['max']

        r, g, b = get_color(floor_current / floor_mx * 100)
        floor_data += floor_partial.substitute(floor = f'{j}F', hex_color = f'{r:02x}{g:02x}{b:02x}') + "\n"

        total += floor_current
        mx += floor_mx

    for j in flow_port_data[i]:

        port_current = flow_port_data[i][j]['current']
        port_mx = flow_port_data[i][j]['max']

        if port_mx < 1000:
            port_mx_show = round(port_mx / 1000, 3)
        elif port_mx < 10000:
            port_mx_show = round(port_mx / 1000, 2)
        else:
            port_mx_show = round(port_mx / 1000, 1)

        percentage = port_current / port_mx * 100
        r, g, b = get_color(percentage)
        port_data += port_partial.substitute(port = j, percentage = round(percentage, 2), port_mx = port_mx_show, hex_color = f'{r:02x}{g:02x}{b:02x}') + "\n"

    avg = total / mx * 100
    avg = total / mx * 100
    r, g, b = get_color(avg)

    floor_popup = floor.substitute(dorm_name = relation[i], port_data = port_data[:-1], floor_data = floor_data[:-1])

    with open(os.path.join(output_dir, f'{i}.ejs'), 'w', encoding = 'utf-8') as f:
        f.write(html.substitute(dorm_name = i, percentage = round(avg, 2), total = round(total / 1000, 3), mx = round(mx / 1000, 3), timestamp = flow_data['time_stamp'], coordinates = coordinates[i], hex_color = f'{r:02x}{g:02x}{b:02x}', popup = floor_popup))
