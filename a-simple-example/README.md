# El Toro API Example Script: Simple Example

This script will login, list campaigns, view campaign, view orderLine,
and report monthly stats for the campaign and daily for the orderLine.

This is meant for demonstration purposes only,
and as an added bonus, it outputs to the console curl commands
if you set `REDACTTOKEN=False` you can just copy/paste curl commands to replicate

## Usage Instructions

Download/copy the script locally and edit it to your heart's content.

Specifically the top, you will need to set the username and password.

*Bonus* here is a quick copy and paste: (on Linux or a Mac)

    cd /tmp
    wget https://raw.githubusercontent.com/eltorocorp/eltoro-API-examples/master/a-simple-example/example-login-list-view-stats.py
    sed -i'' 's/__your__user__/MYUSERNAME/g' example-login-list-view-stats.py
    sed -i'' 's/__your__pass__/MYPASSWORD/g' example-login-list-view-stats.py
    python example-login-list-view-stats.py

