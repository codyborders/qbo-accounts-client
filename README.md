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

## CLI

After installation, the `qbo` command is available for terminal-based access to the QBO API. All output is JSON.

### Setup

Copy `.env.example` to `.env` and fill in your credentials (see [Configuration](#configuration) below). The CLI reads these automatically.

### Commands

```bash
# List all available entity names
qbo entities

# Read a single entity by ID
qbo read customers 42

# Read system entities that don't require an ID
qbo read preferences
qbo read entitlements

# Shortcut for company info
qbo company-info

# Query with filters (single page, default 100 results)
qbo query customers --where "DisplayName LIKE '%John%'"
qbo query invoices --where "Balance > '0'" --order-by "MetaData.CreateTime DESC"
qbo query customers --max-results 10

# List all entities with auto-pagination
qbo list customers
qbo list invoices --where "Balance > '0'" --order-by "DueDate ASC"

# Create an entity from a JSON string
qbo create customers '{"DisplayName": "Acme Corp"}'

# Update an entity (Id and SyncToken are required)
qbo update customers '{"Id": "42", "SyncToken": "0", "DisplayName": "Acme Inc"}'

# Hard-delete a transaction entity
qbo delete bills 42 0

# Soft-delete a name-list entity (sets Active=false)
qbo deactivate customers 42 0

# Void a voidable transaction (invoices, payments, etc.)
qbo void invoices 42 0
```

### Entity names

Use hyphens in entity names on the command line. They are converted to underscores internally.

```bash
qbo read bill-payments 42    # resolves to bill_payments
qbo list purchase-orders     # resolves to purchase_orders
qbo list time-activities     # resolves to time_activities
```

### Operation support by entity type

Not all operations are available on every entity:

| Operation    | Name-list entities | Transaction entities | Voidable transactions | System entities |
|---|---|---|---|---|
| `read`       | Yes | Yes | Yes | Varies |
| `query`      | Yes | Yes | Yes | Some |
| `list`       | Yes | Yes | Yes | No |
| `create`     | Yes | Yes | Yes | tax-service only |
| `update`     | Yes | Yes | Yes | Some |
| `delete`     | No  | Yes | Yes | No |
| `deactivate` | Yes | No  | No  | No |
| `void`       | No  | No  | Yes | No |

### Error handling

Errors are written as JSON to stderr with a non-zero exit code:

```json
{"error": "Unknown entity: foo"}
```

### Piping and scripting

JSON output works well with `jq`:

```bash
# Get a customer's display name
qbo read customers 42 | jq '.DisplayName'

# List all active customer IDs
qbo list customers --where "Active = true" | jq '.[].Id'

# Count invoices with a balance
qbo query invoices --where "Balance > '0'" | jq '.total_count'
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
| `QBO_REDIRECT_URI` | OAuth2 redirect URI. Defaults to `http://localhost:8484/callback` for local development. Set this to your public HTTPS callback in production. |

## Development

```bash
pip install -e ".[dev]"
pytest
```

For production QuickBooks apps, Intuit requires an HTTPS redirect URI. Set `QBO_REDIRECT_URI`
to the exact public callback URL registered in the Intuit app. The CLI uses the same redirect
URI for both the authorization request and the token exchange so the values stay aligned.
