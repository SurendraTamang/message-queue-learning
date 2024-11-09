from enum import Enum
from datetime import datetime, timedelta, UTC
import logging
from typing import Dict, Any
from .failures import FailureType

class FailureHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Configure failure thresholds
        self.timeout_threshold = 30  # seconds
        self.max_retries = {
            FailureType.TIMEOUT: 3,
            FailureType.NETWORK: 5,
            FailureType.DATABASE: 3,
            FailureType.VALIDATION: 1,
            FailureType.RESOURCE: 2,
            FailureType.BUSINESS: 0
        }
        
    def handle_message_failure(self, message: Dict[str, Any], failure_type: FailureType) -> Dict[str, Any]:
        """Handle different types of message failures"""
        failure_count = message.get('failure_count', {})
        failure_count[failure_type.value] = failure_count.get(failure_type.value, 0) + 1
        
        message.update({
            'last_failure': {
                'type': failure_type.value,
                'timestamp': datetime.now(UTC).isoformat(),
                'attempt': failure_count[failure_type.value]
            },
            'failure_count': failure_count
        })

        strategy = self._get_failure_strategy(message, failure_type)
        return self._apply_failure_strategy(message, strategy)

    def _get_failure_strategy(self, message: Dict[str, Any], failure_type: FailureType) -> str:
        """Determine how to handle the failure based on type and history"""
        failure_count = message['failure_count'][failure_type.value]
        max_retries = self.max_retries[failure_type]

        if failure_count > max_retries:
            return 'dead_letter'
        
        if failure_type in [FailureType.VALIDATION, FailureType.BUSINESS]:
            return 'dead_letter'
            
        if failure_type == FailureType.TIMEOUT:
            return 'retry_with_timeout'
            
        if failure_type == FailureType.NETWORK:
            return 'retry_with_backoff'
            
        if failure_type == FailureType.DATABASE:
            return 'retry_with_circuit_breaker'
            
        if failure_type == FailureType.RESOURCE:
            return 'retry_when_available'
            
        return 'retry'

    def _apply_failure_strategy(self, message: Dict[str, Any], strategy: str) -> Dict[str, Any]:
        """Apply the chosen failure handling strategy"""
        if strategy == 'dead_letter':
            message['status'] = 'dead_letter'
            message.pop('next_process_time', None)  # Remove next_process_time for dead letter
            self.logger.error(f"Message {message['id']} moved to dead letter queue")
            
        elif strategy == 'retry_with_timeout':
            delay = min(5 * (2 ** (message['failure_count']['timeout'] - 1)), 300)
            message['next_process_time'] = datetime.now(UTC) + timedelta(seconds=delay)
            message['status'] = 'retry'
            self.logger.info(f"Message {message['id']} scheduled for retry with {delay}s timeout")
            
        elif strategy == 'retry_with_backoff':
            delay = min(10 * (2 ** (message['failure_count']['network'] - 1)), 600)
            message['next_process_time'] = datetime.now(UTC) + timedelta(seconds=delay)
            message['status'] = 'retry'
            self.logger.info(f"Message {message['id']} scheduled for retry with {delay}s backoff")
            
        elif strategy == 'retry_with_circuit_breaker':
            if self._check_circuit_breaker():
                message['next_process_time'] = datetime.now(UTC) + timedelta(minutes=5)
                message['status'] = 'retry'
                self.logger.info(f"Message {message['id']} scheduled for retry after circuit breaker")
            else:
                message['status'] = 'dead_letter'
                message.pop('next_process_time', None)
                self.logger.error(f"Message {message['id']} failed due to open circuit breaker")
                
        elif strategy == 'retry_when_available':
            message['next_process_time'] = datetime.now(UTC) + timedelta(minutes=1)
            message['status'] = 'retry'
            message['requires_resource_check'] = True
            self.logger.info(f"Message {message['id']} waiting for resource availability")
            
        return message

    def _check_circuit_breaker(self) -> bool:
        """Check if circuit breaker allows retries"""
        return True  # Simplified version always allows retries