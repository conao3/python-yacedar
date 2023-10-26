'''
7. Attribute-based conditions (pt. 2)
https://www.cedarpolicy.com/en/tutorial/abac-pt2
'''

import yacedar

policy_set = yacedar.PolicySet('''\
permit(
  principal,
  action in [Action::"view", Action::"edit", Action::"delete"],
  resource
)
when {
  resource.owner == principal.id
};
''')

entities = yacedar.Entities([
    {
        "uid": {
            "type": "Photo",
            "id": "VacationPhoto94.jpg"
        },
        "attrs": {
            "dept": "cosmic",
            "owner": "alice"
        },
        "parents": []
    },
    {
        "uid": {
            "type": "User",
            "id": "alice"
        },
        "attrs": {
            "id": "alice",
            "dept": "chaos"
        },
        "parents": []
    }
])

request = yacedar.Request(
    principal = yacedar.EntityUid('User', 'alice'),
    action = yacedar.EntityUid('Action', 'view'),
    resource = yacedar.EntityUid('Photo', 'VacationPhoto94.jpg'),
)

authorizer = yacedar.Authorizer()
response = authorizer.is_authorized(request, policy_set, entities)

# expected: True
print(response.is_allowed)
