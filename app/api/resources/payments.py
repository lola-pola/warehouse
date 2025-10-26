"""
Payment API resources
"""
import random
from datetime import datetime
from flask_restx import Resource, Namespace
from app.models import db, PaymentTransaction, PaymentType, Policy


def create_payment_namespace(api, schemas):
    """Create and configure the payments namespace with all endpoints"""

    payments_ns = Namespace(
        'payments', 
        description='Payment transaction operations'
    )
    payment_schema = schemas['payment_schema']
    payment_create_schema = schemas['payment_create_schema']

    @payments_ns.route('/')
    class PaymentList(Resource):
        @payments_ns.doc('list_payments')
        @payments_ns.marshal_list_with(payment_schema)
        def get(self):
            """Get all payment transactions"""
            payments = PaymentTransaction.query.all()
            return payments

        @payments_ns.doc('create_payment')
        @payments_ns.expect(payment_create_schema)
        @payments_ns.marshal_with(payment_schema, code=201)
        def post(self):
            """Create a new payment transaction"""
            data = api.payload
            
            # Validate policy exists
            policy = Policy.query.get_or_404(data['policy_id'])
            
            # Convert string to enum
            payment_type = PaymentType(data['payment_type'])
            
            # Simulate payment processing (random success/failure)
            success = random.choice([True, False])
            
            payment = PaymentTransaction(
                time=datetime.utcnow(),
                payment_type=payment_type,
                policy_id=data['policy_id'],
                success=success
            )
            db.session.add(payment)
            db.session.commit()
            return payment, 201

    @payments_ns.route('/<int:payment_id>')
    @payments_ns.response(404, 'Payment not found')
    @payments_ns.param('payment_id', 'Payment transaction identifier')
    class PaymentResource(Resource):
        @payments_ns.doc('get_payment')
        @payments_ns.marshal_with(payment_schema)
        def get(self, payment_id):
            """Get a payment transaction by ID"""
            payment = PaymentTransaction.query.get_or_404(payment_id)
            return payment

    return payments_ns
