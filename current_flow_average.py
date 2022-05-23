import csv
import glob
import json
import os
import re
import datetime
from bs4 import BeautifulSoup
import configparser


building = {}
OID = 0
FLOOR = 2

config = configparser.ConfigParser()
config.optionxform = str

WORKDIR = os.path.dirname(__file__)
config.read(os.path.join(WORKDIR, 'config.ini'))

IPs = dict(config['IP'])

HTML_DIR = config['Directory']['HTML_DIR']

CLASSIFIED_DIR = config['Directory']['CLASSIFIED_DIR']
CSV_DIR = config['Directory']['CSV_DIR']

csv_list = glob.glob(os.path.join(CSV_DIR, '*.csv'))



SCALE = 1024

for filename in csv_list:
    with open(filename, newline='', encoding = 'cp950') as fp:

        building_name = filename.split('/')[5].split('.')[0]
        if building_name not in building:
            building[building_name] = {}

        # ignore the first line
        next(fp)
        rows = csv.reader(fp)
        for row in rows:
            if (row[FLOOR]+'F' not in building[building_name]) and (row[FLOOR] != ''):
                building[building_name][row[FLOOR]+'F'] = []

            if row[FLOOR] != '':
                html_name = IPs[building_name] + '_' + row[OID].lower().replace('/', '_') + '.html'
                building[building_name][row[FLOOR]+'F'].append(html_name)

# write to json            
with open(os.path.join(CLASSIFIED_DIR, "buildings.json"), "w") as output:
    output.write(json.dumps(building, indent=2))

flow_avg = {}
flow_avg_port = {}

for building_name in building:
    if building_name not in flow_avg:
        flow_avg[building_name] = {}

    if building_name not in flow_avg_port:
        flow_avg_port[building_name] = {}

    for floor in building[building_name]:
        flow_avg[building_name][floor] = {}
        flow_avg[building_name][floor]["current"] = 0
        flow_avg[building_name][floor]["max"] = 0

        for html_file in building[building_name][floor]:

            port_id = html_file.split('.html')[0]
            try:
                fp = open(os.path.join(HTML_DIR, html_file))
            except Exception as e:  
                print(e)
                continue
            soup = BeautifulSoup(fp, 'html.parser')
            parent = soup.find('img', title='day').parent
            trs = parent.find_all('tr', class_=re.compile('in|out'))   

            daily_sum_interface = 0
            flow_avg_port[building_name][port_id] = {}
            flow_avg_port[building_name][port_id]["current"] = 0
            flow_avg_port[building_name][port_id]["max"] = 0

            # sum current in and out flow
            for tr in trs:
                current_text = tr.find_all('td')[2].text
                flow = float(current_text[0:current_text.find(" ")])
                unit = current_text[current_text.find(" ")+1:current_text.find("/")]

                # current flow unit: kB
                if unit.upper() == 'B':
                    flow /= SCALE
                elif unit.upper() == 'MB':
                    flow *= SCALE
                daily_sum_interface += flow

            flow_avg[building_name][floor]["current"] += daily_sum_interface
            flow_avg_port[building_name][port_id]["current"] += daily_sum_interface

            # sum max flow data
            max_flow = soup.find('td', text='Max Speed:').find_next_sibling('td').text
            unit = max_flow[max_flow.find(" ")+1:max_flow.find("y")]
            max_flow = float(max_flow[0:max_flow.find(" ")])

            if unit.upper() == 'MB':
                max_flow *= SCALE
            elif unit.upper() == 'B':
                max_flow /= SCALE
            # need to check if unit is correct
            # max flow unit: kB
            flow_avg[building_name][floor]["max"] += max_flow
            flow_avg_port[building_name][port_id]["max"] += max_flow 

dt = datetime.datetime.today()
flow_avg['time_stamp'] = dt.strftime('%Y/%m/%d %H:%M:%S')
flow_avg_port['time_stamp'] = dt.strftime('%Y/%m/%d %H:%M:%S')

# sort by building name
flow_avg = dict(sorted(flow_avg.items()))
flow_avg_port = dict(sorted(flow_avg_port.items()))

# sort the floor in buildings
for bn in flow_avg:
    if(bn == 'time_stamp'):
        continue
    flow_avg[bn] = dict(sorted(flow_avg[bn].items(), key=lambda x : int(x[0].split('F')[0])))

for bn in flow_avg_port:
    if(bn == 'time_stamp'):
        continue
    flow_avg_port[bn] = dict(sorted(flow_avg_port[bn].items(), key=lambda x : x[0]))

with open(os.path.join(CLASSIFIED_DIR, 'flow_avg.json'), 'w') as output:
    output.write(json.dumps(flow_avg, indent=2))

with open(os.path.join(CLASSIFIED_DIR, 'flow_avg_port.json'), 'w') as output:
    output.write(json.dumps(flow_avg_port, indent=2))
