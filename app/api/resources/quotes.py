"""
Quote API resources
"""
from datetime import datetime
from flask_restx import Resource, Namespace
from app.models import db, Quote, User


def create_quote_namespace(api, schemas):
    """Create and configure the quotes namespace with all endpoints"""

    quotes_ns = Namespace('quotes', description='Quote operations')
    quote_schema = schemas['quote_schema']
    quote_create_schema = schemas['quote_create_schema']

    @quotes_ns.route('/')
    class QuoteList(Resource):
        @quotes_ns.doc('list_quotes')
        @quotes_ns.marshal_list_with(quote_schema)
        def get(self):
            """Get all quotes"""
            quotes = Quote.query.all()
            return quotes

        @quotes_ns.doc('create_quote')
        @quotes_ns.expect(quote_create_schema)
        @quotes_ns.marshal_with(quote_schema, code=201)
        def post(self):
            """Create a new quote"""
            data = api.payload
            
            # Validate user exists
            user = User.query.get_or_404(data['user_id'])
            
            quote = Quote(
                user_id=data['user_id'],
                create_time=datetime.utcnow(),
                bindable=data.get('bindable', True)
            )
            db.session.add(quote)
            db.session.commit()
            return quote, 201

    @quotes_ns.route('/<int:quote_id>')
    @quotes_ns.response(404, 'Quote not found')
    @quotes_ns.param('quote_id', 'Quote identifier')
    class QuoteResource(Resource):
        @quotes_ns.doc('get_quote')
        @quotes_ns.marshal_with(quote_schema)
        def get(self, quote_id):
            """Get a quote by ID"""
            quote = Quote.query.get_or_404(quote_id)
            return quote

        @quotes_ns.doc('bind_quote')
        @quotes_ns.marshal_with(quote_schema)
        def patch(self, quote_id):
            """Bind a quote (set bind_time)"""
            quote = Quote.query.get_or_404(quote_id)
            if not quote.bindable:
                quotes_ns.abort(400, 'Quote is not bindable')
            
            quote.bind_time = datetime.utcnow()
            db.session.commit()
            return quote

    return quotes_ns
