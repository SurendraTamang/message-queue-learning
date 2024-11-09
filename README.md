# Resilient Queue System
A robust message queue implementation with comprehensive failure handling and recovery mechanisms.

## Features
- Message tracking and state management
- Configurable retry mechanisms
- Dead Letter Queue (DLQ) for failed messages
- Multiple failure type handling
- Circuit breaker pattern implementation
- Extensive logging and monitoring
- Crash recovery capabilities

## Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/resilient-queue

# Install dependencies
pip install -r requirements.txt
```

## Project Structure
```
resilient-queue/
├── queue/
│   ├── __init__.py
│   ├── manager.py          # Main queue implementation
│   ├── handler.py          # Failure handling logic
│   ├── failures.py         # Failure type definitions
│   └── utils.py            # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_manager.py
│   └── test_handler.py
├── requirements.txt
└── README.md
```

## Usage Examples

### Basic Queue Operations
```python
from queue.manager import QueueSystem

# Initialize queue
queue = QueueSystem()

# Add message to queue
message = {"user_id": 123, "action": "process_payment"}
queue.enqueue(message)

# Process messages
queue.process_message(message)
```

### Handling Failures
```python
from queue.handler import FailureHandler
from queue.failures import FailureType

# Initialize failure handler
handler = FailureHandler()

# Handle specific failure type
handler.handle_message_failure(message, FailureType.NETWORK)
```

## Failure Types
1. **TIMEOUT**
   - Description: Processing exceeded time limit
   - Default retries: 3
   - Strategy: Exponential backoff

2. **NETWORK**
   - Description: Network communication issues
   - Default retries: 5
   - Strategy: Progressive delay

3. **DATABASE**
   - Description: Database operation failures
   - Default retries: 3
   - Strategy: Circuit breaker pattern

4. **VALIDATION**
   - Description: Invalid message format/content
   - Default retries: 1
   - Strategy: Move to DLQ

5. **RESOURCE**
   - Description: System resource unavailability
   - Default retries: 2
   - Strategy: Wait for availability

6. **BUSINESS**
   - Description: Business rule violations
   - Default retries: 0
   - Strategy: Immediate DLQ

## Configuration
Key configuration parameters in `config.py`:

```python
# Retry configuration
MAX_RETRIES = {
    'TIMEOUT': 3,
    'NETWORK': 5,
    'DATABASE': 3,
    'VALIDATION': 1,
    'RESOURCE': 2,
    'BUSINESS': 0
}

# Timing configuration
TIMEOUT_THRESHOLD = 30  # seconds
BASE_RETRY_DELAY = 5   # seconds
MAX_RETRY_DELAY = 300  # seconds

# Monitoring
ENABLE_LOGGING = True
LOG_LEVEL = 'INFO'
```

## Monitoring and Health Checks
Monitor queue health using the built-in metrics:

```python
health_metrics = queue.monitor_health()
print(f"Queue Status: {health_metrics}")
```

Metrics include:
- Pending messages count
- Processing messages count
- Dead letter queue size
- Failure rates by type
- Average processing time

## Error Recovery
The system provides automatic recovery from crashes:

```python
# After system restart
queue.recover_processing_messages()
```

## Logging
Logs are written to `queue.log` by default. Configure logging in `config.py`:

```python
LOGGING_CONFIG = {
    'filename': 'queue.log',
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}
```

## Testing
Run the test suite:

```bash
python -m pytest tests/
```

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Support
For support, please open an issue in the GitHub repository or contact the maintainers.

## Future Enhancements
- [ ] Redis backend support
- [ ] Cluster support for distributed processing
- [ ] Real-time monitoring dashboard
- [ ] Custom failure handlers
- [ ] Message priority queues