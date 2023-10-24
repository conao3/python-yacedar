'''
1. Policy structure
https://www.cedarpolicy.com/en/tutorial/policy-structure
'''

import yacedar

principal = yacedar.EntityUid('User', 'alice')
action = yacedar.EntityUid('Action', 'update')
resource = yacedar.EntityUid('Photo', 'VacationPhoto94.jpg')
context = yacedar.Context({})

request = yacedar.Request(principal, action, resource, context)

policy_set = yacedar.PolicySet('''\
permit(
  principal == User::"alice",
  action    == Action::"update",
  resource  == Photo::"VacationPhoto94.jpg"
);
''')

entities = yacedar.Entities([])

authorizer = yacedar.Authorizer()

response = authorizer.is_authorized(request, policy_set, entities)

# expected: True
print(response.allowed)
print(response.diagnostics())
