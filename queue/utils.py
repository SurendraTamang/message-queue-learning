import time
import uuid
from typing import Dict, Any
from datetime import datetime

def generate_message_id() -> str:
    """Generate a unique message ID"""
    return str(uuid.uuid4())

def create_message_wrapper(data: Dict[str, Any]) -> Dict[str, Any]:
    """Wrap message data with metadata"""
    return {
        'id': generate_message_id(),
        'data': data,
        'timestamp': datetime.utcnow().isoformat(),
        'attempt': 0,
        'status': 'pending',
        'failures': []
    }

def calculate_backoff_delay(attempt: int, base_delay: int = 5, max_delay: int = 300) -> int:
    """Calculate exponential backoff delay"""
    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
    return delay

def is_message_expired(message: Dict[str, Any], timeout_seconds: int = 300) -> bool:
    """Check if message has expired based on timestamp"""
    created_time = datetime.fromisoformat(message['timestamp'])
    elapsed = (datetime.utcnow() - created_time).total_seconds()
    return elapsed > timeout_seconds