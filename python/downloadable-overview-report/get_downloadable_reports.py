"""Using the /stats/download endpoint to generate 'last month' reports for all orgs
   for which the user has reporting access.

   Reports can be downloaded in HTML, PDF, or CSV format

   Usage:

   python get_downloadable_reports <email> <password> <html|pdf|csv>
"""
import datetime
import calendar
import sys
import requests

from get_downloadable_reports_lib import *

TYPES = ['html', 'pdf', 'csv']

TYPE = 'html'

if sys.argv[3] in TYPES:
    TYPE = sys.argv[3]

HEADERS, ORG_ID = get_headers()
ORGS = get_orgs(HEADERS, ORG_ID)

NOW = datetime.datetime.now()
MONTH = ((NOW.month - 2) % 12) + 1
YEAR = NOW.year - 1 if MONTH == 12 else NOW.year
MONTH_NAME = calendar.month_name[MONTH]
MONTH_LAST = calendar.monthrange(YEAR, MONTH)[1]

for org in ORGS:
    filename = org + '_' + MONTH_NAME + str(YEAR) + '.' + TYPE
    data = {
        "orgId": org,
        "start": str(YEAR) + '-' + pad_month(MONTH) + '01',
        "stop": str(YEAR) + '-' + pad_month(MONTH) + str(MONTH_LAST),
        "as": TYPE,
    }
    r = requests.get(BASE_URL + '/stats/download', data=data, headers=HEADERS)
    report = requests.utils.get_unicode_from_response(r)
    with open('./' + filename, 'wb') as fout:
        fout.write(base64.decodestring(report))

