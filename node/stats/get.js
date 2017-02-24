/* GET /stats
 */

import rp from 'request-promise';
import querystring from 'querystring';


// An email object. See UsersEmailSchema
const emailObj = {
  address: 'ex@example.com',                   // required field
  label: 'Work',
  service: 'google',
}

// Retrieve one day of an org's total stats
// This will serialize as:
// ?start=2017-01-01&stop2017-01-01&granularity=hour&orgId=<ORG ID>
export const org_stats = {
  start: '2017-01-01',                        // required field
  stop: '2017-01-01',                         // required field
  granularity: 'hour',                        // required field
  orgId: '<ORG ID>',
}


export const stats_GET = (token, body) => {
  return new Promise((resolve, reject) => {
    rp({
      method: 'GET',
      url: `${baseUrl}${querystring.stringify(body)}`,
      body: querystring.s
      headers: {
        Content-Type: 'application/json',
        Authorization: `Bearer ${token}`,
      }
      json: true,
    })
      .then((body) => {
        resolve(body);
      })
      .catch((err) => {
        reject(err);
      });
  });
}
