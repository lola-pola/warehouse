# OpenAI Integration for Natural Language to SQL

This document describes the OpenAI integration that allows users to query the database using natural language.

## Overview

The OpenAI integration provides the following capabilities:
- Set and manage OpenAI API keys
- Convert natural language queries to SQL
- Execute SQL queries safely (SELECT only)
- Get database schema information
- Direct SQL execution for advanced users

## API Endpoints

All endpoints are under `/api/v1/openai/`

### 1. Set OpenAI API Key

**POST** `/api/v1/openai/set-key`

Set the OpenAI API key for natural language processing.

**Request Body:**
```json
{
    "api_key": "sk-your-openai-api-key-here"
}
```

**Response:**
```json
{
    "message": "OpenAI API key set successfully"
}
```

### 2. Get Database Schema

**GET** `/api/v1/openai/schema`

Get a human-readable description of the database schema.

**Response:**
```json
{
    "schema": "Table: user\n  - id: INTEGER NOT NULL PRIMARY KEY\n  - name: VARCHAR(80) NOT NULL\n  - email: VARCHAR(120) NULL\n..."
}
```

### 3. Natural Language Query

**POST** `/api/v1/openai/query`

Convert natural language to SQL and execute the query.

**Request Body:**
```json
{
    "query": "Show me all users with their email addresses",
    "limit": 100
}
```

**Response:**
```json
{
    "sql": "SELECT name, email FROM user LIMIT 100",
    "explanation": "This query selects the name and email columns from the user table",
    "data": [
        {"name": "John Doe", "email": "john@example.com"},
        {"name": "Jane Smith", "email": "jane@example.com"}
    ],
    "columns": ["name", "email"],
    "row_count": 2
}
```

### 4. Direct SQL Execution

**POST** `/api/v1/openai/sql`

Execute a SQL query directly (SELECT queries only).

**Request Body:**
```json
{
    "sql": "SELECT * FROM user WHERE email IS NOT NULL LIMIT 10",
    "limit": 10
}
```

**Response:**
```json
{
    "sql": "SELECT * FROM user WHERE email IS NOT NULL LIMIT 10",
    "explanation": "Direct SQL execution",
    "data": [...],
    "columns": ["id", "name", "email"],
    "row_count": 10
}
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install openai==1.3.0
```

### 2. Get OpenAI API Key

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-`)

### 3. Set API Key

Use the `/set-key` endpoint to configure your OpenAI API key:

```bash
curl -X POST http://localhost:25000/api/v1/openai/set-key \
  -H "Content-Type: application/json" \
  -d '{"api_key": "sk-your-api-key-here"}'
```

## Usage Examples

### Example Natural Language Queries

1. **Basic queries:**
   - "Show me all users"
   - "Get users with email addresses"
   - "Find all policies created this month"

2. **Aggregation queries:**
   - "How many users do we have?"
   - "Count successful payments by type"
   - "Average number of quotes per user"

3. **Join queries:**
   - "Show users and their policies"
   - "Get payment transactions with policy details"
   - "List quotes that became policies"

### Example API Calls

```python
import requests

# Set API key
requests.post('http://localhost:25000/api/v1/openai/set-key', 
              json={'api_key': 'sk-your-key'})

# Natural language query
response = requests.post('http://localhost:25000/api/v1/openai/query',
                        json={'query': 'Show me all users with their policies'})
print(response.json())

# Direct SQL
response = requests.post('http://localhost:25000/api/v1/openai/sql',
                        json={'sql': 'SELECT COUNT(*) FROM user'})
print(response.json())
```

## Database Schema

The system understands the following tables:

- **user**: User information (id, name, email)
- **quote**: Insurance quotes (id, user_id, create_time, bind_time, bindable)
- **policy**: Insurance policies (id, user_id, quote_id)
- **payment_transaction**: Payment attempts (id, time, payment_type, policy_id, success)

### Relationships:
- User has many Quotes and Policies
- Quote belongs to User and has many Policies
- Policy belongs to User and Quote, has many PaymentTransactions
- PaymentTransaction belongs to Policy

## Security Features

1. **API Key Validation**: Keys are validated against OpenAI before being stored
2. **Query Restrictions**: Only SELECT queries are allowed for safety
3. **Result Limits**: Automatic LIMIT clauses prevent large result sets
4. **Error Handling**: Comprehensive error handling and logging

## Error Handling

Common error responses:

```json
{
    "error": "OpenAI API key not set"
}
```

```json
{
    "error": "Only SELECT queries are allowed"
}
```

```json
{
    "error": "Failed to generate SQL query"
}
```

## Testing

Run the test script to verify the integration:

```bash
python test_openai_integration.py
```

This will test all endpoints and provide feedback on their functionality.

## Troubleshooting

### Common Issues

1. **"OpenAI package not installed"**
   - Solution: `pip install openai==1.3.0`

2. **"Invalid OpenAI API key"**
   - Check your API key is correct and has sufficient credits
   - Ensure the key starts with `sk-`

3. **"Failed to generate SQL query"**
   - Try rephrasing your natural language query
   - Check that your query relates to the available tables

4. **"Only SELECT queries are allowed"**
   - The system only allows read operations for security
   - Use the direct SQL endpoint for complex SELECT queries

### Logs

Check the application logs for detailed error information:
- OpenAI API errors are logged with full details
- SQL execution errors include the attempted query
- All API key operations are logged for security auditing
