"""
API package for the data warehouse
"""
from .schemas import create_api_schemas
from .resources import (
    create_user_namespace,
    create_quote_namespace,
    create_policy_namespace,
    create_payment_namespace,
    create_analytics_namespace,
    create_openai_namespace,
    create_feature_store_namespace
)

__all__ = [
    'create_api_schemas',
    'create_user_namespace',
    'create_quote_namespace',
    'create_policy_namespace',
    'create_payment_namespace',
    'create_analytics_namespace',
    'create_openai_namespace',
    'create_feature_store_namespace'
]
