# Feature Store Documentation

## Overview

This feature store provides a minimal working implementation that solves the problem of feature duplication between Data Scientists (training time) and Backend Engineers (inference time). It offers three main APIs to serve features consistently across both use cases.

## Architecture

### Components

1. **Feature Store Models** - Cache computed features in a real-time data store
2. **Feature Calculation Service** - Extract and compute features from warehouse tables
3. **Batch Processor** - Run scheduled feature extraction from warehouse to feature store
4. **Three APIs**:
   - **Inference API** - Single feature lookup for real-time serving
   - **Training API** - Bulk feature retrieval for data scientists
   - **Discovery API** - Feature catalog and metadata

### Data Flow

```
Data Warehouse Tables (User, Quote, Policy, PaymentTransaction)
                    ↓
            Batch Feature Extraction
                    ↓
              Feature Store Cache
                    ↓
        ┌─────────────────────────────────┐
        ├─ Inference API (Real-time)     │
        ├─ Training API (Bulk)           │
        └─ Discovery API (Metadata)      │
```

## Available Features

### 1. User Policy Time of Purchase
- **Key**: `user_id`
- **Returns**: Policy payment transaction time (datetime)
- **Description**: For a given user_id, returns when they made their policy payment

### 2. Time from Quote Creation to Binding
- **Key**: `quote_id` 
- **Returns**: Time difference in seconds (integer)
- **Description**: For a given quote_id, returns the difference between binding time and creation time

### 3. Count of User Failed Transactions
- **Key**: `user_id`
- **Returns**: Number of failed transactions (integer)
- **Description**: For a given user_id, returns the count of failed payment transactions

### 4. Type of Payment
- **Key**: `payment_transaction_id`
- **Returns**: Payment type (string: "Credit", "Debit", "Prepaid")
- **Description**: For a given payment transaction ID, returns the payment type

## API Endpoints

### Base URL
```
http://localhost:25000/api/v1/features
```

### 1. Feature Discovery API

**Endpoint**: `GET /discovery`

**Description**: Discover available features and their metadata

**Response**:
```json
[
  {
    "feature_type": "user_policy_time_of_purchase",
    "name": "User Policy Time of Purchase",
    "description": "For a given user_id, returns the policy payment transaction time",
    "entity_type": "user_id",
    "data_type": "datetime",
    "created_at": "2025-01-01T00:00:00"
  }
]
```

### 2. Feature Inference API (Real-time)

**Endpoint**: `POST /inference`

**Description**: Get a single feature for real-time inference

**Request**:
```json
{
  "feature_type": "user_policy_time_of_purchase",
  "entity_id": "123"
}
```

**Response**:
```json
{
  "feature_type": "user_policy_time_of_purchase",
  "entity_id": "123",
  "feature_value": "2025-01-15T10:30:00",
  "computed_at": "2025-01-20T12:00:00",
  "success": true
}
```

### 3. Feature Training API (Bulk)

**Endpoint**: `POST /training`

**Description**: Get multiple features for training purposes

**Request**:
```json
{
  "features": [
    {
      "feature_type": "user_policy_time_of_purchase",
      "entity_id": "123"
    },
    {
      "feature_type": "user_failed_transaction_count",
      "entity_id": "123"
    }
  ]
}
```

**Response**:
```json
{
  "results": [
    {
      "feature_type": "user_policy_time_of_purchase",
      "entity_id": "123",
      "feature_value": "2025-01-15T10:30:00",
      "computed_at": "2025-01-20T12:00:00",
      "success": true
    },
    {
      "feature_type": "user_failed_transaction_count", 
      "entity_id": "123",
      "feature_value": 2,
      "computed_at": "2025-01-20T12:00:00",
      "success": true
    }
  ],
  "total_requested": 2,
  "total_successful": 2
}
```

### 4. Feature Extraction API (Batch Processing)

**Endpoint**: `POST /extract`

**Description**: Run batch feature extraction from warehouse to feature store

**Response**:
```json
{
  "message": "Feature extraction completed successfully",
  "features_extracted": {
    "user_policy_time_of_purchase": 150,
    "quote_creation_to_binding_time": 75,
    "user_failed_transaction_count": 150,
    "payment_type": 200
  },
  "total_features": 575
}
```

## Usage Examples

### For Data Scientists (Training Time)

```python
import requests

# 1. Discover available features
response = requests.get("http://localhost:25000/api/v1/features/discovery")
features = response.json()
print(f"Available features: {[f['name'] for f in features]}")

# 2. Get features for training dataset
user_ids = [1, 2, 3, 4, 5]
feature_requests = []

for user_id in user_ids:
    feature_requests.extend([
        {
            "feature_type": "user_policy_time_of_purchase",
            "entity_id": str(user_id)
        },
        {
            "feature_type": "user_failed_transaction_count", 
            "entity_id": str(user_id)
        }
    ])

response = requests.post(
    "http://localhost:25000/api/v1/features/training",
    json={"features": feature_requests}
)

training_data = response.json()
# Process training_data['results'] for model training
```

### For Backend Engineers (Inference Time)

```python
import requests

def get_user_features(user_id):
    """Get features for a user during inference"""
    
    # Get user policy time
    response = requests.post(
        "http://localhost:25000/api/v1/features/inference",
        json={
            "feature_type": "user_policy_time_of_purchase",
            "entity_id": str(user_id)
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            return result['feature_value']
    
    return None

# Use in production API
user_policy_time = get_user_features(user_id=123)
```

### Batch Processing (DevOps/Scheduled Jobs)

```python
import requests

def run_feature_extraction():
    """Run scheduled feature extraction"""
    
    response = requests.post("http://localhost:25000/api/v1/features/extract")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Extracted {result['total_features']} features")
        return True
    else:
        print(f"Extraction failed: {response.text}")
        return False

# Run this on a schedule (e.g., daily cron job)
if __name__ == "__main__":
    run_feature_extraction()
```

## Benefits

### 1. **Eliminates Code Duplication**
- Data Scientists and Backend Engineers use the same feature computation logic
- Features are computed once and cached for reuse

### 2. **Consistency**
- Training and inference use identical feature values
- Reduces model drift due to feature computation differences

### 3. **Performance**
- Real-time inference API optimized for low latency
- Bulk training API optimized for throughput
- Features are pre-computed and cached

### 4. **Discoverability**
- Discovery API allows teams to find and reuse existing features
- Prevents duplicate feature development

### 5. **Maintainability**
- Single source of truth for feature definitions
- Easy to add new features or modify existing ones

## Implementation Details

### Feature Computation Logic

Each feature is computed using SQL queries on the warehouse tables:

1. **User Policy Time of Purchase**: Joins PaymentTransaction → Policy → User
2. **Quote Creation to Binding Time**: Simple datetime arithmetic on Quote table
3. **User Failed Transaction Count**: Aggregation query with failure condition
4. **Payment Type**: Direct lookup from PaymentTransaction table

### Caching Strategy

- Features are computed on-demand if not cached
- Batch extraction pre-populates cache for all entities
- Cache includes computation timestamp for freshness tracking

### Error Handling

- Graceful degradation when features can't be computed
- Detailed error messages in API responses
- Batch operations continue even if individual features fail

## Testing

Run the test script to verify all APIs:

```bash
python test_feature_store.py
```

This will test:
- Feature discovery
- Batch extraction
- Single feature inference
- Bulk feature training

## Future Enhancements

1. **Feature Versioning**: Track feature definition changes over time
2. **Feature Monitoring**: Monitor feature drift and data quality
3. **Real-time Updates**: Stream updates from warehouse to feature store
4. **Advanced Caching**: TTL-based cache invalidation
5. **Feature Lineage**: Track feature dependencies and transformations
