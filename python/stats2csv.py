#/usr/bin/python
"""Using the /stats endpoint to generate CSVs of click and impression data.

    This script will create CSVs of click and impression data by hour, disaggregated by
    creative, order line, and campaign. It will iterate over all active campaigns for
    which the user has permissions.
"""

from stats2csv_lib import *

HEADERS, ORG_ID = get_headers()
OPTIONS = get_options()
FILES = open_files(OPTIONS['start'])

ORGS = get_orgs(ORG_ID, HEADERS)
CAMPAIGNS, OLS, CREATIVES = get_orderlines(ORGS, HEADERS)


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
    hour = {}
    for row in rows:
        if level == "campaigns":
            ids['campaigns'] = row["campaignId"]
            ids['creatives'] = ""
            ids['orderLines'] = ""
        if level == "orderLines":
            ids['campaigns'] = ""
            ids['creatives'] = ""
            ids['orderLines'] = row["orderLineId"]
        if level == "creatives":
            ids['campaigns'] = ""
            ids['creatives'] = row["creativeId"]
            ids['orderLines'] = row["orderLineId"]

        stats = stats_query(ids, HEADERS, OPTIONS)
        i = 0
        ii = 0
        for obs in stats:
            FILES[level]['file'].write(str(OPTIONS['start']) + ',')
            FILES[level]['file'].write(str(i) + ',')
            FILES[level]['file'].write(str(obs['clicks']) + ',')
            totalclicks = totalclicks + obs['clicks']
            FILES[level]['file'].write(str(obs['imps']) + ',')
            totalimps = totalimps + obs['imps']
            if level == "campaigns":
                FILES[level]['file'].write(str(row['orgId']) + ',')
                FILES[level]['file'].write(str(row['campaignId']))
            if level == "orderLines":
                FILES[level]['file'].write(str(row['orderLineId']) + ',')
                FILES[level]['file'].write(str(row['campaignId']) + ',')
                FILES[level]['file'].write(str(row['targetType']) + ',')
                FILES[level]['file'].write(str(row['creativeType']) + ',')
                FILES[level]['file'].write(str(row['orderLineName']) + ',')
                FILES[level]['file'].write(str(row['campaignName']) + ',')
                FILES[level]['file'].write(str(row['refId']) + ',')
                FILES[level]['file'].write(str(row['start']) + ',')
                FILES[level]['file'].write(str(row['stop']))
            if level == "creatives":
                FILES[level]['file'].write(str(row['creativeId']) + ',')
                FILES[level]['file'].write(str(row['orderLineId']) + ',')
                FILES[level]['file'].write(str(row['creativeName']))
            FILES[level]['file'].write('\r\n')
            try:
                hour[ii]['imps'] = hour[ii]['imps']+obs['imps']
                hour[ii]['clicks'] = hour[ii]['clicks']+obs['clicks']
            except StandardError:
                hour[ii] = {}
                hour[ii]['imps'] = 0
                hour[ii]['clicks'] = 0
                hour[ii]['imps'] = hour[ii]['imps']+obs['imps']
                hour[ii]['clicks'] = hour[ii]['clicks']+obs['clicks']
            ii = ii+1
        i += 1
