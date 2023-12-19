'''
2. Forbid policies
https://www.cedarpolicy.com/en/tutorial/forbid
'''

import yacedar

policy_set = yacedar.PolicySet('''\
permit(
  principal == User::"alice",
  action    == Action::"view",
  resource  == Photo::"VacationPhoto94.jpg"
);

forbid(
  principal == User::"alice",
  action    == Action::"view",
  resource  == Photo::"VacationPhoto94.jpg"
);
''')

request = yacedar.Request(
    principal='User::"alice"',
    action='Action::"view"',
    resource='Photo::"VacationPhoto94.jpg"',
)

authorizer = yacedar.Authorizer()
response = authorizer.is_authorized(request, policy_set)

# expected: False
print(response.is_allowed)
