'''
5. Groups for role-based access control
https://www.cedarpolicy.com/en/tutorial/rbac
'''

import yacedar

policy_set = yacedar.PolicySet('''\
permit(
  principal in Role::"vacationPhotoJudges",
  action == Action::"view",
  resource == Photo::"vacationPhoto94.jpg"
);
''')

entities = yacedar.Entities([
    {
        "uid": {
            "type": "User",
            "id": "Bob"
        },
        "attrs": {},
        "parents": [
            {
                "type": "Role",
                "id": "vacationPhotoJudges"
            },
            {
                "type": "Role",
                "id": "juniorPhotographerJudges"
            }
        ]
    },
    {
        "uid": {
            "type": "Role",
            "id": "vacationPhotoJudges"
        },
        "attrs": {},
        "parents": []
    },
    {
        "uid": {
            "type": "Role",
            "id": "juniorPhotographerJudges"
        },
        "attrs": {},
        "parents": []
    }
])

request = yacedar.Request(
    principal = yacedar.EntityUid('User', 'Bob'),
    action = yacedar.EntityUid('Action', 'view'),
    resource = yacedar.EntityUid('Photo', 'vacationPhoto94.jpg'),
)

authorizer = yacedar.Authorizer()
response = authorizer.is_authorized(request, policy_set, entities)

# expected: True
print(response.is_allowed)
