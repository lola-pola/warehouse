"""
API Resources package
"""
from .users import create_user_namespace
from .quotes import create_quote_namespace
from .policies import create_policy_namespace
from .payments import create_payment_namespace
from .analytics import create_analytics_namespace
from .openai_queries import create_openai_namespace

__all__ = [
    'create_user_namespace',
    'create_quote_namespace',
    'create_policy_namespace',
    'create_payment_namespace',
    'create_analytics_namespace',
    'create_openai_namespace'
]
