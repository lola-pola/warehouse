"""
Feature Store API resources
"""
from datetime import datetime
from flask import request
from flask_restx import Resource, Namespace

from app.models import FeatureType
from app.services.feature_store_service import FeatureStoreService


def create_feature_store_namespace(api, schemas):
    """Create and configure the feature store namespace"""
    
    ns = Namespace('features', description='Feature Store operations')
    
    @ns.route('/inference')
    class FeatureInference(Resource):
        """Feature inference endpoint for real-time single feature requests"""
        
        @ns.expect(schemas['feature_request_schema'])
        @ns.marshal_with(schemas['feature_response_schema'])
        @ns.doc('get_feature_inference')
        def post(self):
            """
            Get a single feature for real-time inference
            
            This endpoint is optimized for low-latency feature serving in production.
            It returns cached features when available or computes them on-demand.
            """
            data = request.get_json()
            
            try:
                # Initialize the feature store service
                feature_service = FeatureStoreService()
                feature_type_str = data.get('feature_type')
                entity_id = data.get('entity_id')
                
                if not feature_type_str or not entity_id:
                    return {
                        'feature_type': feature_type_str,
                        'entity_id': entity_id,
                        'feature_value': None,
                        'computed_at': None,
                        'success': False,
                        'error': 'Missing feature_type or entity_id'
                    }, 400
                
                # Convert string to enum
                feature_type = FeatureType(feature_type_str)
                
                # Get or compute the feature
                feature_value = feature_service.get_or_compute_feature(
                    feature_type, entity_id
                )
                
                # Format the response
                response = {
                    'feature_type': feature_type.value,
                    'entity_id': str(entity_id),
                    'feature_value': feature_value,
                    'computed_at': datetime.utcnow().isoformat(),
                    'success': True
                }
                
                # Handle datetime serialization
                if isinstance(feature_value, datetime):
                    response['feature_value'] = feature_value.isoformat()
                
                return response, 200
                
            except ValueError as e:
                return {
                    'feature_type': data.get('feature_type'),
                    'entity_id': data.get('entity_id'),
                    'feature_value': None,
                    'computed_at': None,
                    'success': False,
                    'error': f'Invalid feature_type: {str(e)}'
                }, 400
            except Exception as e:
                return {
                    'feature_type': data.get('feature_type'),
                    'entity_id': data.get('entity_id'),
                    'feature_value': None,
                    'computed_at': None,
                    'success': False,
                    'error': str(e)
                }, 500
    
    @ns.route('/training')
    class FeatureTraining(Resource):
        """Feature training endpoint for bulk feature requests"""
        
        @ns.expect(schemas['batch_feature_request_schema'])
        @ns.marshal_with(schemas['batch_feature_response_schema'])
        @ns.doc('get_features_training')
        def post(self):
            """
            Get multiple features for training purposes
            
            This endpoint is optimized for bulk feature retrieval used by data scientists
            during model training. It can handle large batches of feature requests.
            """
            data = request.get_json()
            
            try:
                # Initialize the feature store service
                feature_service = FeatureStoreService()
                feature_requests = data.get('features', [])
                
                if not feature_requests:
                    return {
                        'results': [],
                        'total_requested': 0,
                        'total_successful': 0
                    }, 400
                
                # Process batch requests
                results = feature_service.batch_compute_features(feature_requests)
                
                # Count successful results
                successful_count = sum(1 for result in results if result.get('success', False))
                
                # Format datetime values in results
                for result in results:
                    if isinstance(result.get('feature_value'), datetime):
                        result['feature_value'] = result['feature_value'].isoformat()
                    result['computed_at'] = datetime.utcnow().isoformat()
                
                return {
                    'results': results,
                    'total_requested': len(feature_requests),
                    'total_successful': successful_count
                }, 200
                
            except Exception as e:
                return {
                    'results': [],
                    'total_requested': 0,
                    'total_successful': 0,
                    'error': str(e)
                }, 500
    
    @ns.route('/discovery')
    class FeatureDiscovery(Resource):
        """Feature discovery endpoint for listing available features"""
        
        @ns.marshal_list_with(schemas['feature_metadata_schema'])
        @ns.doc('get_feature_discovery')
        def get(self):
            """
            Discover available features
            
            This endpoint returns metadata about all available features in the feature store.
            Data scientists can use this to understand what features are available for training.
            """
            try:
                # Initialize the feature store service
                feature_service = FeatureStoreService()
                metadata_list = feature_service.get_all_feature_metadata()
                return metadata_list, 200
            except Exception as e:
                ns.abort(500, f'Error retrieving feature metadata: {str(e)}')
    
    @ns.route('/extract')
    class FeatureExtraction(Resource):
        """Feature extraction endpoint for batch processing"""
        
        @ns.marshal_with(schemas['feature_extraction_response_schema'])
        @ns.doc('run_feature_extraction')
        def post(self):
            """
            Run batch feature extraction
            
            This endpoint triggers batch processing to extract all features from the data warehouse
            and populate the feature store. This is typically run on a schedule or when new data
            is available in the warehouse.
            """
            try:
                # Initialize the feature store service
                feature_service = FeatureStoreService()
                results = feature_service.batch_extract_all_features()
                
                total_features = sum(results.values())
                
                return {
                    'message': 'Feature extraction completed successfully',
                    'features_extracted': results,
                    'total_features': total_features
                }, 200
                
            except Exception as e:
                return {
                    'message': f'Feature extraction failed: {str(e)}',
                    'features_extracted': {},
                    'total_features': 0
                }, 500
    
    return ns
