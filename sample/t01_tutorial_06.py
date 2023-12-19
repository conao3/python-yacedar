'''
6. Attribute-based conditions
https://www.cedarpolicy.com/en/tutorial/abac-pt1
'''

import yacedar

policy_set = yacedar.PolicySet('''\
permit(
  principal,
  action == Action::"view",
  resource
)
when {
  resource.accessLevel == "public" && principal.location == "USA"
};
''')

entities = yacedar.Entities([
    {
        "uid": {
            "type": "Photo",
            "id": "VacationPhoto94.jpg"
        },
        "attrs": {
            "accessLevel": "public"
        },
        "parents": []
    },
    {
        "uid": {
            "type": "User",
            "id": "alice"
        },
        "attrs": {
            "location": "USA"
        },
        "parents": []
    }
])

request = yacedar.Request(
    principal='User::"alice"',
    action='Action::"view"',
    resource='Photo::"VacationPhoto94.jpg"',
)

authorizer = yacedar.Authorizer()
response = authorizer.is_authorized(request, policy_set, entities)

# expected: True
print(response.is_allowed)
