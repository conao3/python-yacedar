'''
3. Sets
https://www.cedarpolicy.com/en/tutorial/sets
'''

import yacedar

policy_set = yacedar.PolicySet('''\
permit(
  principal == User::"alice",
  action in [Action::"view", Action::"edit", Action::"delete"],
  resource == Photo::"VacationPhoto94.jpg"
);
''')

request = yacedar.Request(
    principal = yacedar.EntityUid('User', 'alice'),
    action = yacedar.EntityUid('Action', 'view'),
    resource = yacedar.EntityUid('Photo', 'VacationPhoto94.jpg'),
)

authorizer = yacedar.Authorizer()
response = authorizer.is_authorized(request, policy_set)

# expected: True
print(response.is_allowed)
