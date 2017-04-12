#!/usr/bin/env python
# ---------------------------------------
# El Toro API Example Script: Simple Example
# ---------------------------------------
# This script will login, list campaigns, view campaign, view orderLine,
# and report monthly stats for the campaign and daily for the orderLine.
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

USERNAME="__your__user__"
PASSWORD="__your__pass__"

DOMAIN="https://api-sandbox.eltoro.com/"  # Dev / Sandbox
# DOMAIN="https://api-prod.eltoro.com/"   # Prod
REDACTTOKEN=True    # True will replace token in your console
# REDACTTOKEN=False # False will show the token in your console

# Set this to force Campaign View & Stats to use it (otherwise we use recent)
CAMPAIGNID=""

# Set this to force Order Line View & Stats to use it (otherwise we use recent)
ORDERLINEID=""

# ---------------------------------------
# Helper Functions
# ---------------------------------------
# simple response JSON data cleanup - needed for simple print statements
def mock_curl_output(response):
    data = response.json()
    if 'token' in data:
        if REDACTTOKEN:
            data[unicode('token')] = 'xxxxxxxx'
    return json.dumps(data)

print('')
# ---------------------------------------
# Login
# ---------------------------------------
# NOTE you probably want to store the TOKEN somewhere in your API
# it's a bit slow to login every time - better to maintain a login TOKEN
# we send an expiration with it, or you can try/catch for
#   { "error": 401, "reason": "Requires Auth" }
# ---------------------------------------
print('')
print("### LOGIN to get a token")
URL=DOMAIN + "users/login"
mock_curl_cmd = Template("curl -X POST -H \"Content-Type: application/json\" -d '{\"username\": \"$USERNAME\", \"password\": \"xxxxxx\"}' '$URL'")
print("$ " + mock_curl_cmd.substitute(dict(USERNAME=USERNAME, URL=URL)))
payload = "{\"username\": \"developerstemp\", \"password\": \"eltororocks\"}"
headers = { 'content-type': "application/json" };
response = requests.request("POST", URL, data=payload, headers=headers)
print(mock_curl_output(response))
print('')
# ok - get from the response the token and user_id
try:
    TOKEN = response.json()[unicode('token')]
    USERID = response.json()[unicode('id')]
except KeyError:
    print 'Login error, check your credentials\n'
    print response.text
    sys.exit()

# all other requests use the same headers
headers = {
    'authorization': "Bearer " + TOKEN,
    'content-type': "application/json"
    };
# not displaying the token on screen... (uncomment below to show)
TOKENREDACTED='xxxxxxxx' if REDACTTOKEN == True else TOKEN

# ---------------------------------------
# Get a List of Recent Campaigns
# ---------------------------------------
print('')
print("### Get a List of Recent Campaigns")
URL=DOMAIN + "campaigns"
mock_curl_cmd = Template("curl -X GET -H \"Content-Type: application/json\" -H \"Authorization: Bearer $TOKEN\" '$URL'")
print("$ " + mock_curl_cmd.substitute(dict(TOKEN=TOKENREDACTED, URL=URL)))
response = requests.request("GET", URL, headers=headers)
print(mock_curl_output(response))
print('')
if CAMPAIGNID == "":
    # ok - get the top campaign ID
    try:
        CAMPAIGNID = response.json()['results'][0][unicode('_id')]
    except KeyError:
        print 'FAIL - unable to parse CAMPAIGNID (do you have any campaigns?)\n'
        print response.text
        sys.exit()


# ---------------------------------------
# Get A Single Campaigns's Full Details
# ---------------------------------------
print('')
print("### Get A Single Campaigns's Full Details")
URL=DOMAIN + "campaigns/" + CAMPAIGNID
mock_curl_cmd = Template("curl -X GET -H \"Content-Type: application/json\" -H \"Authorization: Bearer $TOKEN\" '$URL'")
print("$ " + mock_curl_cmd.substitute(dict(TOKEN=TOKENREDACTED, URL=URL)))
response = requests.request("GET", URL, headers=headers)
print(mock_curl_output(response))
print('')
if ORDERLINEID == "":
    # ok - get the top order line ID
    try:
        ORDERLINEID = response.json()['orderLines'][0][unicode('_id')]
    except KeyError:
        print 'FAIL - unable to parse ORDERLINEID (did the campaign have some?)\n'
        print response.text
        sys.exit()

# ---------------------------------------
# Get Order Line Details
# ---------------------------------------
print('')
print("### Get the Details of the first Order Line")
URL=DOMAIN + "orderLines/" + ORDERLINEID
mock_curl_cmd = Template("curl -X GET -H \"Content-Type: application/json\" -H \"Authorization: Bearer $TOKEN\" '$URL'")
print("$ " + mock_curl_cmd.substitute(dict(TOKEN=TOKENREDACTED, URL=URL)))
response = requests.request("GET", URL, headers=headers)
print(mock_curl_output(response))
print('')

# ---------------------------------------
# Get Stats for
# ---------------------------------------
print('')
print("### Get the Monthly Stats for the first Campaign")
URL=DOMAIN + "stats"
# get start/stop dates for the last year, end-of-month (note: currently timezone in UTC, soon will be a param)
today = datetime.datetime.now()
stop = today.replace(day=calendar.monthrange(today.year, today.month)[1])
delta = datetime.timedelta(days=365)
start = datetime.datetime.now() - delta
QS={
    'campaignId': CAMPAIGNID,
    'start': start.strftime('%Y-%m-01'),
    'stop': stop.strftime('%Y-%m-%d'),
    'granularity': 'month',
    }
URLWITHQS = URL + '?orderLineId=' + ORDERLINEID + '&start=' + QS['start'] + '&stop=' + QS['stop'] + '&granularity=' + QS['granularity']
mock_curl_cmd = Template("curl -X GET -H \"Content-Type: application/json\" -H \"Authorization: Bearer $TOKEN\" '$URL'")
print("$ " + mock_curl_cmd.substitute(dict(TOKEN=TOKENREDACTED, URL=URLWITHQS)))
response = requests.request("GET", URL, headers=headers, params=QS)
print(mock_curl_output(response))
print('')

print('')
print("### Get the Daily Stats for the first Order Line")
URL=DOMAIN + "stats"
# get start/stop dates for the last 10 days (note: currently timezone in UTC, soon will be a param)
stop = datetime.datetime.now()
delta = datetime.timedelta(days=10)
start = datetime.datetime.now() - delta
QS={
    'orderLineId': ORDERLINEID,
    'start': start.strftime('%Y-%m-%d'),
    'stop': stop.strftime('%Y-%m-%d'),
    'granularity': 'day',
    }
URLWITHQS = URL + '?orderLineId=' + ORDERLINEID + '&start=' + QS['start'] + '&stop=' + QS['stop'] + '&granularity=' + QS['granularity']
mock_curl_cmd = Template("curl -X GET -H \"Content-Type: application/json\" -H \"Authorization: Bearer $TOKEN\" '$URL'")
print("$ " + mock_curl_cmd.substitute(dict(TOKEN=TOKENREDACTED, URL=URLWITHQS)))
response = requests.request("GET", URL, headers=headers, params=QS)
print(mock_curl_output(response))
print('')

