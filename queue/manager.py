from datetime import datetime, UTC
import logging
from typing import Dict, Any, List, Tuple
import time
from .failures import FailureType
from .handler import FailureHandler

class QueueSystem:
    def __init__(self):
        self.queue: List[Dict[str, Any]] = []
        self.processing: Dict[str, Dict[str, Any]] = {}
        self.dead_letter_queue: List[Dict[str, Any]] = []
        self.max_retries = 3
        self.failure_handler = FailureHandler()
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def enqueue(self, message: Dict[str, Any]) -> None:
        """Add message to queue with metadata"""
        message_wrapper = {
            'id': str(time.time()),
            'data': message,
            'attempt': 0,
            'timestamp': datetime.now(UTC).isoformat(),
            'status': 'pending'
        }
        self.queue.append(message_wrapper)
        self.logger.info(f"Message {message_wrapper['id']} enqueued")

    def process_message(self, message: Dict[str, Any]) -> bool:
        """Process a message from the queue"""
        try:
            # Move to processing state
            message['status'] = 'processing'
            self.processing[message['id']] = message
            
            # Simulate processing - in real system, this would be business logic
            if message.get('data', {}).get('force_fail'):
                raise Exception("Forced failure for testing")
            
            # Successfully processed
            message['status'] = 'completed'
            self.queue.remove(message)  # Remove from main queue
            del self.processing[message['id']]  # Remove from processing
            self.logger.info(f"Message {message['id']} processed successfully")
            return True
            
        except Exception as e:
            self.handle_failure(message, str(e))
            return False

    def handle_failure(self, message: Dict[str, Any], error: str) -> None:
        """Handle failed message processing"""
        message['status'] = 'failed'
        message['error'] = error
        message['attempt'] += 1
        
        if message['attempt'] >= self.max_retries:
            self.dead_letter_queue.append(message)
            if message['id'] in self.processing:
                del self.processing[message['id']]
            if message in self.queue:
                self.queue.remove(message)
            self.logger.error(
                f"Message {message['id']} failed permanently after {self.max_retries} attempts. "
                f"Moved to dead letter queue. Error: {error}"
            )
        else:
            self.logger.warning(
                f"Message {message['id']} failed, attempt {message['attempt']}/{self.max_retries}. "
                f"Retrying in 5 seconds"
            )

    def recover_processing_messages(self) -> None:
        """Recover messages that were being processed during a crash"""
        processing_items = list(self.processing.values())  # Create a copy of values
        for message in processing_items:
            message['status'] = 'failed'
            message['error'] = 'System crash recovery'
            self.handle_failure(message, 'System crash recovery')

    def monitor_health(self) -> Dict[str, int]:
        """Return queue health metrics"""
        return {
            'pending': len(self.queue),
            'processing': len(self.processing),
            'dead_letter': len(self.dead_letter_queue)
        }