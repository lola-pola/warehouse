"""
Feature store models for caching computed features
"""
import enum
from datetime import datetime
from .base import db



class FeatureType(enum.Enum):
    """Enum for different feature types"""
    USER_POLICY_TIME_OF_PURCHASE = "user_policy_time_of_purchase"
    QUOTE_CREATION_TO_BINDING_TIME = "quote_creation_to_binding_time"
    USER_FAILED_TRANSACTION_COUNT = "user_failed_transaction_count"
    PAYMENT_TYPE = "payment_type"


class Feature(db.Model):
    """Feature model representing computed features in the feature store"""
    
    id = db.Column(db.Integer, primary_key=True)
    feature_type = db.Column(db.Enum(FeatureType), nullable=False)
    entity_id = db.Column(db.String(50), nullable=False)  # user_id, quote_id, or payment_transaction_id
    feature_value = db.Column(db.Text, nullable=True)  # JSON string for complex values
    computed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Composite index for fast lookups
    __table_args__ = (
        db.Index('idx_feature_type_entity', 'feature_type', 'entity_id'),
    )
    
    def __repr__(self):
        return f'<Feature {self.feature_type.value} for {self.entity_id}>'


class FeatureMetadata(db.Model):
    """Feature metadata for discovery API"""
    
    id = db.Column(db.Integer, primary_key=True)
    feature_type = db.Column(db.Enum(FeatureType), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)  # user_id, quote_id, payment_transaction_id
    data_type = db.Column(db.String(50), nullable=False)  # datetime, integer, string, etc.
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FeatureMetadata {self.name}>'
