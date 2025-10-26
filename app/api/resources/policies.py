"""
Policy API resources
"""
from flask_restx import Resource, Namespace
from app.models import db, Policy, User, Quote


def create_policy_namespace(api, schemas):
    """Create and configure the policies namespace with all endpoints"""

    policies_ns = Namespace('policies', description='Policy operations')
    policy_schema = schemas['policy_schema']
    policy_create_schema = schemas['policy_create_schema']

    @policies_ns.route('/')
    class PolicyList(Resource):
        @policies_ns.doc('list_policies')
        @policies_ns.marshal_list_with(policy_schema)
        def get(self):
            """Get all policies"""
            policies = Policy.query.all()
            return policies

        @policies_ns.doc('create_policy')
        @policies_ns.expect(policy_create_schema)
        @policies_ns.marshal_with(policy_schema, code=201)
        def post(self):
            """Create a new policy"""
            data = api.payload
            
            # Validate user and quote exist
            user = User.query.get_or_404(data['user_id'])
            quote = Quote.query.get_or_404(data['quote_id'])
            
            # Validate quote belongs to user
            if quote.user_id != data['user_id']:
                policies_ns.abort(400, 'Quote does not belong to the specified user')
            
            # Validate quote is bound
            if not quote.bind_time:
                policies_ns.abort(400, 'Quote must be bound before creating a policy')
            
            policy = Policy(
                user_id=data['user_id'],
                quote_id=data['quote_id']
            )
            db.session.add(policy)
            db.session.commit()
            return policy, 201

    @policies_ns.route('/<int:policy_id>')
    @policies_ns.response(404, 'Policy not found')
    @policies_ns.param('policy_id', 'Policy identifier')
    class PolicyResource(Resource):
        @policies_ns.doc('get_policy')
        @policies_ns.marshal_with(policy_schema)
        def get(self, policy_id):
            """Get a policy by ID"""
            policy = Policy.query.get_or_404(policy_id)
            return policy

    return policies_ns
