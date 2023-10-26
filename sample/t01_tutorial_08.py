'''
8. Conditions and context
https://www.cedarpolicy.com/en/tutorial/abac-pt1
'''

import yacedar

policy_set = yacedar.PolicySet('''\
permit(
  principal in User::"alice",
  action in [Action::"update", Action::"delete"],
  resource == Photo::"flower.jpg")
when {
  context.mfa_authenticated == true &&
  context.request_client_ip == "222.222.222.222"
};
''')

request = yacedar.Request(
    principal = yacedar.EntityUid('User', 'alice'),
    action = yacedar.EntityUid('Action', 'update'),
    resource = yacedar.EntityUid('Photo', 'flower.jpg'),
    context = yacedar.Context({
        'mfa_authenticated': True,
        'request_client_ip': '222.222.222.222',
        'oidc_scope': 'profile',
    }),
)

authorizer = yacedar.Authorizer()
response = authorizer.is_authorized(request, policy_set)

# expected: True
print(response.is_allowed)
