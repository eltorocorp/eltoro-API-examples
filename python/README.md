# stats2csv.py

This script will create CSVs of click and impression data by hour, disaggregated by
creative, order line, and campaign. It will iterate over all active campaigns for
an org and all of its sub orgs.

## Requirements

You will need to have Python 2.7 installed. Linux and OS X both provide Python
out of the box, to verify run `python --version` in a terminal window. If
`python` isn't found, or the version is anything other than 2.7, follow these
instructions to install Python 2.7:

  * [Installing Python on Linux](http://docs.python-guide.org/en/latest/starting/install/linux/)
  * [Installing Python on Mac](http://docs.python-guide.org/en/latest/starting/install/osx/)

Windows users will likely need to install Python. This walkthrough will guide
you through a Windows install:

  * [Installing Python on Windows](http://docs.python-guide.org/en/latest/starting/install/win/)

The first time you set this up on windows, you will need to run the setup.bat script.
This will install the requests module for python.

In a linux or OSX environment, you need to also have the requests module.  Just run
`sudo pip install requests` after ensuring Python 2.7 is installed

## Usage

```python stats2csv <username> <password> <start> <stop> <granularity> <org id>```

CLI options:
```
  username: ElToro Portal email/username

  password: ElToro Portal password.

  start: (optional, defaults to yesterday) Start date of stats run.

  stop: (optional, defaults to yesterday) End date of stats run

  granularity: (optional, defaults to 'hour') Timeframe of results. Results can be
  grouped by hour, day, week or month

  org id: (optional) Org id. Use this option to specifiy which org's stats to
  return if the user belongs to multiple orgs.

  Start and stop should be provided in the %Y-%m-%d or %Y-%m-%d %H:%M:%S format
```

The most typical use case is retrieving the previous day's stats to be loaded
into a local database. If the user does not belong to multiple orgs, this can be
accomplished by using the script's default values:

```python stats2csv <username> <password> ```

We recommend running this script after 6AM EST. By specifying time in the
`start` and `stop` fields, this script can be run multiple times a day, as long
as the resulting CSVs are _upserted_ in the local data store.

Windows users can accomplish this typical usage by running the provided
`getstats.bat` script.


## Results

This script produces three CSV files with the following headers

campaignYYYY-MM-DD.csv (YYYY-MM-DD matches the provided value for `start`)

```Date, Hour, Clicks, Imps, orgId, campaignId```

orderLinesYYYY-MM-DD.csv

```Date, Hour, Clicks, Imps, orderLineId, campaignId, targetType, creativeType, orderLineName, campaignName, refId, start, stop```

creativeYYYY-MM-DD.csv

```Date, Hour, Clicks, Imps, creativeId, orderLineId, creativeName```
