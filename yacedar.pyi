from __future__ import annotations

import enum
from typing import Any


class EntityUid:
    def __new__(cls, type_name: str, name: str) -> EntityUid: ...

class Context:
    def __new__(cls, value: dict[str, Any]) -> Context: ...

class Request:
    def __new__(cls, principal: EntityUid | None, action: EntityUid | None, resource: EntityUid | None, context: Context | None) -> Request: ...

class PolicySet:
    def __new__(cls, policies_str: str) -> PolicySet: ...

class Entities:
    def __new__(cls, entities: list[dict[str, Any]]) -> Entities: ...

class Authorizer:
    def __new__(cls) -> Authorizer: ...
    def is_authorized(self, request: Request, policy_set: PolicySet, entities: Entities) -> Response: ...

class Response:
    decision: Decision
    allowed: bool

    def diagnostics(self) -> str: ...

class Decision(enum.Enum):
    Allow = enum.auto()
    Deny = enum.auto()
