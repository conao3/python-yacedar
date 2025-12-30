# yacedar

Python bindings for the [Cedar](https://www.cedarpolicy.com/) policy language, built with Rust for performance and reliability.

Cedar is an open-source policy language created by AWS for defining and enforcing authorization policies. This library provides a straightforward way to use Cedar policies in your Python applications.

## Installation

```bash
pip install yacedar
```

## Quick Start

```python
import yacedar

# Define your authorization policies
policy_set = yacedar.PolicySet('''
permit(
  principal == User::"alice",
  action    == Action::"update",
  resource  == Photo::"VacationPhoto94.jpg"
);
''')

# Create an authorization request
request = yacedar.Request(
    principal='User::"alice"',
    action='Action::"update"',
    resource='Photo::"VacationPhoto94.jpg"',
)

# Evaluate the request against the policies
authorizer = yacedar.Authorizer()
response = authorizer.is_authorized(request, policy_set)

print(response.is_allowed)  # True
```

## Features

- **Permit and Forbid Policies**: Define fine-grained access control rules
- **Entity-based Authorization**: Work with principals, actions, and resources
- **Set Operations**: Use collections in policy conditions
- **Schema Validation**: Validate entities and policies against schemas

## API Reference

### PolicySet

Create a policy set from Cedar policy syntax:

```python
policy_set = yacedar.PolicySet('''
permit(
  principal == User::"alice",
  action in [Action::"view", Action::"edit"],
  resource == Document::"report.pdf"
);

forbid(
  principal == User::"bob",
  action == Action::"delete",
  resource
);
''')
```

### Request

Create an authorization request:

```python
request = yacedar.Request(
    principal='User::"alice"',
    action='Action::"view"',
    resource='Document::"report.pdf"',
)
```

### Authorizer

Evaluate requests against policies:

```python
authorizer = yacedar.Authorizer()
response = authorizer.is_authorized(request, policy_set)

if response.is_allowed:
    print("Access granted")
else:
    print("Access denied")
```

## Examples

More examples are available in the `sample/` directory, covering:

- Basic policy structure
- Forbid policies
- Set operations
- Entity hierarchies
- Conditional policies

## Requirements

- Python 3.7 or later

## Links

- [Cedar Policy Language](https://www.cedarpolicy.com/)
- [Cedar Documentation](https://docs.cedarpolicy.com/)
- [Cedar GitHub Repository](https://github.com/cedar-policy/cedar)

## License

Apache License 2.0
