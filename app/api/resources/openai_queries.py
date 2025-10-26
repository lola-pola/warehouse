"""
OpenAI API resources for natural language to SQL conversion
"""
from flask import request
try:
    from flask_restx import Resource, Namespace, fields
except ImportError:
    Resource = None
    Namespace = None
    fields = None

from app.services.openai_service import OpenAIService


def create_openai_namespace(api, schemas):
    """Create and configure the OpenAI namespace with all endpoints"""

    if not Namespace:
        raise ImportError("Flask-RESTX not available")

    openai_ns = Namespace(
        'openai',
        description='OpenAI natural language to SQL operations')

    # Define models for request/response
    openai_key_model = openai_ns.model('OpenAIKey', {
        'api_key': fields.String(required=True,
                                 description='OpenAI API key')
    })

    nl_query_model = openai_ns.model('NaturalLanguageQuery', {
        'query': fields.String(required=True,
                               description='Natural language query'),
        'limit': fields.Integer(default=100,
                                description='Maximum number of rows to return')
    })

    sql_response_model = openai_ns.model('SQLResponse', {
        'sql': fields.String(description='Generated SQL query'),
        'explanation': fields.String(description='Explanation of the query'),
        'data': fields.List(fields.Raw, description='Query results'),
        'columns': fields.List(fields.String, description='Column names'),
        'row_count': fields.Integer(description='Number of rows returned')
    })

    schema_response_model = openai_ns.model('SchemaResponse', {
        'schema': fields.String(description='Database schema description')
    })

    auth_status_model = openai_ns.model('AuthStatus', {
        'authenticated': fields.Boolean(description='Whether OpenAI is authenticated'),
        'message': fields.String(description='Status message')
    })

    sql_query_model = openai_ns.model('SQLQuery', {
        'sql': fields.String(required=True,
                             description='SQL query to execute'),
        'limit': fields.Integer(default=100,
                                description='Maximum number of rows to return')
    })

    @openai_ns.route('/set-key')
    class SetOpenAIKey(Resource):
        """Set OpenAI API key"""

        @openai_ns.expect(openai_key_model)
        @openai_ns.doc('set_openai_key')
        def post(self):
            """Set the OpenAI API key"""
            try:
                data = request.get_json()
                api_key = data.get('api_key')

                if not api_key:
                    return {'error': 'API key is required'}, 400

                success = OpenAIService.set_api_key(api_key)

                if success:
                    return {'message': 'OpenAI API key set successfully'}, 200
                else:
                    return {'error': 'Invalid OpenAI API key'}, 400

            except Exception as e:
                return {'error': str(e)}, 500

    @openai_ns.route('/status')
    class AuthenticationStatus(Resource):
        """Check OpenAI authentication status"""

        @openai_ns.marshal_with(auth_status_model)
        @openai_ns.doc('check_auth_status')
        def get(self):
            """Check if OpenAI is properly authenticated"""
            try:
                is_authenticated = OpenAIService.is_authenticated()
                
                if is_authenticated:
                    # Validate the actual API key
                    is_valid, error_msg = OpenAIService._validate_openai_auth()
                    if is_valid:
                        return {
                            'authenticated': True,
                            'message': 'OpenAI API is properly configured and authenticated'
                        }, 200
                    else:
                        return {
                            'authenticated': False,
                            'message': error_msg
                        }, 401
                else:
                    return {
                        'authenticated': False,
                        'message': 'OpenAI API key not configured. Please set your API key using the /openai/set-key endpoint.'
                    }, 401

            except Exception as e:
                return {
                    'authenticated': False,
                    'message': f'Error checking authentication: {str(e)}'
                }, 500

    @openai_ns.route('/schema')
    class GetDatabaseSchema(Resource):
        """Get database schema information"""

        @openai_ns.marshal_with(schema_response_model)
        @openai_ns.doc('get_database_schema')
        def get(self):
            """Get the database schema description"""
            try:
                schema = OpenAIService.get_database_schema()
                return {'schema': schema}, 200

            except Exception as e:
                return {'error': str(e)}, 500

    @openai_ns.route('/query')
    class NaturalLanguageQuery(Resource):
        """Convert natural language to SQL and execute"""

        @openai_ns.expect(nl_query_model)
        @openai_ns.marshal_with(sql_response_model)
        @openai_ns.doc('natural_language_query')
        def post(self):
            """Convert natural language query to SQL and execute it"""
            try:
                # Check if OpenAI is authenticated first
                if not OpenAIService.is_authenticated():
                    return {
                        'error': 'OpenAI not configured. Please set your API key first using the /openai/set-key endpoint.'
                    }, 401

                data = request.get_json()
                nl_query = data.get('query')
                limit = data.get('limit', 100)

                if not nl_query:
                    return {'error': 'Query is required'}, 400

                # Convert natural language to SQL
                conversion_result = OpenAIService.convert_nl_to_sql(nl_query)

                if not conversion_result.get('sql'):
                    return {'error': 'Failed to generate SQL query'}, 400

                # Execute the SQL query
                execution_result = OpenAIService.execute_sql_query(
                    conversion_result['sql'],
                    limit
                )

                # Combine results
                response = {
                    'sql': conversion_result['sql'],
                    'explanation': conversion_result['explanation'],
                    'data': execution_result['data'],
                    'columns': execution_result['columns'],
                    'row_count': execution_result['row_count']
                }

                return response, 200

            except ValueError as e:
                # Authentication and validation errors
                if "authentication" in str(e).lower() or "api key" in str(e).lower():
                    return {'error': str(e)}, 401
                return {'error': str(e)}, 400
            except Exception as e:
                return {'error': str(e)}, 500

    @openai_ns.route('/sql')
    class DirectSQLQuery(Resource):
        """Execute SQL query directly"""

        @openai_ns.expect(sql_query_model)
        @openai_ns.marshal_with(sql_response_model)
        @openai_ns.doc('execute_sql_query')
        def post(self):
            """Execute a SQL query directly"""
            try:
                data = request.get_json()
                sql_query = data.get('sql')
                limit = data.get('limit', 100)

                if not sql_query:
                    return {'error': 'SQL query is required'}, 400

                # Execute the SQL query
                result = OpenAIService.execute_sql_query(sql_query, limit)

                response = {
                    'sql': result['query'],
                    'explanation': 'Direct SQL execution',
                    'data': result['data'],
                    'columns': result['columns'],
                    'row_count': result['row_count']
                }

                return response, 200

            except ValueError as e:
                return {'error': str(e)}, 400
            except Exception as e:
                return {'error': str(e)}, 500

    return openai_ns
