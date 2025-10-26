"""
API Schemas for request/response validation and Swagger documentation
"""
from flask_restx import fields


def create_api_schemas(api):
    """Create and return all API schemas for Swagger documentation"""

    # User schemas
    user_schema = api.model('User', {
        'id': fields.Integer(readonly=True, description='User ID'),
        'name': fields.String(required=True, description='User name'),
        'email': fields.String(description='User email address')
    })

    user_create_schema = api.model('UserCreate', {
        'name': fields.String(required=True, description='User name'),
        'email': fields.String(description='User email address')
    })

    # Quote schemas
    quote_schema = api.model('Quote', {
        'id': fields.Integer(readonly=True, description='Quote ID'),
        'user_id': fields.Integer(required=True, description='User ID'),
        'create_time': fields.DateTime(description='Quote creation time'),
        'bind_time': fields.DateTime(description='Quote binding time'),
        'bindable': fields.Boolean(description='Whether quote is bindable')
    })

    quote_create_schema = api.model('QuoteCreate', {
        'user_id': fields.Integer(required=True, description='User ID'),
        'bindable': fields.Boolean(description='Whether quote is bindable')
    })

    # Policy schemas
    policy_schema = api.model('Policy', {
        'id': fields.Integer(readonly=True, description='Policy ID'),
        'user_id': fields.Integer(required=True, description='User ID'),
        'quote_id': fields.Integer(required=True, description='Quote ID')
    })

    policy_create_schema = api.model('PolicyCreate', {
        'user_id': fields.Integer(required=True, description='User ID'),
        'quote_id': fields.Integer(required=True, description='Quote ID')
    })

    # Payment schemas
    payment_schema = api.model('PaymentTransaction', {
        'id': fields.Integer(readonly=True, description='Payment transaction ID'),
        'time': fields.DateTime(required=True, description='Transaction time'),
        'payment_type': fields.String(
            enum=['CREDIT', 'DEBIT', 'PREPAID'], 
            description='Payment type'
        ),
        'policy_id': fields.Integer(required=True, description='Policy ID'),
        'success': fields.Boolean(description='Transaction success status')
    })

    payment_create_schema = api.model('PaymentTransactionCreate', {
        'payment_type': fields.String(
            enum=['CREDIT', 'DEBIT', 'PREPAID'], 
            required=True,
            description='Payment type'
        ),
        'policy_id': fields.Integer(required=True, description='Policy ID')
    })

    # Analytics schemas
    analytics_schema = api.model('Analytics', {
        'total_users': fields.Integer(description='Total number of users'),
        'total_quotes': fields.Integer(description='Total number of quotes'),
        'total_policies': fields.Integer(description='Total number of policies'),
        'total_payments': fields.Integer(description='Total number of payments'),
        'successful_payments': fields.Integer(description='Number of successful payments'),
        'payment_success_rate': fields.Float(description='Payment success rate percentage')
    })

    # Feature Store schemas
    feature_metadata_schema = api.model('FeatureMetadata', {
        'feature_type': fields.String(description='Feature type identifier'),
        'name': fields.String(description='Human-readable feature name'),
        'description': fields.String(description='Feature description'),
        'entity_type': fields.String(description='Entity type (user_id, quote_id, payment_transaction_id)'),
        'data_type': fields.String(description='Data type (datetime, integer, string)'),
        'created_at': fields.String(description='Feature metadata creation timestamp')
    })

    feature_request_schema = api.model('FeatureRequest', {
        'feature_type': fields.String(
            required=True,
            enum=['user_policy_time_of_purchase', 'quote_creation_to_binding_time', 
                  'user_failed_transaction_count', 'payment_type'],
            description='Type of feature to retrieve'
        ),
        'entity_id': fields.String(required=True, description='Entity ID (user_id, quote_id, or payment_transaction_id)')
    })

    feature_response_schema = api.model('FeatureResponse', {
        'feature_type': fields.String(description='Feature type identifier'),
        'entity_id': fields.String(description='Entity ID'),
        'feature_value': fields.Raw(description='Feature value (type depends on feature)'),
        'computed_at': fields.String(description='When the feature was computed'),
        'success': fields.Boolean(description='Whether the request was successful')
    })

    batch_feature_request_schema = api.model('BatchFeatureRequest', {
        'features': fields.List(
            fields.Nested(feature_request_schema),
            required=True,
            description='List of feature requests'
        )
    })

    batch_feature_response_schema = api.model('BatchFeatureResponse', {
        'results': fields.List(
            fields.Nested(feature_response_schema),
            description='List of feature results'
        ),
        'total_requested': fields.Integer(description='Total number of features requested'),
        'total_successful': fields.Integer(description='Total number of successful feature retrievals')
    })

    feature_extraction_response_schema = api.model('FeatureExtractionResponse', {
        'message': fields.String(description='Extraction status message'),
        'features_extracted': fields.Raw(description='Count of features extracted by type'),
        'total_features': fields.Integer(description='Total number of features extracted')
    })

    return {
        'user_schema': user_schema,
        'user_create_schema': user_create_schema,
        'quote_schema': quote_schema,
        'quote_create_schema': quote_create_schema,
        'policy_schema': policy_schema,
        'policy_create_schema': policy_create_schema,
        'payment_schema': payment_schema,
        'payment_create_schema': payment_create_schema,
        'analytics_schema': analytics_schema,
        'feature_metadata_schema': feature_metadata_schema,
        'feature_request_schema': feature_request_schema,
        'feature_response_schema': feature_response_schema,
        'batch_feature_request_schema': batch_feature_request_schema,
        'batch_feature_response_schema': batch_feature_response_schema,
        'feature_extraction_response_schema': feature_extraction_response_schema
    }
