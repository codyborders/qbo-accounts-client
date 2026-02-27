"""Account resource for QBO API."""

from __future__ import annotations

from ..models.accounts import Account, AccountCreate, AccountUpdate
from .base import NameListResource


class AccountsResource(NameListResource[Account, AccountCreate, AccountUpdate]):
    """CRUD operations for QBO Account entities."""

    ENTITY = "account"
    ENTITY_KEY = "Account"
    QUERY_ENTITY = "Account"
