"""
Feature store service for computing and managing features
"""
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from sqlalchemy import func, and_

from app.models import (
    db, User, Quote, Policy, PaymentTransaction, PaymentType,
    Feature, FeatureType, FeatureMetadata
)


class FeatureStoreService:
    """Service for computing and managing features in the feature store"""
    
    def __init__(self):
        """Initialize feature metadata on service creation"""
        self._ensure_feature_metadata()
    
    def _ensure_feature_metadata(self):
        """Ensure feature metadata exists in the database"""
        metadata_configs = [
            {
                'feature_type': FeatureType.USER_POLICY_TIME_OF_PURCHASE,
                'name': 'User Policy Time of Purchase',
                'description': 'For a given user_id, returns the policy payment transaction time',
                'entity_type': 'user_id',
                'data_type': 'datetime'
            },
            {
                'feature_type': FeatureType.QUOTE_CREATION_TO_BINDING_TIME,
                'name': 'Time from Quote Creation to Binding',
                'description': 'For a given quote_id, returns the difference between binding time and creation time in seconds',
                'entity_type': 'quote_id',
                'data_type': 'integer'
            },
            {
                'feature_type': FeatureType.USER_FAILED_TRANSACTION_COUNT,
                'name': 'Count of User Failed Transactions',
                'description': 'For a given user_id, returns the number of failed payment transactions',
                'entity_type': 'user_id',
                'data_type': 'integer'
            },
            {
                'feature_type': FeatureType.PAYMENT_TYPE,
                'name': 'Type of Payment',
                'description': 'For a given payment_transaction_id, returns the payment type',
                'entity_type': 'payment_transaction_id',
                'data_type': 'string'
            }
        ]
        
        for config in metadata_configs:
            existing = FeatureMetadata.query.filter_by(
                feature_type=config['feature_type']
            ).first()
            
            if not existing:
                metadata = FeatureMetadata(**config)
                db.session.add(metadata)
        
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
    
    def compute_user_policy_time_of_purchase(self, user_id: int) -> Optional[datetime]:
        """
        Compute User Policy Time of Purchase feature
        Returns the policy payment transaction time for a given user_id
        """
        # Get the most recent successful payment transaction for the user's policies
        result = db.session.query(PaymentTransaction.time).join(
            Policy, PaymentTransaction.policy_id == Policy.id
        ).filter(
            and_(
                Policy.user_id == user_id,
                PaymentTransaction.success == True
            )
        ).order_by(PaymentTransaction.time.desc()).first()
        

        return result[0] if result else None
    
    def compute_quote_creation_to_binding_time(self, quote_id: int) -> Optional[int]:
        """
        Compute Time from Quote Creation to Binding feature
        Returns the difference between binding time and creation time in seconds
        """
        quote = Quote.query.filter_by(id=quote_id).first()
        
        if not quote or not quote.create_time or not quote.bind_time:
            return None
        
        time_diff = quote.bind_time - quote.create_time
        return int(time_diff.total_seconds())
    
    def compute_user_failed_transaction_count(self, user_id: int) -> int:
        """
        Compute Count of User Failed Transactions feature
        Returns the number of failed payment transactions for a given user_id
        """
        count = db.session.query(func.count(PaymentTransaction.id)).join(
            Policy, PaymentTransaction.policy_id == Policy.id
        ).filter(
            and_(
                Policy.user_id == user_id,
                PaymentTransaction.success == False
            )
        ).scalar()
        
        return count or 0
    
    def compute_payment_type(self, payment_transaction_id: int) -> Optional[str]:
        """
        Compute Type of Payment feature
        Returns the payment type for a given payment_transaction_id
        """
        transaction = PaymentTransaction.query.filter_by(id=payment_transaction_id).first()
        
        if not transaction or not transaction.payment_type:
            return None
        
        return transaction.payment_type.value
    
    def compute_feature(self, feature_type: FeatureType, entity_id: Union[int, str]) -> Any:
        """
        Compute a specific feature based on feature type and entity ID
        
        Args:
            feature_type: The type of feature to compute
            entity_id: The entity ID (user_id, quote_id, or payment_transaction_id)
        
        Returns:
            The computed feature value
        """
        entity_id_int = int(entity_id)
        
        if feature_type == FeatureType.USER_POLICY_TIME_OF_PURCHASE:
            return self.compute_user_policy_time_of_purchase(entity_id_int)
        elif feature_type == FeatureType.QUOTE_CREATION_TO_BINDING_TIME:
            return self.compute_quote_creation_to_binding_time(entity_id_int)
        elif feature_type == FeatureType.USER_FAILED_TRANSACTION_COUNT:
            return self.compute_user_failed_transaction_count(entity_id_int)
        elif feature_type == FeatureType.PAYMENT_TYPE:
            return self.compute_payment_type(entity_id_int)
        else:
            raise ValueError(f"Unknown feature type: {feature_type}")
    
    def store_feature(self, feature_type: FeatureType, entity_id: Union[int, str], 
                     feature_value: Any) -> Feature:
        """
        Store a computed feature in the feature store
        
        Args:
            feature_type: The type of feature
            entity_id: The entity ID
            feature_value: The computed feature value
        
        Returns:
            The stored Feature object
        """
        # Convert feature value to JSON string for storage
        if isinstance(feature_value, datetime):
            value_str = feature_value.isoformat()
        elif feature_value is None:
            value_str = None
        else:
            value_str = json.dumps(feature_value)
        
        # Check if feature already exists and update it
        existing_feature = Feature.query.filter_by(
            feature_type=feature_type,
            entity_id=str(entity_id)
        ).first()
        
        if existing_feature:
            existing_feature.feature_value = value_str
            existing_feature.computed_at = datetime.utcnow()
            feature = existing_feature
        else:
            feature = Feature(
                feature_type=feature_type,
                entity_id=str(entity_id),
                feature_value=value_str,
                computed_at=datetime.utcnow()
            )
            db.session.add(feature)
        
        db.session.commit()
        return feature
    
    def get_feature(self, feature_type: FeatureType, entity_id: Union[int, str]) -> Optional[Any]:
        """
        Get a feature from the feature store
        
        Args:
            feature_type: The type of feature
            entity_id: The entity ID
        
        Returns:
            The feature value or None if not found
        """
        feature = Feature.query.filter_by(
            feature_type=feature_type,
            entity_id=str(entity_id)
        ).first()
        
        if not feature or feature.feature_value is None:
            return None
        
        # Parse the stored JSON value back to appropriate type
        if feature_type == FeatureType.USER_POLICY_TIME_OF_PURCHASE:
            return datetime.fromisoformat(feature.feature_value)
        elif feature_type in [FeatureType.QUOTE_CREATION_TO_BINDING_TIME, 
                             FeatureType.USER_FAILED_TRANSACTION_COUNT]:
            return json.loads(feature.feature_value)
        elif feature_type == FeatureType.PAYMENT_TYPE:
            return json.loads(feature.feature_value)
        else:
            return json.loads(feature.feature_value)
    
    def compute_and_store_feature(self, feature_type: FeatureType, 
                                 entity_id: Union[int, str]) -> Any:
        """
        Compute and store a feature in one operation
        
        Args:
            feature_type: The type of feature to compute
            entity_id: The entity ID
        
        Returns:
            The computed feature value
        """
        feature_value = self.compute_feature(feature_type, entity_id)
        self.store_feature(feature_type, entity_id, feature_value)
        return feature_value
    
    def get_or_compute_feature(self, feature_type: FeatureType, 
                              entity_id: Union[int, str], 
                              force_recompute: bool = False) -> Any:
        """
        Get a feature from store or compute it if not available
        
        Args:
            feature_type: The type of feature
            entity_id: The entity ID
            force_recompute: Whether to force recomputation even if cached
        
        Returns:
            The feature value
        """
        if not force_recompute:
            cached_value = self.get_feature(feature_type, entity_id)
            if cached_value is not None:
                return cached_value
        
        return self.compute_and_store_feature(feature_type, entity_id)
    
    def batch_compute_features(self, feature_requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Compute multiple features in batch
        
        Args:
            feature_requests: List of dicts with 'feature_type' and 'entity_id' keys
        
        Returns:
            List of dicts with feature results
        """
        results = []
        
        for request in feature_requests:
            try:
                feature_type = request['feature_type']
                entity_id = request['entity_id']
                
                if isinstance(feature_type, str):
                    feature_type = FeatureType(feature_type)
                
                feature_value = self.get_or_compute_feature(feature_type, entity_id)
                
                results.append({
                    'feature_type': feature_type.value,
                    'entity_id': str(entity_id),
                    'feature_value': feature_value,
                    'success': True
                })
            except Exception as e:
                results.append({
                    'feature_type': request.get('feature_type', 'unknown'),
                    'entity_id': request.get('entity_id', 'unknown'),
                    'feature_value': None,
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def get_all_feature_metadata(self) -> List[Dict[str, Any]]:
        """
        Get metadata for all available features
        
        Returns:
            List of feature metadata dictionaries
        """
        metadata_list = FeatureMetadata.query.all()
        
        return [
            {
                'feature_type': metadata.feature_type.value,
                'name': metadata.name,
                'description': metadata.description,
                'entity_type': metadata.entity_type,
                'data_type': metadata.data_type,
                'created_at': metadata.created_at.isoformat()
            }
            for metadata in metadata_list
        ]
    
    def batch_extract_all_features(self) -> Dict[str, int]:
        """
        Extract all features for all entities in batch
        This is the main batch processing function
        
        Returns:
            Dictionary with counts of processed features by type
        """
        results = {
            'user_policy_time_of_purchase': 0,
            'quote_creation_to_binding_time': 0,
            'user_failed_transaction_count': 0,
            'payment_type': 0
        }
        
        # Extract User Policy Time of Purchase for all users
        users = User.query.all()
        for user in users:
            try:
                self.compute_and_store_feature(
                    FeatureType.USER_POLICY_TIME_OF_PURCHASE, 
                    user.id
                )
                results['user_policy_time_of_purchase'] += 1
            except Exception:
                pass  # Skip failed computations
        
        # Extract Quote Creation to Binding Time for all quotes
        quotes = Quote.query.all()
        for quote in quotes:
            try:
                self.compute_and_store_feature(
                    FeatureType.QUOTE_CREATION_TO_BINDING_TIME,
                    quote.id
                )
                results['quote_creation_to_binding_time'] += 1
            except Exception:
                pass
        
        # Extract User Failed Transaction Count for all users
        for user in users:
            try:
                self.compute_and_store_feature(
                    FeatureType.USER_FAILED_TRANSACTION_COUNT,
                    user.id
                )
                results['user_failed_transaction_count'] += 1
            except Exception:
                pass
        
        # Extract Payment Type for all payment transactions
        transactions = PaymentTransaction.query.all()
        for transaction in transactions:
            try:
                self.compute_and_store_feature(
                    FeatureType.PAYMENT_TYPE,
                    transaction.id
                )
                results['payment_type'] += 1
            except Exception:
                pass
        
        return results
