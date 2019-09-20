#!/usr/bin/env python3

import urllib.parse
import urllib.request
import csv
import time
import json
import base64

# GET TEMP TOKEN
try:
    with open("allegro_creds") as f:
        token = f.readlines()
except:
    raise Exception("no creds found! pls create allegro_creds file: CLIENT_ID:CLIENT_SECRET inside")

URL = 'https://allegro.pl/auth/oauth/token?grant_type=client_credentials'

HEADERS = {
    'Authorization': 'Basic {}'.format(base64.b64encode(token[0].strip().encode()).decode())
}
req = urllib.request.Request(
    URL,
    headers=HEADERS,
)
try:
    with urllib.request.urlopen(req) as response:
        r = json.loads(response.read())
except:
    raise Exception('sth wrong with req')
# TOKEN FETCHED


#
# RUN PARAMETERS:
#

URL = 'https://api.allegro.pl/offers/listing?category.id={}&phrase={}'
HEADERS = {
    'Accept': 'application/vnd.allegro.public.v1+json',
    'Content-type': 'application/vnd.allegro.public.v1+json',
    'Authorization': 'Bearer {}'.format(r['access_token']),
}
ALLEGRO_CATEGORY_ID = 11
FILE_WITH_DATA = 'daclist1.csv'

# CHANGE BORDER ;)

STOP_WORDS = (
    'pasek',
    'paski',
    'stopki',
)
MAX_PRICE = 50
DAC_NAME = 'tda1541'

#
# END OF PARAMETERS
#

try:
    with open("allegro_already_seen") as f:
        already_seen = set([int(x) for x in f.read()[:-1].split(',')])
except:
    already_seen = set()

with open(FILE_WITH_DATA, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=';', quotechar='"')
    for row in reader:
        model = row[0]
        dac = row[1]
        if DAC_NAME in dac.lower():
            time.sleep(0.02)
            print('searchin for ...', model, 'with DAC:', dac)
            req = urllib.request.Request(
                URL.format(ALLEGRO_CATEGORY_ID, urllib.parse.quote_plus(model)),
                headers=HEADERS,
            )
            #[ req.add_header(key, val) for key, val in HEADERS.items() ]
            try:
                with urllib.request.urlopen(req) as response:
                    r = json.loads(response.read())
            except:
                raise Exception('sth wrong with req')

            for item in r['items']['promoted'] + r['items']['regular']:
                if float(item['sellingMode']['price']['amount']) < MAX_PRICE and \
                all([ x not in item['name'].lower() for x in STOP_WORDS ]) and \
                int(item['id']) not in already_seen:
                    print(
                        "    ",
                        item['name'],
                        float(item['sellingMode']['price']['amount']),
                    )
                    already_seen.add(int(item['id']))

with open("allegro_already_seen", 'w') as f:
    f.write(','.join([str(x) for x in already_seen]))
    f.write('\n')
