# stats2csv.py

This script will create CSVs of click and impression data by hour, disaggregated by
creative, order line, and campaign. It will iterate over all active campaigns for
an org and all of its sub orgs

## Usage

```python stats2csv <username> <password> <start> <end> <granularity)> <org id>```

CLI options:
```
  username: ElToro email/username
  password: ElToro password
  start: (optional, defaults to yesterday) start date of stats run
  end: (optional, defaults to yesterday) end date of stats run
  granularity: (optional, defaults to 'hour') timeframe of results. Hour, day, week or month
  org id: (optional) Org id, if user belongs to multiple orgs
````

