# API Documentation

This document provides detailed information about the Data Warehouse API endpoints, request/response formats, and usage examples.

## Base URL

```
http://localhost:25000/api/v1
```

## Authentication

Currently, the API does not require authentication. In a production environment, you would typically implement:
- API keys
- JWT tokens
- OAuth 2.0

## Content Type

All API requests and responses use JSON format:
```
Content-Type: application/json
```

## Error Handling

The API uses standard HTTP status codes:

- `200` - OK
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

Error responses include a message describing the issue:
```json
{
  "message": "Error description"
}
```

## Endpoints

### Users

#### List Users
```http
GET /users/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  }
]
```

#### Create User
```http
POST /users/
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com"
}
```

#### Get User
```http
GET /users/{id}
```

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com"
}
```

#### Update User
```http
PUT /users/{id}
```

**Request Body:**
```json
{
  "name": "Updated Name",
  "email": "updated@example.com"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Updated Name",
  "email": "updated@example.com"
}
```

#### Delete User
```http
DELETE /users/{id}
```

**Response:** `204 No Content`

### Quotes

#### List Quotes
```http
GET /quotes/
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "create_time": "2023-01-01T12:00:00Z",
    "bind_time": null,
    "bindable": true
  }
]
```

#### Create Quote
```http
POST /quotes/
```

**Request Body:**
```json
{
  "user_id": 1,
  "bindable": true
}
```

**Response (201):**
```json
{
  "id": 1,
  "user_id": 1,
  "create_time": "2023-01-01T12:00:00Z",
  "bind_time": null,
  "bindable": true
}
```

#### Get Quote
```http
GET /quotes/{id}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "create_time": "2023-01-01T12:00:00Z",
  "bind_time": null,
  "bindable": true
}
```

#### Bind Quote
```http
PATCH /quotes/{id}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "create_time": "2023-01-01T12:00:00Z",
  "bind_time": "2023-01-01T14:00:00Z",
  "bindable": true
}
```

### Policies

#### List Policies
```http
GET /policies/
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "quote_id": 1
  }
]
```

#### Create Policy
```http
POST /policies/
```

**Request Body:**
```json
{
  "user_id": 1,
  "quote_id": 1
}
```

**Response (201):**
```json
{
  "id": 1,
  "user_id": 1,
  "quote_id": 1
}
```

**Validation Rules:**
- Quote must exist and belong to the specified user
- Quote must be bound (have a `bind_time`)
- Only one policy can be created per quote

#### Get Policy
```http
GET /policies/{id}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "quote_id": 1
}
```

### Payments

#### List Payment Transactions
```http
GET /payments/
```

**Response:**
```json
[
  {
    "id": 1,
    "time": "2023-01-01T15:00:00Z",
    "payment_type": "CREDIT",
    "policy_id": 1,
    "success": true
  }
]
```

#### Create Payment Transaction
```http
POST /payments/
```

**Request Body:**
```json
{
  "payment_type": "CREDIT",
  "policy_id": 1
}
```

**Payment Types:**
- `CREDIT`
- `DEBIT`
- `PREPAID`

**Response (201):**
```json
{
  "id": 1,
  "time": "2023-01-01T15:00:00Z",
  "payment_type": "CREDIT",
  "policy_id": 1,
  "success": true
}
```

**Note:** The `success` field is randomly determined to simulate payment processing.

#### Get Payment Transaction
```http
GET /payments/{id}
```

**Response:**
```json
{
  "id": 1,
  "time": "2023-01-01T15:00:00Z",
  "payment_type": "CREDIT",
  "policy_id": 1,
  "success": true
}
```

### Analytics

#### General Statistics
```http
GET /analytics/stats
```

**Response:**
```json
{
  "total_users": 10,
  "total_quotes": 20,
  "total_policies": 15,
  "total_payments": 45,
  "successful_payments": 38,
  "payment_success_rate": 84.44
}
```

#### Payment Statistics by Type
```http
GET /analytics/payment-stats
```

**Response:**
```json
{
  "Credit": {
    "total": 20,
    "successful": 17,
    "failed": 3,
    "success_rate": 85.0
  },
  "Debit": {
    "total": 15,
    "successful": 14,
    "failed": 1,
    "success_rate": 93.33
  },
  "Prepaid": {
    "total": 10,
    "successful": 7,
    "failed": 3,
    "success_rate": 70.0
  }
}
```

#### User Statistics
```http
GET /analytics/user-stats
```

**Response:**
```json
{
  "total_users": 10,
  "users_with_quotes": 8,
  "users_with_policies": 6,
  "users_without_quotes": 2,
  "conversion_rate": 75.0
}
```

## Usage Examples

### Complete Workflow Example

1. **Create a user:**
```bash
curl -X POST http://localhost:25000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

2. **Create a quote for the user:**
```bash
curl -X POST http://localhost:25000/api/v1/quotes/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "bindable": true}'
```

3. **Bind the quote:**
```bash
curl -X PATCH http://localhost:25000/api/v1/quotes/1
```

4. **Create a policy from the bound quote:**
```bash
curl -X POST http://localhost:25000/api/v1/policies/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "quote_id": 1}'
```

5. **Process a payment for the policy:**
```bash
curl -X POST http://localhost:25000/api/v1/payments/ \
  -H "Content-Type: application/json" \
  -d '{"payment_type": "CREDIT", "policy_id": 1}'
```

6. **Get analytics:**
```bash
curl http://localhost:25000/api/v1/analytics/stats
```

## Swagger Documentation

Interactive API documentation is available at:
```
http://localhost:25000/swagger/
```

The Swagger UI provides:
- Interactive endpoint testing
- Request/response schema details
- Example payloads
- Authentication testing (when implemented)

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider implementing:
- Request rate limits per IP
- API key-based quotas
- Burst protection

## Pagination

For endpoints that return lists, pagination is not currently implemented but should be added for production use:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

## Filtering and Sorting

Future enhancements could include:
- Query parameter filtering: `GET /users/?name=John`
- Sorting: `GET /quotes/?sort=create_time&order=desc`
- Date range filtering: `GET /payments/?start_date=2023-01-01&end_date=2023-01-31`
