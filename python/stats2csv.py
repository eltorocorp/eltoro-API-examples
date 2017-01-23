#/usr/bin/python
"""Using the /stats endpoint to generate CSVs of click and impression data.

    This script will create CSVs of click and impression data by hour, disaggregated by
    creative, order line, and campaign. It will iterate over all active campaigns for
    which the user has permissions.
"""

import sys
from datetime import date, timedelta
import requests

BASE_URL = 'https://api-prod.eltoro.com'

# Functions
def get_orgs(org_id):
    """Get list of orgs for which stats will be received

    Args:
        org_id (str): Id of parent org

    Returns:
        list: List of org ids

    """
    _orgs = [org_id]
    orgs_resp = requests.get(BASE_URL + '/orgs', headers=headers)
    for org in orgs_resp.json()['results']:
        if org_id in org['parents']:
            _orgs.append(org['_id'])
    return _orgs

def get_campaigns(org_list, hdrs):
    """Retrieves lists of objects for which we will return stats

    Args:
        org_list (list): List of org ids
        hdrs (dict): Authorization header for API

    Returns:
        list, list, list: Lists of campaign, order line and creative objects to query

    """
    collection = "campaigns"
    result = []
    suffix = '&pagingLimit=10'
    for org in org_list:
        page = 1
        query = '/' + collection + '?orgId=' + org + suffix
        resp = requests.get(BASE_URL + query + '&pagingPage=' + str(page), headers=hdrs).json()
        coll = resp['results']
        paging = resp['paging']
        while paging['total'] > paging['limit'] * page:
            page += 1
            resp = requests.get(BASE_URL + query + '&pagingPage=' + str(page), headers=hdrs).json()
            coll += resp['results']

        # This section
        recentdate = date.today() - timedelta(days=7)
        for obj in coll:
            try:
                if obj['status'] == 20 or obj['status'] == 99 and obj["stop"] > recentdate:
                    result.append(obj)
            except:
                pass
    return result

## This gets all of the orderline data, and preps the data for output - add additional fields here
def get_orderlines(org_list, hdrs):

    campaigns = get_campaigns(org_list, hdrs)

    collection = "orderLines"
    ols = []
    creatives = []
    camplist = []
    suffix = '&pagingLimit=10'
    page = 1
    query = '/' + collection + "?" + suffix
    resp = requests.get(BASE_URL + query + '&pagingPage=' + str(page), headers=headers).json()
    coll = resp['results']
    paging = resp['paging']
    while paging['total'] > paging['limit'] * page:
        page += 1
        resp = requests.get(BASE_URL + query + '&pagingPage=' + str(page), headers=headers).json()
        coll += resp['results']
    allols = coll
    for camp in campaigns:
        thecamp = {
            'campaignId':camp["_id"],
            'orgId':camp["orgId"]
            }
        camplist.append(thecamp)

    for obj in allols:
        for camp in campaigns:
            if obj["campaign"]["_id"] == camp["_id"]:
                try:
                    ref_id = obj["refId"]
                except:
                    ref_id = ""
                oldata = {
                    ##  CSV Field Header: Field to Populate it wit
                    'orderLineId':obj["_id"],
                    'campaignId':obj["campaignId"],
                    'targetType':obj["targetType"],
                    'creativeType':obj["creativeType"],
                    'orderLineName':obj["name"],
                    'campaignName':obj["campaign"]["name"],
                    'ref_id':ref_id,
                    'start':obj["start"],
                    'stop':obj["stop"]
                }
                ols.append(oldata)
                olid = obj["_id"]
                for cre in obj["creatives"]:
                    creative = {
                        'creativeId':cre["_id"],
                        'orderLineId':olid,
                        'creativeName':cre["name"]
                        }
                    creatives.append(creative)
                try:
                    for cre in obj["creativesIdsDetached"]:
                        creative = {
                            'creativeId':cre["_id"],
                            'orderLineId':olid,
                            'creativeName':cre["name"]
                            }
                        creatives.append(creative)
                except:
                    pass
    return camplist, ols, creatives

# this runs the query for the detail stats for each option
def stats_query(ids, headers):
    query = (
        '/stats?start=' +
        start +
        '&stop=' +
        stop +
        '&granularity=' +
        granularity+
        #'&orgId=' +
        #org_id +
        '&campaignId=' + ids['campaigns'] +
        '&orderLineId=' + ids['orderLines'] +
        '&creativeId=' + ids['creatives'] +
        '&disableCache=true'
    )
    r = requests.get(BASE_URL + query+ "&disableCache=true", headers=headers).json()
    return r

# Parse arguments and verify some things, default others
try:
    try:
        start = sys.argv[3]
    except:
        start = str(date.today() - timedelta(days=1))# + "%2007:00:00"
    try:
        stop = sys.argv[4]
    except:
        stop = str(date.today() - timedelta(days=0))# + "%2006:59:59"
    try:
        granularity = sys.argv[5]
    except:
        granularity = "hour"
    user = sys.argv[1]  # Hard Code username here if you do not wish to enter it on the command line
    passw = sys.argv[2] # Hard Code password here if you do not wish to enter it on the command line

except IndexError:
    print 'Usage:\n\n  python stats2csv <username> <password> <start (optional)> <end (optional)> <granularity (optional)> <org id (optional)>'
    print ""
    print "If dates or granularity are left off, it defaults to 'yesterday' (if run right now : "+ start +" thru  " + stop +") with a granularity timeframe of '"+granularity+"'"
    print "username/password are required fields, unless you have hard coded them into this script"
    print "-- This script should be in a cron/scheduled task to run daily at at least 2am PST, or 5am EST to ensure yesterday stats are updated --"
    sys.exit()

try:
    org_id = sys.argv[6]
except IndexError:
    org_id = 'not set'

#create output files
creative_csv = open('creative' + str(start) + '.csv', 'w')
orderLine_csv = open('orderLine' + str(start) + '.csv', 'w')
campaign_csv = open('campaign' + str(start) + '.csv', 'w')


## Do all of the login stuff here

login = { 'email': user, 'password': passw }


login_resp = requests.post(BASE_URL + '/users/login', login)
#login_resp_local = requests.post('http://localhost:3000' + '/users/login', login)

try:
    token = login_resp.json()[unicode('token')]
#    token_local = login_resp_local.json()[unicode('token')]
    user_id = login_resp.json()[unicode('id')]
#    user_id_local = login_resp_local.json()[unicode('id')]
except KeyError:
    print 'Login error, check your credentials\n'
    print login_resp.text
    sys.exit()

headers = {
    "Authorization": ("Bearer " + str(token))
}

#headers_local = {
#    "Authorization": ("Bearer " + str(token_local))
#}

## Check valid login and org id
if org_id == 'not set':
    user_resp = requests.get(BASE_URL + '/users/' + user_id, headers=headers)
    try:
        orgs = user_resp.json()[unicode('roles')].keys()
    except:
        print "Please provide an org id as the last argument"
        sys.exit()
    if len(orgs) == 1:
        org_id = str(orgs[0])
    else:
        print "You belong to multiple orgs. Please provide an org id as the last argument"
        sys.exit()

#Used for making the csvs by names
indices = {
    'orderLines': {
        'name': 'orderLines',
        'file': orderLine_csv,
    },
    'campaigns': {
        'name': 'campaigns',
        'file': campaign_csv,
    },
    'creatives': {
        'name': 'creatives',
        'file': creative_csv,
        'denorm': 'orderLines',
    },
}
import json
with open("apnxcompare.json") as json_data:
        tocompare=json.load(json_data)
#tocompare=dict(tocompare)

## Get the org from the login that happened
orgs = get_orgs(org_id)
## now go get the data from the functions above
#print "Getting data for the report"
campaigns,ols,creatives = get_orderlines(orgs)


# meat an Potato's
for level in indices.keys():
#    print level + " running"
    rows = []
    ids={}
    val = ""
    row1 = 'Date,Hour,Clicks,Imps,'

    #Write a row for each collection belonging to each org
    if level == 'orderLines':
        rows = ols
        id = 'orderLineId'
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
        rows = creatives
        id = 'creativeId'
        for row in rows:
            row1 += 'creativeId' + ','
            row1 += 'orderLineId' + ','
            row1 += 'creativeName'
            break

    if level == 'campaigns':
        rows = campaigns
        id = 'campaignId'
        for row in rows:
            row1 += "orgId" + ','
            row1 += 'campaignId'
            break

#    print level + " Column headers: " + row1
    indices[level]['file'].write(row1 + '\r\n')

    print "Running Stats for " + level
    totalclicks=0
    totalimps=0
    hour={}
    for row in rows:

        #ids = build_ids(level, row[id])
        if level == "campaigns":
            ids['campaigns']=row["campaignId"]
            ids['creatives']=""
            ids['orderLines']=""
        if level == "orderLines":
            ids['campaigns']=""
            ids['creatives']=""
            ids['orderLines']=row["orderLineId"]
        if level == "creatives":
            ids['campaigns']=""
            ids['creatives']=row["creativeId"]
            ids['orderLines']=row["orderLineId"]

        stats = stats_query(ids, headers)
#        stats = stats_query_tmp(ids, headers)
        i=0
        ii=0
        for obs in stats:
            #print obs
            #
            ## This is accounting for GMT->EST by getting two days worth and running on the proper window...
            ## Raw Log data is in GMT
            if i > 4 and i < 29:
                indices[level]['file'].write(str(start) + ',')
                indices[level]['file'].write(str(i - 5) + ',')
                indices[level]['file'].write(str(obs['clicks']) + ',')
                totalclicks = totalclicks + obs['clicks']
                indices[level]['file'].write(str(obs['imps']) + ',')
                totalimps = totalimps + obs['imps']
                if level == "campaigns":
                    indices[level]['file'].write(str(row['orgId']) + ',')
                    indices[level]['file'].write(str(row['campaignId']))
                if level == "orderLines":
                    indices[level]['file'].write(str(row['orderLineId']) + ',')
                    indices[level]['file'].write(str(row['campaignId']) + ',')
                    indices[level]['file'].write(str(row['targetType']) + ',')
                    indices[level]['file'].write(str(row['creativeType']) + ',')
                    indices[level]['file'].write(str(row['orderLineName']) + ',')
                    indices[level]['file'].write(str(row['campaignName']) + ',')
                    indices[level]['file'].write(str(row['refId']) + ',')
                    indices[level]['file'].write(str(row['start']) + ',')
                    indices[level]['file'].write(str(row['stop']))
                if level == "creatives":
                    indices[level]['file'].write(str(row['creativeId']) + ',')
                    indices[level]['file'].write(str(row['orderLineId']) + ',')
                    indices[level]['file'].write(str(row['creativeName']))
                indices[level]['file'].write('\r\n')
                try:
                    hour[ii]['imps']=hour[ii]['imps']+obs['imps']
                    hour[ii]['clicks']=hour[ii]['clicks']+obs['clicks']
                except:
                    hour[ii] = {}
                    hour[ii]['imps'] = 0
                    hour[ii]['clicks'] = 0
                    hour[ii]['imps']=hour[ii]['imps']+obs['imps']
                    hour[ii]['clicks']=hour[ii]['clicks']+obs['clicks']
                    pass
                ii=ii+1
                val = ""
            i += 1
    print "Total Clicks for "+ level +" : " + str(totalclicks)
    if str(totalclicks) != str(tocompare["totals"][0]["clicks"]):
        print "  ****************** DOES NOT MATCH ("+str(tocompare["totals"][0]["clicks"])+") ************************"
    print "Total Imps for "+ level +" : " + str(totalimps)
    if str(totalimps) != str(tocompare["totals"][0]["imps"]):
        print "  ****************** DOES NOT MATCH ("+str(tocompare["totals"][0]["imps"])+") ************************"

    if level == "creatives":
        print "Totals by Hour for "+level+""
        print "    Checks comparing each Hour also running..."
        for hr in hour:
            if str(tocompare["data"][hr]["imps"]) != str(hour[hr]['imps']):
                print str(hr)+':Imps:' +str(hour[hr]['imps'])
                print "  ****************** DOES NOT MATCH ("+str(tocompare["data"][hr]["imps"])+") ************************"
            if str(tocompare["data"][hr]["clicks"]) != str(hour[hr]['clicks']):
                print str(hr)+':Clicks:' +str(hour[hr]['clicks'])
                "  ****************** DOES NOT MATCH ("+str(tocompare["data"][hr]["clicks"])+") ************************"
print "Unless it shows 'DOES NOT MATCH' above, it actually matched the downloaded file"
sysg.exit()
