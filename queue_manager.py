import time
from datetime import datetime
import json
from typing import Dict, Any
import logging

class QueueSystem:
    def __init__(self):
        self.queue = []
        self.processing = {}  # Track in-progress items
        self.dead_letter_queue = []  # Store failed messages DLQ
        self.max_retries = 3
        self.retry_delays = [5, 15, 30]  # Increasing delays between retries (seconds)
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def enqueue(self, message: Dict[str, Any]) -> None:
        """Add message to queue with metadata"""
        message_wrapper = {
            'id': str(time.time()),
            'data': message,
            'attempt': 0,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'pending'
        }
        self.queue.append(message_wrapper)
        self.logger.info(f"Message {message_wrapper['id']} enqueued")

    def process_message(self, message: Dict[str, Any]) -> bool:
        """Simulate message processing with potential failures"""
        try:
            # Move to processing state
            message['status'] = 'processing'
            self.processing[message['id']] = message
            
            # Simulate actual processing
            # In real system, this would be your business logic
            if message['attempt'] >= self.max_retries:
                raise Exception("Max retries exceeded")
                
            # Process successfully
            del self.processing[message['id']]
            message['status'] = 'completed'
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
        
        if message['attempt'] < self.max_retries:
            # Calculate delay for next retry
            delay = self.retry_delays[min(message['attempt'] - 1, len(self.retry_delays) - 1)]
            message['next_retry'] = time.time() + delay
            self.queue.append(message)  # Re-queue for retry
            self.logger.warning(
                f"Message {message['id']} failed, attempt {message['attempt']}/{self.max_retries}. "
                f"Retrying in {delay} seconds"
            )
        else:
            # Move to dead letter queue after max retries
            self.dead_letter_queue.append(message)
            self.logger.error(
                f"Message {message['id']} failed permanently after {self.max_retries} attempts. "
                f"Moved to dead letter queue. Error: {error}"
            )
        
        # Clean up processing tracking
        if message['id'] in self.processing:
            del self.processing[message['id']]

    def recover_processing_messages(self) -> None:
        """Recover messages that were being processed during a crash"""
        for message in self.processing.values():
            message['status'] = 'failed'
            message['error'] = 'System crash during processing'
            self.handle_failure(message, 'System crash recovery')
        self.processing.clear()

    def monitor_health(self) -> Dict[str, int]:
        """Return queue health metrics"""
        return {
            'pending': len(self.queue),
            'processing': len(self.processing),
            'dead_letter': len(self.dead_letter_queue)
        }