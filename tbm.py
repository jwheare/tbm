#!/usr/bin/env python

import json
import random
import re
import datetime

# curl -H "X-Requested-With:XMLHttpRequest" http://www.crossrail.co.uk/near-you/geoserver/get-tbms

data = json.load(open('tbm.json'))

def greet_phrase():
    now = datetime.datetime.now()
    if now.hour > 7 and (now.hour < 12 and now.minute < 45):
        return random.choice(['Good morning', 'Morning', 'Hullo', 'Hi', 'Hey'])
    elif now.hour > 17 and now.hour < 23:
        return random.choice(['Good evening', 'Evening', 'Hello', 'Hi there', 'Hi'])
    else:
        return random.choice(['Hello', 'Hi', 'Hey'])


greetings = [
    '{phrase}, {{name}} here! ',
    '{phrase}, it\'s {{name}}. ',
    'This is {{name}} and ',
    '{{name}} here. '
]

def summarise_direction(direction):
    m = re.match(r'\w+ to (\w+)', direction)
    if m:
        return m.group(1).lower()
    return direction

for tbm in data:
    print (random.choice(greetings).format(phrase=greet_phrase()) + 'I\'m at {location}, heading {direction} towards {destination} with {to_go:0.1f}km to go').format(
        name=tbm['drive_name'],
        location='[E%s/N%s]' % (tbm['easting'], tbm['northing']),
        direction=summarise_direction(tbm['tbm_direction']),
        destination=tbm['tbm_dest'],
        to_go=float(tbm['distance_remaining'])
    )
