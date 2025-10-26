"""
Analytics service layer for business logic
"""
from typing import Dict, Any
from app.models import User, Quote, Policy, PaymentTransaction, PaymentType


class AnalyticsService:
    """Service class for analytics and reporting business logic"""

    @staticmethod
    def get_general_stats() -> Dict[str, Any]:
        """Get general database statistics"""
        total_payments = PaymentTransaction.query.count()
        successful_payments = PaymentTransaction.query.filter_by(success=True).count()
        
        return {
            'total_users': User.query.count(),
            'total_quotes': Quote.query.count(),
            'total_policies': Policy.query.count(),
            'total_payments': total_payments,
            'successful_payments': successful_payments,
            'payment_success_rate': round(
                (successful_payments / total_payments * 100) if total_payments > 0 else 0, 2
            )
        }

    @staticmethod
    def get_payment_stats_by_type() -> Dict[str, Dict[str, Any]]:
        """Get detailed payment statistics by payment type"""
        payment_stats = {}
        
        for payment_type in PaymentType:
            total = PaymentTransaction.query.filter_by(payment_type=payment_type).count()
            successful = PaymentTransaction.query.filter_by(
                payment_type=payment_type, success=True
            ).count()
            
            payment_stats[payment_type.value] = {
                'total': total,
                'successful': successful,
                'failed': total - successful,
                'success_rate': round(
                    (successful / total * 100) if total > 0 else 0, 2
                )
            }
        
        return payment_stats

    @staticmethod
    def get_user_stats() -> Dict[str, Any]:
        """Get user-related statistics"""
        total_users = User.query.count()
        users_with_quotes = User.query.join(Quote).distinct().count()
        users_with_policies = User.query.join(Policy).distinct().count()
        
        return {
            'total_users': total_users,
            'users_with_quotes': users_with_quotes,
            'users_with_policies': users_with_policies,
            'users_without_quotes': total_users - users_with_quotes,
            'conversion_rate': round(
                (users_with_policies / users_with_quotes * 100) 
                if users_with_quotes > 0 else 0, 2
            )
        }

    @staticmethod
    def get_quote_stats() -> Dict[str, Any]:
        """Get quote-related statistics"""
        total_quotes = Quote.query.count()
        bound_quotes = Quote.query.filter(Quote.bind_time.isnot(None)).count()
        bindable_quotes = Quote.query.filter_by(bindable=True).count()
        
        return {
            'total_quotes': total_quotes,
            'bound_quotes': bound_quotes,
            'unbound_quotes': total_quotes - bound_quotes,
            'bindable_quotes': bindable_quotes,
            'bind_rate': round(
                (bound_quotes / total_quotes * 100) if total_quotes > 0 else 0, 2
            )
        }

    @staticmethod
    def get_policy_stats() -> Dict[str, Any]:
        """Get policy-related statistics"""
        total_policies = Policy.query.count()
        policies_with_payments = Policy.query.join(PaymentTransaction).distinct().count()
        
        return {
            'total_policies': total_policies,
            'policies_with_payments': policies_with_payments,
            'policies_without_payments': total_policies - policies_with_payments,
            'payment_adoption_rate': round(
                (policies_with_payments / total_policies * 100) if total_policies > 0 else 0, 2
            )
        }
