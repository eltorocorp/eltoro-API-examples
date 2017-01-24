#!/bin/bash
# Usage:
# ./createCampaign.sh campaignName /location/of/file.csv

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

URL="https://api-prod.eltoro.com"
CAMPAIGN_NAME=$1
SEG=$2

YOUR_USER_NAME="Your Username goes here."
YOUR_PASSWORD="Your Password goes here."
YOUR_ORG_ID="Your orgId goes here."

# login
bearerToken=$(curl -X POST -H "Content-Type: application/json" -d \
        '{"username":"${YOUR_USER_NAME}", "password":"${YOUR_PASSWORD}"}' \
        "${URL}/users/login")


# create a new Campaign, title only
curlresult=$(curl -X POST -H "Authorization: Bearer ${bearerToken}" -H "Content-Type: application/json" -d '{
  "name": "${CAMPAIGN_NAME}",
  "orgId": "${YOUR_ORG_ID}"
}' "${URL}/campaigns")

echo $curlresult

CID=`echo $curlresult  | jsonlint -p | grep "_id" | tail -n -1 | cut -f4 -d '"'`

echo "campaign $CID added"

# Create orderLine
orderLineId=$(curl -X POST -H "Authorization: Bearer ${bearerToken}" -H "Content-Type: application/json" -d '{
    "name": "${CAMPAIGN_NAME}",
    "orgId": "${YOUR_ORG_ID}",
    "campaignId": "${CID}"
}' "${URL}/orderLines")

orderLineId=`echo ${orderLineId}  | jsonlint -p | grep "_id" | tail -n -1 | cut -f4 -d '"'`

# Create bucket
bucketId=$(curl -X POST -H "Authorization: Bearer ${bearerToken}" -H "Content-Type: multipart/form-data" \
  -F "name=${SEG}" -F "type=12" -F "targetType=1" -F "conf.preventDownload=true" -F "file=@${SEG}" \
  -F "orgId=${YOUR_ORG_ID}" "https://api-prod-uploads.eltoro.com/bucket")

bucketId=`echo ${bucketId}  | jsonlint -p | grep "_id" | tail -n -1 | cut -f4 -d '"'`

# Attach bucket to orderLine
curlResult=$(curl -X PATCH -H "Content-Type: application/json" -H "Authorization: Bearer ${bearerToken}" -d '{
    "orderLineId": "${orderLineId}",
    "bucketId": "${bucketId}"
}' "${URL}/orderLines/${orderLineId}/attachBucket")

echo 'Bucket attached to OrderLine: ${curlResult}'
