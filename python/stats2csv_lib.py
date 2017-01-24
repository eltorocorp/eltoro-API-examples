"""Using the /stats endpoint to generate CSVs of click and impression data.

    This script will create CSVs of click and impression data by hour, disaggregated by
    creative, order line, and campaign. It will iterate over all active campaigns for
    which the user has permissions.
"""
import sys
from datetime import date, timedelta
import requests

BASE_URL = 'https://api-prod.eltoro.com'

def open_files(start):
    """Open the csv files for writing and return a dict of file handles

        Args:
            start (str): The stringified start date for the stats run

        Returns:
            dict: File handles for csv output
    """
    return {
        'orderLines': {
            'name': 'orderLines',
            'file': open('orderLines' + str(start) + '.csv', 'w'),
        },
        'campaigns': {
            'name': 'campaigns',
            'file': open('campaigns' + str(start) + '.csv', 'w'),
        },
        'creatives': {
            'name': 'creatives',
            'file': open('creatives' + str(start) + '.csv', 'w'),
            'denorm': 'orderLines',
        },
    }

def get_orgs(org_id, hdrs):
    """Get list of orgs for which stats will be received

    Args:
        org_id (str): Id of parent org

    Returns:
        list: List of org ids

    """
    _orgs = [org_id]
    orgs_resp = requests.get(BASE_URL + '/orgs', headers=hdrs)
    for org in orgs_resp.json()['results']:
        if org_id in org['parents']:
            _orgs.append(org['_id'])
    return _orgs

def get_campaigns(org_list, hdrs):
    """Retrieves lists of objects for which we will return stats

    Args:
        org_list (list): List of org ids
        hdrs (dict): authorization header for api

    Returns:
        list: List of campaign objects from which we will pull order line data

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
            except StandardError:
                pass
    return result

def ol_request(page, hdrs):
    """Returns a page of orderline results

    Args:
        page (int): Page of results to return
        hdrs (dict): authorization header for api

    Returns:
        dict: JSON body of response

    """
    return requests.get((
        BASE_URL + '/orderLines?pagingLimit=10' +
        '&pagingPage=' +
        str(page)
        ), headers=hdrs).json()

def get_orderlines(org_list, hdrs):
    """Retrieves all order line data, and extracts the necessary campaign and creative data

    Args:
        org_list (list): List of ids for orgs to which the user belongs
        hdrs (dict): authorization header for api

    Returns:
        list, list, list: Lists of campaign, order line and creative objects to query
    """
    campaigns = get_campaigns(org_list, hdrs)

    ols = []
    creatives = []
    camplist = []
    page = 1
    resp = ol_request(page, hdrs)
    coll = resp['results']
    while resp['paging']['total'] > resp['paging']['limit'] * page:
        page += 1
        resp = ol_request(page, hdrs)
        coll += resp['results']
    allols = resp['results']
    for camp in campaigns:
        thecamp = {
            'campaignId':camp["_id"],
            'orgId':camp["orgId"]
            }
        camplist.append(thecamp)

    for obj in allols:
        for camp in campaigns:
            if obj["campaign"]["_id"] == camp["_id"]:
                if 'refId' not in obj:
                    obj["refId"] = ''
                ols.append({
                    ##  CSV Field Header: Field to Populate it wit
                    'orderLineId':obj["_id"],
                    'campaignId':obj["campaignId"],
                    'targetType':obj["targetType"],
                    'creativeType':obj["creativeType"],
                    'orderLineName':obj["name"],
                    'campaignName':obj["campaign"]["name"],
                    'ref_id':obj["refId"],
                    'start':obj["start"],
                    'stop':obj["stop"]
                })
                for cre in obj["creatives"]:
                    creative = {
                        'creativeId':cre["_id"],
                        'orderLineId':obj["_id"],
                        'creativeName':cre["name"]
                        }
                    creatives.append(creative)
                if 'creativeIdsDetached' in obj:
                    for cre in obj["creativesIdsDetached"]:
                        creative = {
                            'creativeId':cre["_id"],
                            'orderLineId':obj["_id"],
                            'creativeName':cre["name"]
                            }
                        creatives.append(creative)
    return camplist, ols, creatives

# this runs the query for the detail stats for each option
def stats_query(ids, hdrs, options):
    """Queries the stats API and returns a list of results

    Args:
        ids (dict): Dict of object ids to query
        hdrs (dict): authorization header for api
        options (dict): Query parameters to include with the request

    Returns:
        list: Stats broken down by (granularity)

    """
    query = (
        '/stats?start=' +
        options["start"] +
        '&stop=' +
        options["stop"] +
        '&granularity=' +
        options["granularity"] +
        '&campaignId=' + ids['campaigns'] +
        '&orderLineId=' + ids['orderLines'] +
        '&creativeId=' + ids['creatives'] +
        '&disableCache=true'
    )
    res = requests.get(BASE_URL + query+ "&disableCache=true", headers=hdrs).json()
    return res

# Parse arguments and verify some things, default others
def get_options():
    """Parse time window and granularity agruments

    Returns:
        dict: User supplied or default start time, stop time, and granularity
    """
    options = {}
    try:
        try:
            options['start'] = sys.argv[3]
        except StandardError:
            options['start'] = str(date.today() - timedelta(days=1))# + "%2007:00:00"
        try:
            options['stop'] = sys.argv[4]
        except StandardError:
            options['stop'] = str(date.today() - timedelta(days=0))# + "%2006:59:59"
        try:
            options['granularity'] = sys.argv[5]
        except StandardError:
            options['granularity'] = "hour"

    except IndexError:
        print (
            'Usage:\n\n  python stats2csv <username> <password> <start (optional)>' +
            '<end (optional)> <granularity (optional)> <org id (optional)>'
            )
        print ""
        print (
            "If dates or granularity are left off, it defaults to 'yesterday' (if" +
            "run right now : "+ options['start'] +" thru  " + options['stop'] +") with " +
            "a granularity timeframe of '" + options['granularity'] + "'"
            )
        print (
            "-- This script should be in a cron/scheduled task to run daily at at least" +
            "2am PST, or 5am EST to ensure yesterday stats are updated --"
            )
        sys.exit()
    return options


def get_headers():
    """Login and acquire an auth token

    Returns:
        dict: Header object with auth token
    """
    try:
        user = sys.argv[1]  # Hard Code username here if you do not wish to enter it
                            # on the command line
        passw = sys.argv[2] # Hard Code password here if you do not wish to enter it
                            # on the command line
    except IndexError:
        print (
            "username/password are required fields, unless you have hard coded them " +
            "into this script"
            )
        sys.exit()
    try:
        org_id = sys.argv[6]
    except IndexError:
        org_id = 'not set'

    login = {'email': user, 'password': passw}

    login_resp = requests.post(BASE_URL + '/users/login', login)

    try:
        token = login_resp.json()[unicode('token')]
        user_id = login_resp.json()[unicode('userId')]
    except KeyError:
        print 'Login error, check your credentials\n'
        print login_resp.text
        sys.exit()

    headers = {
        "Authorization": ("Bearer " + str(token))
    }
    ## Check valid login and org id
    if org_id == 'not set':
        user_resp = requests.get(BASE_URL + '/users/' + user_id, headers=headers)
        try:
            orgs = user_resp.json()[unicode('roles')].keys()
        except StandardError:
            print "Please provide an org id as the last argument"
            sys.exit()
        if len(orgs) == 1:
            org_id = str(orgs[0])
        else:
            print "You belong to multiple orgs. Please provide an org id as the last argument"
            sys.exit()

    return headers, org_id
