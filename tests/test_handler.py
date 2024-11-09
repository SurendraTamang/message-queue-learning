import pytest
from datetime import datetime, timedelta
from queue.handler import FailureHandler
from queue.failures import FailureType

@pytest.fixture
def failure_handler():
    return FailureHandler()

class TestFailureHandler:
    def test_handle_timeout_failure(self, failure_handler):
        """Test handling of timeout failures"""
        message = {
            'id': '123',
            'data': {'test': 'data'},
            'status': 'processing',
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = failure_handler.handle_message_failure(message, FailureType.TIMEOUT)
        assert result['status'] == 'retry'
        assert 'next_process_time' in result
        assert result['last_failure']['type'] == 'timeout'

    def test_handle_validation_failure(self, failure_handler):
        """Test handling of validation failures"""
        message = {
            'id': '123',
            'data': {'test': 'data'},
            'status': 'processing',
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = failure_handler.handle_message_failure(message, FailureType.VALIDATION)
        assert result['status'] == 'dead_letter'
        assert result['last_failure']['type'] == 'validation'

    def test_retry_count_exceeded(self, failure_handler):
        """Test handling when retry count is exceeded"""
        message = {
            'id': '123',
            'data': {'test': 'data'},
            'status': 'processing',
            'created_at': datetime.utcnow().isoformat(),
            'failure_count': {'timeout': 5}  # Exceed max retries
        }
        
        result = failure_handler.handle_message_failure(message, FailureType.TIMEOUT)
        assert result['status'] == 'dead_letter'

    def test_network_failure_backoff(self, failure_handler):
        """Test exponential backoff for network failures"""
        message = {
            'id': '123',
            'data': {'test': 'data'},
            'status': 'processing',
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = failure_handler.handle_message_failure(message, FailureType.NETWORK)
        first_retry = result['next_process_time']
        
        result = failure_handler.handle_message_failure(result, FailureType.NETWORK)
        second_retry = result['next_process_time']
        
        # Second retry should be later than first retry
        assert second_retry > first_retry

    def test_business_rule_failure(self, failure_handler):
        """Test handling of business rule violations"""
        message = {
            'id': '123',
            'data': {'test': 'data'},
            'status': 'processing',
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = failure_handler.handle_message_failure(message, FailureType.BUSINESS)
        assert result['status'] == 'dead_letter'
        assert 'next_process_time' not in result

    def test_resource_failure(self, failure_handler):
        """Test handling of resource availability failures"""
        message = {
            'id': '123',
            'data': {'test': 'data'},
            'status': 'processing',
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = failure_handler.handle_message_failure(message, FailureType.RESOURCE)
        assert result['status'] == 'retry'
        assert result['requires_resource_check'] is True