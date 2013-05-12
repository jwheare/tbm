#!/usr/bin/env python

import json
import random
import re
import datetime
import sys
import urllib2, BaseHTTPServer
import pyproj
import csv
import os
import twitter

def get_twitter():
    for k in ['TBM_OAUTH_TOKEN', 'TBM_OAUTH_SECRET', 'TBM_CONSUMER_KEY', 'TBM_CONSUMER_SECRET']:
        if k not in os.environ:
            return None
    return twitter.Twitter(auth=twitter.OAuth(
        os.environ['TBM_OAUTH_TOKEN'],
        os.environ['TBM_OAUTH_SECRET'],
        os.environ['TBM_CONSUMER_KEY'],
        os.environ['TBM_CONSUMER_SECRET']
    ))

def get_last_values(f):
    last_values = {}
    reader = csv.reader(f)
    for tbm in reader:
        last_values[tbm[0]] = float(tbm[1])
    return last_values

def fetch(url, data=None, headers={}):
    req = urllib2.Request(url=url, data=data, headers=headers)
    try:
        return urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        short_err, long_err = BaseHTTPServer.BaseHTTPRequestHandler.responses.get(e.code)
        print 'Error %s %s\n%s' % (e.code, long_err, e.read())
        return None

def get_name(lat, lon):
    # http://wiki.openstreetmap.org/wiki/Nominatim
    response = fetch('http://nominatim.openstreetmap.org/reverse?lat=%s&lon=%s&format=json' % (lat, lon))
    if not response:
        sys.exit()
    data = json.load(response)
    addr = data['address']
    return addr.get('village', addr.get('town', addr.get('suburb')))

def get_lat_lon(easting, northing):
    bng = pyproj.Proj(init='epsg:27700')
    wgs84 = pyproj.Proj(init='epsg:4326')
    (lon, lat) = pyproj.transform(bng, wgs84, easting, northing)
    return (lat, lon)


def greet_phrase():
    now = datetime.datetime.now()
    if now.hour > 7 and (now.hour < 12 and now.minute < 45):
        return random.choice(['Good morning', 'Morning', 'Hullo', 'Hi', 'Hey'])
    elif now.hour > 17 and now.hour < 23:
        return random.choice(['Good evening', 'Evening', 'Hello', 'Hi there', 'Hi'])
    else:
        return random.choice(['Hello', 'Hi', 'Hey'])

def summarise_direction(direction):
    m = re.match(r'\w+ to (\w+)', direction)
    if m:
        return m.group(1).lower()
    return direction

# Load machines data
# source = open('sample.json')
source = fetch("http://www.crossrail.co.uk/near-you/geoserver/get-tbms", headers={
    'X-Requested-With': 'XMLHttpRequest'
})
if not source:
    sys.exit()

data = json.load(source)

# Precompute lat long
for tbm in data:
    lat, lon = get_lat_lon(tbm['easting'], tbm['northing'])
    tbm['lat'] = lat
    tbm['lon'] = lon

# Fetch a list of dlr stations
dlr = []
with open('dlr.csv', 'rb') as f:
    reader = csv.reader(f)
    for i, station in enumerate(reader):
        if i > 0: # skip header
            dlr.append(station[0])

# Precompute distances to tube stations (exclude dlr)
tube_distances = []
g = pyproj.Geod(ellps='WGS84')
with open('tube.csv', 'rb') as f:
    reader = csv.reader(f)
    for i, station in enumerate(reader):
        if i > 0: # skip header
            station_name = station[0]
            if station_name not in dlr:
                station_lat = station[3]
                station_lon = station[4]
                station_distances = [station_name]
                for tbm in data:
                    az12, az21, dist = g.inv(station_lon, station_lat, tbm['lon'], tbm['lat'])
                    station_distances.append(dist)
                tube_distances.append(station_distances)

# Generate messages
greetings = [
    '{phrase}, {name} here! ',
    '{phrase}, it\'s {name}. ',
    'This is {name} and ',
    '{name} here. '
]

# Set up last values log
last_file = 'last.csv'
if os.path.isfile(last_file):
    f = open(last_file, 'r+')
else:
    f = open(last_file, 'w+')
last_values = get_last_values(f)
writer = csv.writer(f)

TWITTER = get_twitter()

for i, tbm in enumerate(data):
    last = last_values.get(tbm['drive_name'])
    remain = float(tbm['distance_remaining'])
    if last and last - remain < 1:
        continue

    tube_distances.sort(key=lambda station: station[i+1])
    nearest_station = tube_distances[0]
    station_name = nearest_station[0]
    station_distance = nearest_station[i+1]

    # Vary if we're 'at' a station
    if station_distance < 100:
        at = 'at %s station' % station_name
    else:
        at = 'under %s' % get_name(tbm['lat'], tbm['lon'])

    message = 'I\'m {at}, heading {direction} towards {destination} with {to_go:g}km to go'
    line = (random.choice(greetings) + message).format(
        phrase=greet_phrase(),
        name=tbm['drive_name'],
        at=at,
        dist=tube_distances[0][i+1],
        direction=summarise_direction(tbm['tbm_direction']),
        destination=tbm['tbm_dest'],
        to_go=round(remain, 1)
    )
    print line
    if TWITTER:
        TWITTER.statuses.update(
            status=line,
            lat=tbm['lat'],
            long=tbm['lon'],
            display_coordinates=True
        )
        writer.writerow((tbm['drive_name'], tbm['distance_remaining']))
