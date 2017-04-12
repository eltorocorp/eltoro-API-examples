"""Using the /stats/download endpoint to generate 'last month' reports for all orgs
   for which the user has reporting access.

   Reports can be downloaded in HTML, PDF, or CSV format

   Usage:

   python get_downloadable_reports <email> <password> <html|pdf|csv>
"""
import sys
import requests

BASE_URL = 'https://api-prod.eltoro.com'

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
        org_id = sys.argv[4]
    except IndexError:
        org_id = 'not set'

    login = {'email': user, 'password': passw}
    print login
    login_resp = requests.post(BASE_URL + '/users/login', login)
    print login_resp.json()
    try:
        token = login_resp.json()[unicode('token')]
        user_id = login_resp.json()[unicode('id')]
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
            print "You belong to multiple orgs. Please provide one of the following org ids as the last argument."
            print "Orgs to which you belong: "
            print orgs
            sys.exit()

    return headers, org_id

def get_orgs(hdrs, org_id):
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

def pad_month(n):
    return str(n) if n >= 10 else '0' + str(n)
