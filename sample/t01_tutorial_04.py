'''
4. Undefined scopes
https://www.cedarpolicy.com/en/tutorial/undefined-scope
'''

import yacedar

policy_set = yacedar.PolicySet('''\
permit(
  principal,
  action in [Action::"view", Action::"edit", Action::"delete"],
  resource == Photo::"vacationPhoto.jpg"
);
''')

request = yacedar.Request(
    principal = yacedar.EntityUid('User', 'alice'),
    action = yacedar.EntityUid('Action', 'view'),
    resource = yacedar.EntityUid('Photo', 'vacationPhoto.jpg'),
)

authorizer = yacedar.Authorizer()
response = authorizer.is_authorized(request, policy_set)

# expected: True
print(response.is_allowed)
