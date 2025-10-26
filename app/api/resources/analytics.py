"""
Analytics API resources
"""
from flask_restx import Resource, Namespace
from app.models import User, Quote, Policy, PaymentTransaction, PaymentType


def create_analytics_namespace(api, schemas):
    """Create and configure the analytics namespace with all endpoints"""

    analytics_ns = Namespace('analytics', description='Analytics and reporting')
    analytics_schema = schemas['analytics_schema']

    @analytics_ns.route('/stats')
    class AnalyticsStats(Resource):
        @analytics_ns.doc('get_stats')
        @analytics_ns.marshal_with(analytics_schema)
        def get(self):
            """Get comprehensive database statistics"""
            total_payments = PaymentTransaction.query.count()
            successful_payments = PaymentTransaction.query.filter_by(success=True).count()
            
            stats = {
                'total_users': User.query.count(),
                'total_quotes': Quote.query.count(),
                'total_policies': Policy.query.count(),
                'total_payments': total_payments,
                'successful_payments': successful_payments,
                'payment_success_rate': round(
                    (successful_payments / total_payments * 100) if total_payments > 0 else 0, 2
                )
            }
            return stats

    @analytics_ns.route('/payment-stats')
    class PaymentStats(Resource):
        @analytics_ns.doc('get_payment_stats')
        def get(self):
            """Get detailed payment statistics by type"""
            payment_stats = {}
            for payment_type in PaymentType:
                count = PaymentTransaction.query.filter_by(
                    payment_type=payment_type
                ).count()
                successful = PaymentTransaction.query.filter_by(
                    payment_type=payment_type, success=True
                ).count()
                payment_stats[payment_type.value] = {
                    'total': count,
                    'successful': successful,
                    'failed': count - successful,
                    'success_rate': round(
                        (successful / count * 100) if count > 0 else 0, 2
                    )
                }
            return payment_stats

    @analytics_ns.route('/user-stats')
    class UserStats(Resource):
        @analytics_ns.doc('get_user_stats')
        def get(self):
            """Get user-related statistics"""
            users_with_quotes = User.query.join(Quote).distinct().count()
            users_with_policies = User.query.join(Policy).distinct().count()
            
            return {
                'total_users': User.query.count(),
                'users_with_quotes': users_with_quotes,
                'users_with_policies': users_with_policies,
                'users_without_quotes': User.query.count() - users_with_quotes,
                'conversion_rate': round(
                    (users_with_policies / users_with_quotes * 100) 
                    if users_with_quotes > 0 else 0, 2
                )
            }

    return analytics_ns
