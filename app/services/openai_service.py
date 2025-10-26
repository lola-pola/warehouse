"""
OpenAI service for natural language to SQL conversion
"""
try:
    from openai import OpenAI
    openai_available = True
except ImportError:
    OpenAI = None
    openai_available = False

from flask import current_app
try:
    from sqlalchemy import inspect, text
except ImportError:
    inspect = None
    text = None

from app.models.base import db
from app.models.user import User
from app.models.quote import Quote
from app.models.policy import Policy
from app.models.payment import PaymentTransaction


class OpenAIService:
    """Service for handling OpenAI API interactions and NL to SQL conversion"""

    @staticmethod
    def _validate_openai_auth() -> tuple[bool, str]:
        """
        Validate OpenAI authentication

        Returns:
            tuple: (is_valid, error_message)
        """
        if not openai_available:
            return False, "OpenAI package not installed. Please install openai package."

        api_key = current_app.config.get('OPENAI_API_KEY')
        if not api_key:
            return False, ("OpenAI API key not configured. Please set your API key "
                          "first using the /openai/set-key endpoint.")

        try:
            # Test the API key by making a simple request
            client = OpenAI(api_key=api_key)
            client.models.list()
            return True, ""
        except Exception as e:
            error_msg = f"OpenAI authentication failed: {str(e)}"
            current_app.logger.error(error_msg)
            return False, error_msg

    @staticmethod
    def set_api_key(api_key: str) -> bool:
        """
        Set the OpenAI API key

        Args:
            api_key: The OpenAI API key

        Returns:
            bool: True if key was set successfully
        """
        if not openai_available:
            raise ImportError("OpenAI package not installed")

        try:
            # Test the API key by making a simple request
            client = OpenAI(api_key=api_key)

            # Make a test request to validate the key
            client.models.list()

            # Store in app config if valid
            current_app.config['OPENAI_API_KEY'] = api_key
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to set OpenAI API key: {str(e)}")
            return False

    @staticmethod
    def is_authenticated() -> bool:
        """
        Check if OpenAI is properly authenticated without making an API call
        
        Returns:
            bool: True if API key is configured, False otherwise
        """
        return (openai_available and 
                current_app.config.get('OPENAI_API_KEY') is not None)

    @staticmethod
    def get_database_schema() -> str:
        """
        Generate a comprehensive database schema description for OpenAI

        Returns:
            str: Formatted schema description
        """
        if not inspect:
            raise ImportError("SQLAlchemy package not available")

        schema_info = []

        # Get all models with their table names
        model_tables = [
            (User, 'user'),
            (Quote, 'quote'),
            (Policy, 'policy'),
            (PaymentTransaction, 'payment_transaction')
        ]

        for model, table_name in model_tables:
            schema_info.append(f"\nTable: {table_name}")

            # Get column information
            inspector = inspect(db.engine)
            columns = inspector.get_columns(table_name)

            for column in columns:
                col_name = column['name']
                col_type = str(column['type'])
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                pk = "PRIMARY KEY" if column.get('primary_key', False) else ""

                line = f"  - {col_name}: {col_type} {nullable} {pk}".strip()
                schema_info.append(line)

            # Get foreign key information
            foreign_keys = inspector.get_foreign_keys(table_name)
            for fk in foreign_keys:
                constrained = fk['constrained_columns']
                referred_table = fk['referred_table']
                referred_cols = fk['referred_columns']
                fk_info = (f"  - Foreign Key: {constrained} -> "
                           f"{referred_table}.{referred_cols}")
                schema_info.append(fk_info)

        # Add enum information
        schema_info.append("\nEnums:")
        schema_info.append("  - PaymentType: Credit, Debit, Prepaid")

        # Add relationships description
        schema_info.append("\nRelationships:")
        schema_info.append("  - User has many Quotes and Policies")
        schema_info.append("  - Quote belongs to User and has many Policies")
        schema_info.append("  - Policy belongs to User and Quote, "
                           "has many PaymentTransactions")
        schema_info.append("  - PaymentTransaction belongs to Policy")

        return "\n".join(schema_info)

    @staticmethod
    def convert_nl_to_sql(natural_language_query: str) -> dict:
        """
        Convert natural language query to SQL using OpenAI

        Args:
            natural_language_query: The natural language query

        Returns:
            dict: Contains 'sql' query and 'explanation'
        
        Raises:
            ValueError: If OpenAI authentication fails
        """
        # Validate OpenAI authentication
        is_valid, error_msg = OpenAIService._validate_openai_auth()
        if not is_valid:
            raise ValueError(error_msg)

        api_key = current_app.config.get('OPENAI_API_KEY')
        client = OpenAI(api_key=api_key)

        # Get database schema
        schema = OpenAIService.get_database_schema()

        # Create the prompt
        prompt = f"""
You are a SQL expert. Convert the following natural language query to SQL \
based on the database schema provided.

Database Schema:
{schema}

Natural Language Query: {natural_language_query}

Please provide:
1. A valid SQL query
2. A brief explanation of what the query does

Format your response as:
SQL: [your sql query here]
EXPLANATION: [brief explanation here]

Important notes:
- Use proper table and column names from the schema
- Use appropriate JOINs when needed
- Consider using LIMIT for large result sets
- Make sure the query is syntactically correct for SQLite
- Do NOT include semicolons at the end of the SQL query
- Return only the SQL query without any extra formatting or semicolons
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system",
                     "content": "You are a helpful SQL expert assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )

            content = response.choices[0].message.content.strip()

            # Parse the response to extract SQL and explanation
            lines = content.split('\n')
            sql_query = ""
            explanation = ""

            for line in lines:
                if line.startswith('SQL:'):
                    sql_query = line[4:].strip()
                elif line.startswith('EXPLANATION:'):
                    explanation = line[12:].strip()

            return {
                'sql': sql_query,
                'explanation': explanation,
                'raw_response': content
            }
        except Exception as e:
            current_app.logger.error(f"OpenAI API error: {str(e)}")
            raise Exception(f"Failed to convert query: {str(e)}") from e

    @staticmethod
    def execute_sql_query(sql_query: str, limit: int = 100) -> dict:
        """
        Execute a SQL query safely

        Args:
            sql_query: The SQL query to execute
            limit: Maximum number of rows to return

        Returns:
            dict: Query results with data, columns, and metadata
        """
        if not text:
            raise ImportError("SQLAlchemy text function not available")

        try:
            # Clean up the SQL query - remove trailing semicolons
            sql_query = sql_query.strip()
            if sql_query.endswith(';'):
                sql_query = sql_query[:-1]
            # Add LIMIT if not present and it's a SELECT query
            sql_lower = sql_query.lower().strip()
            if sql_lower.startswith('select') and 'limit' not in sql_lower:
                sql_query = f"{sql_query} LIMIT {limit}"

            # Only allow SELECT queries for safety
            if not sql_lower.startswith('select'):
                raise ValueError("Only SELECT queries are allowed")

            # Execute the query
            result = db.session.execute(text(sql_query))

            # Get column names
            columns = list(result.keys()) if result.keys() else []

            # Fetch data
            rows = result.fetchall()

            # Convert to list of dictionaries
            data = []
            for row in rows:
                row_dict = {}
                for i, column in enumerate(columns):
                    row_dict[column] = row[i]
                data.append(row_dict)

            return {
                'data': data,
                'columns': columns,
                'row_count': len(data),
                'query': sql_query
            }

        except Exception as e:
            current_app.logger.error(f"SQL execution error: {str(e)}")
            raise Exception(f"Failed to execute query: {str(e)}")
