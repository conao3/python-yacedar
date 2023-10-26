# python-yacedar

Simple, straitforward Python bindings for Rust [Cedar policy language](https://github.com/cedar-policy/cedar).


# Installation

```bash
pip install yacedar
```

# Usage

See `/sample` directory.

```python
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

request = yacedar.Request(
    principal = yacedar.EntityUid('User', 'alice'),
    action = yacedar.EntityUid('Action', 'update'),
    resource = yacedar.EntityUid('Photo', 'VacationPhoto94.jpg'),
)

authorizer = yacedar.Authorizer()
response = authorizer.is_authorized(request, policy_set)

# expected: True
print(response.is_allowed)
```
