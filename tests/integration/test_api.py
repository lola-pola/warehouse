"""
Integration tests for API endpoints
"""
import json
from datetime import datetime


class TestUserAPI:
    """Test User API endpoints"""
    
    def test_get_users_empty(self, client):
        """Test getting users when database is empty"""
        response = client.get('/api/v1/users/')
        assert response.status_code == 200
        assert response.json == []
    
    def test_create_user(self, client):
        """Test creating a user via API"""
        user_data = {
            'name': 'John Doe',
            'email': 'john@example.com'
        }
        
        response = client.post('/api/v1/users/', 
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = response.json
        assert data['name'] == 'John Doe'
        assert data['email'] == 'john@example.com'
        assert 'id' in data
    
    def test_get_user_by_id(self, client, sample_user):
        """Test getting a specific user"""
        response = client.get(f'/api/v1/users/{sample_user.id}')
        
        assert response.status_code == 200
        data = response.json
        assert data['id'] == sample_user.id
        assert data['name'] == sample_user.name
    
    def test_get_nonexistent_user(self, client):
        """Test getting non-existent user"""
        response = client.get('/api/v1/users/999')
        assert response.status_code == 404
    
    def test_update_user(self, client, sample_user):
        """Test updating a user"""
        update_data = {
            'name': 'Updated Name',
            'email': 'updated@example.com'
        }
        
        response = client.put(f'/api/v1/users/{sample_user.id}',
                            data=json.dumps(update_data),
                            content_type='application/json')
        
        assert response.status_code == 200
        data = response.json
        assert data['name'] == 'Updated Name'
        assert data['email'] == 'updated@example.com'
    
    def test_delete_user(self, client, sample_user):
        """Test deleting a user"""
        response = client.delete(f'/api/v1/users/{sample_user.id}')
        assert response.status_code == 204
        
        # Verify user is deleted
        response = client.get(f'/api/v1/users/{sample_user.id}')
        assert response.status_code == 404


class TestQuoteAPI:
    """Test Quote API endpoints"""
    
    def test_create_quote(self, client, sample_user):
        """Test creating a quote via API"""
        quote_data = {
            'user_id': sample_user.id,
            'bindable': True
        }
        
        response = client.post('/api/v1/quotes/',
                             data=json.dumps(quote_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = response.json
        assert data['user_id'] == sample_user.id
        assert data['bindable'] is True
        assert 'create_time' in data
        assert 'id' in data
    
    def test_create_quote_invalid_user(self, client):
        """Test creating quote with invalid user"""
        quote_data = {
            'user_id': 999,
            'bindable': True
        }
        
        response = client.post('/api/v1/quotes/',
                             data=json.dumps(quote_data),
                             content_type='application/json')
        
        assert response.status_code == 404
    
    def test_bind_quote(self, client, sample_quote):
        """Test binding a quote"""
        response = client.patch(f'/api/v1/quotes/{sample_quote.id}')
        
        assert response.status_code == 200
        data = response.json
        assert data['bind_time'] is not None
    
    def test_get_quote(self, client, sample_quote):
        """Test getting a specific quote"""
        response = client.get(f'/api/v1/quotes/{sample_quote.id}')
        
        assert response.status_code == 200
        data = response.json
        assert data['id'] == sample_quote.id
        assert data['user_id'] == sample_quote.user_id


class TestPolicyAPI:
    """Test Policy API endpoints"""
    
    def test_create_policy(self, client, sample_user, bound_quote):
        """Test creating a policy via API"""
        policy_data = {
            'user_id': sample_user.id,
            'quote_id': bound_quote.id
        }
        
        response = client.post('/api/v1/policies/',
                             data=json.dumps(policy_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = response.json
        assert data['user_id'] == sample_user.id
        assert data['quote_id'] == bound_quote.id
        assert 'id' in data
    
    def test_create_policy_unbound_quote(self, client, sample_user, sample_quote):
        """Test creating policy with unbound quote"""
        policy_data = {
            'user_id': sample_user.id,
            'quote_id': sample_quote.id
        }
        
        response = client.post('/api/v1/policies/',
                             data=json.dumps(policy_data),
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_get_policy(self, client, sample_policy):
        """Test getting a specific policy"""
        response = client.get(f'/api/v1/policies/{sample_policy.id}')
        
        assert response.status_code == 200
        data = response.json
        assert data['id'] == sample_policy.id
        assert data['user_id'] == sample_policy.user_id


class TestPaymentAPI:
    """Test Payment API endpoints"""
    
    def test_create_payment(self, client, sample_policy):
        """Test creating a payment via API"""
        payment_data = {
            'payment_type': 'CREDIT',
            'policy_id': sample_policy.id
        }
        
        response = client.post('/api/v1/payments/',
                             data=json.dumps(payment_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = response.json
        assert data['payment_type'] == 'CREDIT'
        assert data['policy_id'] == sample_policy.id
        assert 'success' in data
        assert 'time' in data
        assert 'id' in data
    
    def test_create_payment_invalid_type(self, client, sample_policy):
        """Test creating payment with invalid type"""
        payment_data = {
            'payment_type': 'INVALID',
            'policy_id': sample_policy.id
        }
        
        response = client.post('/api/v1/payments/',
                             data=json.dumps(payment_data),
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_get_payment(self, client, sample_payment):
        """Test getting a specific payment"""
        response = client.get(f'/api/v1/payments/{sample_payment.id}')
        
        assert response.status_code == 200
        data = response.json
        assert data['id'] == sample_payment.id
        assert data['policy_id'] == sample_payment.policy_id


class TestAnalyticsAPI:
    """Test Analytics API endpoints"""
    
    def test_get_stats(self, client, sample_user, sample_quote, sample_policy, sample_payment):
        """Test getting general statistics"""
        response = client.get('/api/v1/analytics/stats')
        
        assert response.status_code == 200
        data = response.json
        
        required_fields = [
            'total_users', 'total_quotes', 'total_policies', 
            'total_payments', 'successful_payments', 'payment_success_rate'
        ]
        
        for field in required_fields:
            assert field in data
            assert isinstance(data[field], (int, float))
    
    def test_get_payment_stats(self, client, sample_payment):
        """Test getting payment statistics by type"""
        response = client.get('/api/v1/analytics/payment-stats')
        
        assert response.status_code == 200
        data = response.json
        
        assert isinstance(data, dict)
        assert 'Credit' in data
        assert 'Debit' in data
        assert 'Prepaid' in data
        
        # Check structure
        for payment_type, stats in data.items():
            assert 'total' in stats
            assert 'successful' in stats
            assert 'failed' in stats
            assert 'success_rate' in stats
    
    def test_get_user_stats(self, client, sample_user):
        """Test getting user statistics"""
        response = client.get('/api/v1/analytics/user-stats')
        
        assert response.status_code == 200
        data = response.json
        
        required_fields = [
            'total_users', 'users_with_quotes', 'users_with_policies',
            'users_without_quotes', 'conversion_rate'
        ]
        
        for field in required_fields:
            assert field in data
            assert isinstance(data[field], (int, float))
