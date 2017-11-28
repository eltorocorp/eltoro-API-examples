#!/usr/bin/env python
# ---------------------------------------
# El Toro API Example Script: Create Venue Replay Bucket
# ---------------------------------------
# This script will login, and then create a Venue Replay Bucket for your Org
# NOTE you will need to configure details of the bucket
# NOTE if you are unsure about login or basics, try out example-login-list-view-stats.py
#
# This is meant for demonstration purposes only,
# and as an added bonus, it outputs to the console curl commands
# if you set REDACTTOKEN=False you can just copy/paste curl commands to replicate
# ---------------------------------------
from string import Template
import requests, json
import datetime
import calendar
import sys

USERNAME="__your__user__" # <-- usually your email
PASSWORD="__your__pass__"

DOMAIN = "https://api-sandbox.eltoro.com/"  # Dev / Sandbox
# DOMAIN="https://api-prod.eltoro.com/"   # Prod
REDACTTOKEN = True    # True will replace token in your console

BUCKET_DATA = {
    "type": 22,
    "name": "Example Venue Replay from API",
    #  "tags": ["indinaola", "my_references"],
    #  "refId": "your_api_id",
    #  "po": "your_purchase_order_id",
    "conf": {
        "geoframe": {
            "timeframes": [
                {
                    "start": "2017-05-01T16:00:00.000-0500",
                    "stop": "2017-05-05T16:00:00.000-0500"
                }
            ],
            "map": {
                "center": [-93.56100797718682, 41.36085012324344],
                "features": [
                    # NOTE this is standard GEOJSON
                    # http://geojsonlint.com/
                    {
                        "type": "Feature",
                        "properties": {},
                        "geometry": {
                            "type": "MultiPolygon",
                            "coordinates": [
                                [
                                    [
                                        [-93.56369018620171, 41.362364024993724],
                                        [-93.56371164387383, 41.359368434408445],
                                        [-93.5583043104998, 41.359304011591],
                                        [-93.55839014118828, 41.362396234895876],
                                        [-93.56369018620171, 41.362364024993724]
                                    ]
                                ]
                            ]
                        }
                    }
                ]
            }
        }
    }
}


# ---------------------------------------
# Helper Functions
# ---------------------------------------
# simple response JSON data cleanup - needed for simple print statements
def mock_curl_output(response):
    data = response.json()
    if 'token' in data:
        if REDACTTOKEN:
            data['token'] = 'xxxxxxxx'
    return json.dumps(data)


print('')
print("### LOGIN to get a token")
URL = DOMAIN + "users/login"
mock_curl_cmd = Template("curl -X POST -H \"Content-Type: application/json\" -d '{\"email\": \"$USERNAME\", \"password\": \"xxxxxx\"}' '$URL'")

print("$ " + mock_curl_cmd.substitute(dict(USERNAME=USERNAME, URL=URL)))
payload = json.dumps(dict(email=USERNAME, password=PASSWORD))
headers = {'content-type': "application/json"}
response = requests.request("POST", URL, data=payload, headers=headers)
print(mock_curl_output(response))
print('')
# ok - get from the response the token and user_id
try:
    TOKEN = response.json()['token']
    USERID = response.json()['id']
except KeyError:
    print('Login error, check your credentials\n')
    print(response.text)
    sys.exit()

# all other requests use the same headers
headers = {
    'authorization': "Bearer " + TOKEN,
    'content-type': "application/json"
}
# not displaying the token on screen... (uncomment below to show)
TOKENREDACTED = 'xxxxxxxx' if REDACTTOKEN is True else TOKEN

# ---------------------------------------
# Add a new Venue Replay Bucket
# ---------------------------------------
print('')
print("### Add a new Venue Replay Bucket")

payload = json.dumps(BUCKET_DATA)

URL = DOMAIN + "buckets"
mock_curl_cmd = Template("curl -X POST -H \"Content-Type: application/json\" -H \"Authorization: Bearer $TOKEN\" -d '$PAYLOAD' '$URL'")
print("$ " + mock_curl_cmd.substitute(dict(TOKEN=TOKENREDACTED, PAYLOAD=payload, URL=URL)))
response = requests.request("POST", URL, data=payload, headers=headers)
print(mock_curl_output(response))
print('')
