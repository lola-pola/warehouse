"""
User API resources
"""
from flask_restx import Resource, Namespace
from app.models import db, User


def create_user_namespace(api, schemas):
    """Create and configure the users namespace with all endpoints"""

    users_ns = Namespace('users', description='User operations')
    user_schema = schemas['user_schema']
    user_create_schema = schemas['user_create_schema']

    @users_ns.route('/')
    class UserList(Resource):
        @users_ns.doc('list_users')
        @users_ns.marshal_list_with(user_schema)
        def get(self):
            """Get all users"""
            users = User.query.all()
            return users

        @users_ns.doc('create_user')
        @users_ns.expect(user_create_schema)
        @users_ns.marshal_with(user_schema, code=201)
        def post(self):
            """Create a new user"""
            data = api.payload
            user = User(
                name=data['name'],
                email=data.get('email')
            )
            db.session.add(user)
            db.session.commit()
            return user, 201

    @users_ns.route('/<int:user_id>')
    @users_ns.response(404, 'User not found')
    @users_ns.param('user_id', 'User identifier')
    class UserResource(Resource):
        @users_ns.doc('get_user')
        @users_ns.marshal_with(user_schema)
        def get(self, user_id):
            """Get a user by ID"""
            user = User.query.get_or_404(user_id)
            return user

        @users_ns.doc('update_user')
        @users_ns.expect(user_create_schema)
        @users_ns.marshal_with(user_schema)
        def put(self, user_id):
            """Update a user"""
            user = User.query.get_or_404(user_id)
            data = api.payload
            user.name = data['name']
            if 'email' in data:
                user.email = data['email']
            db.session.commit()
            return user

        @users_ns.doc('delete_user')
        @users_ns.response(204, 'User deleted')
        def delete(self, user_id):
            """Delete a user"""
            user = User.query.get_or_404(user_id)
            db.session.delete(user)
            db.session.commit()
            return '', 204

    return users_ns
