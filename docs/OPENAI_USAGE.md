# OpenAI Natural Language to SQL System

Your warehouse application already has a complete system that converts customer plain text requests into SQL queries and executes them to show data.

## 🚀 Quick Start

### 1. Start the Server
```bash
python app.py
```
Server runs on: `http://localhost:25000`

### 2. Set OpenAI API Key (One-time setup)
```bash
curl -X POST http://localhost:25000/api/v1/openai/set-key \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your-openai-api-key-here"}'
```

### 3. Send Plain Text Queries
```bash
curl -X POST http://localhost:25000/api/v1/openai/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me all users with their email addresses", "limit": 10}'
```

## 📋 Available Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/openai/set-key` | POST | Set OpenAI API key |
| `/api/v1/openai/query` | POST | **Main endpoint**: Plain text → SQL → Data |
| `/api/v1/openai/schema` | GET | View database schema |
| `/api/v1/openai/sql` | POST | Execute SQL directly |

## 💬 Example Customer Queries

Your customers can ask questions in plain English:

- **"Show me all users"**
- **"Find users who have active policies"**
- **"List all payments made last month"**
- **"Show me quotes that are still bindable"**
- **"Find policies that expire this year"**
- **"What's the total revenue from payments?"**
- **"Show me users without any policies"**

## 📊 Response Format

```json
{
  "sql": "SELECT id, first_name, last_name, email FROM user LIMIT 10",
  "explanation": "This query retrieves all users with their basic information",
  "data": [
    {"id": 1, "first_name": "John", "last_name": "Doe", "email": "john@example.com"},
    {"id": 2, "first_name": "Jane", "last_name": "Smith", "email": "jane@example.com"}
  ],
  "columns": ["id", "first_name", "last_name", "email"],
  "row_count": 2
}
```

## 🧪 Test the System

Run the test script:
```bash
python test_openai_queries.py
```

View API examples:
```bash
python test_openai_queries.py --examples
```

## 🔒 Security Features

- ✅ Only SELECT queries allowed (no data modification)
- ✅ Automatic LIMIT clause added to prevent large results
- ✅ SQL injection protection through parameterized queries
- ✅ Error handling and logging

## 🗄️ Database Schema

Your system automatically detects these tables:
- **user** - User information
- **quote** - Insurance quotes
- **policy** - Insurance policies  
- **payment_transaction** - Payment records

## 🎯 How It Works

1. **Customer Input**: Plain text query
2. **OpenAI Processing**: Converts text to SQL using your database schema
3. **SQL Execution**: Safely executes the generated SQL
4. **Results**: Returns data with explanation

## 🛠️ Troubleshooting

**"OpenAI API key not set"**
- Use the `/openai/set-key` endpoint first

**"Server not running"**
- Start with: `python app.py`

**"Failed to convert query"**
- Check your OpenAI API key is valid
- Try simpler, more specific queries

## 📈 Advanced Usage

### Custom Limits
```json
{"query": "Show me all users", "limit": 50}
```

### Complex Queries
```json
{"query": "Find users who have policies but no payments"}
```

### Direct SQL (for testing)
```json
{"sql": "SELECT COUNT(*) as total_users FROM user"}
```

---

**Your system is ready to use! Customers can now ask questions in plain English and get data back automatically.** 🎉
