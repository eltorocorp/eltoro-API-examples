/* POST /users
 */

import rp from 'request-promise';

// An email object. See UsersEmailSchema
const emailObj = {
  address: 'ex@example.com',                   // required field
  label: 'Work',
  service: 'google',
}

// Body of request, See UsersAddSchema
const data = {
  registered_emails: [                        // required field
    emailObj,
  ],
  orgId: '<Your Org Id>',                     // required field
  // Profile contains user info.
  // See UsersProfileSchema
  profile: {},
  // Set roles for this user on this org
  // We are creating a reporting only user
  rolesOnOrgId: ['orgreporting'],
  username: 'APItestuser',
}

export const users_POST = (token, orgId) => {
  return new Promise((resolve, reject) => {
    rp({
      method: 'POST',
      body,
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
