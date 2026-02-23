# QBO Accounts Client

Python client for the QuickBooks Online Accounts API.

## Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from qbo_accounts import QBOClient, BearerAuth

auth = BearerAuth(access_token="your-token")

with QBOClient(realm_id="1234567890", auth=auth) as client:
    # Read an account
    account = client.accounts.read("42")
    print(account.name, account.account_type)

    # Query accounts
    result = client.accounts.query(where="Active = true")
    for acct in result.accounts:
        print(acct.name, acct.current_balance)
```

## OAuth2 Setup

For production use with automatic token refresh:

```python
from qbo_accounts import QBOClient, OAuth2Auth

auth = OAuth2Auth(
    client_id="your-client-id",
    client_secret="your-client-secret",
    access_token="your-access-token",
    refresh_token="your-refresh-token",
)

with QBOClient(realm_id="1234567890", auth=auth) as client:
    # Tokens are automatically refreshed on 401
    accounts = list(client.accounts.query_all())
```

## CRUD Operations

### Create

```python
from qbo_accounts import AccountCreate

payload = AccountCreate(name="Office Supplies", account_type="Expense")
account = client.accounts.create(payload)
```

### Read

```python
account = client.accounts.read("42")
```

### Query

```python
# Single page
result = client.accounts.query(where="AccountType = 'Bank'")

# All pages (auto-pagination)
for account in client.accounts.query_all(where="Active = true"):
    print(account.name)
```

### Update

```python
from qbo_accounts import AccountUpdate

payload = AccountUpdate(id="42", sync_token="0", name="Updated Name")
account = client.accounts.update(payload)
```

### Deactivate (Soft Delete)

```python
account = client.accounts.deactivate("42", sync_token="0")
```

## Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Environment variables:

| Variable | Description |
|---|---|
| `QBO_BASE_URL` | API base URL (sandbox or production) |
| `QBO_REALM_ID` | Your QBO company ID |
| `QBO_ACCESS_TOKEN` | OAuth2 access token |
| `QBO_REFRESH_TOKEN` | OAuth2 refresh token |
| `QBO_CLIENT_ID` | OAuth2 client ID |
| `QBO_CLIENT_SECRET` | OAuth2 client secret |

## Development

```bash
pip install -e ".[dev]"
pytest
```
