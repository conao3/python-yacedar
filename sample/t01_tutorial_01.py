'''
1. Policy structure
https://www.cedarpolicy.com/en/tutorial/policy-structure
'''

import yacedar

policy_set = yacedar.PolicySet('''\
permit(
  principal == User::"alice",
  action    == Action::"update",
  resource  == Photo::"VacationPhoto94.jpg"
);
''')

entities = yacedar.Entities([])

request = yacedar.Request(
    principal = yacedar.EntityUid('User', 'alice'),
    action = yacedar.EntityUid('Action', 'update'),
    resource = yacedar.EntityUid('Photo', 'VacationPhoto94.jpg'),
    context = yacedar.Context({})
)

authorizer = yacedar.Authorizer()
response = authorizer.is_authorized(request, policy_set, entities)

# expected: True
print(response.allowed)
