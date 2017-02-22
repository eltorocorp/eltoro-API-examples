#/usr/bin/python
"""Using the /stats endpoint to generate CSVs of click and impression data.

    This script will create CSVs of click and impression data by hour, disaggregated by
    creative, order line, and campaign. It will iterate over all active campaigns for
    which the user has permissions.
"""

from stats2csv_lib import *

print 'getting headers'
HEADERS, ORG_ID = get_headers()
print 'getting options'
OPTIONS = get_options()
print 'opening files'
FILES = open_files(OPTIONS['start'])

print 'getting orgs'
ORGS = get_orgs(ORG_ID, HEADERS)
print 'getting campaign data'
CAMPAIGNS, OLS, CREATIVES = get_object_data(ORGS, HEADERS, OPTIONS)

for level in FILES:
    rows = []
    ids = {}
    row1 = 'Date,Hour,Clicks,Imps,'

    if level == 'orderLines':
        rows = OLS
        row1 += 'orderLineId' + ','
        row1 += 'campaignId' + ','
        row1 += 'targetType' + ','
        row1 += 'creativeType' + ','
        row1 += 'orderLineName' + ','
        row1 += 'campaignName' + ','
        row1 += 'refId' + ','
        row1 += 'start' + ','
        row1 += 'stop'

    if level == 'creatives':
        rows = CREATIVES
        for row in rows:
            row1 += 'creativeId' + ','
            row1 += 'orderLineId' + ','
            row1 += 'creativeName'
            break

    if level == 'campaigns':
        rows = CAMPAIGNS
        for row in rows:
            row1 += "orgId" + ','
            row1 += 'campaignId'
            break

    FILES[level]['file'].write(row1 + '\r\n')

    print "Running Stats for " + level
    totalclicks = 0
    totalimps = 0
    for row in rows:
        if level == "campaigns":
            ids['campaigns'] = row["_id"]
            ids['creatives'] = ""
            ids['orderLines'] = ""
        if level == "orderLines":
            ids['campaigns'] = ""
            ids['creatives'] = ""
            ids['orderLines'] = row["_id"]
        if level == "creatives":
            ids['campaigns'] = ""
            ids['creatives'] = row["_id"]
            ids['orderLines'] = row["orderLineId"]

        stats = stats_query(ids, HEADERS, OPTIONS)
        i = 0
        ## Raw Log data is in GMT
        for obs in stats:
                FILES[level]['file'].write(str(OPTIONS['start']) + ',')
                FILES[level]['file'].write(str(i) + ',')
                FILES[level]['file'].write(str(obs['clicks']) + ',')
                totalclicks = totalclicks + obs['clicks']
                FILES[level]['file'].write(str(obs['imps']) + ',')
                totalimps = totalimps + obs['imps']
                if level == "campaigns":
                    FILES[level]['file'].write(str(row['orgId']) + ',')
                    FILES[level]['file'].write(str(row['_id']))
                if level == "orderLines":
                    FILES[level]['file'].write(str(row['_id']) + ',')
                    FILES[level]['file'].write(str(row['campaignId']) + ',')
                    FILES[level]['file'].write(str(row['targetType']) + ',')
                    FILES[level]['file'].write(str(row['creativeType']) + ',')
                    FILES[level]['file'].write(str(row['name']) + ',')
                    FILES[level]['file'].write(str(row['campaignName']) + ',')
                    FILES[level]['file'].write(str(row['start']) + ',')
                    FILES[level]['file'].write(str(row['stop']))
                if level == "creatives":
                    FILES[level]['file'].write(str(row['_id']) + ',')
                    FILES[level]['file'].write(str(row['orderLineId']) + ',')
                    FILES[level]['file'].write(str(row['name']))
                FILES[level]['file'].write('\r\n')
                i += 1
