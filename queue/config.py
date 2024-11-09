import logging

# Queue Configuration
MAX_QUEUE_SIZE = 10000
PROCESSING_TIMEOUT = 30  # seconds

# Retry Configuration
MAX_RETRIES = {
    'TIMEOUT': 3,
    'NETWORK': 5,
    'DATABASE': 3,
    'VALIDATION': 1,
    'RESOURCE': 2,
    'BUSINESS': 0
}

# Timing Configuration
BASE_RETRY_DELAY = 5   # seconds
MAX_RETRY_DELAY = 300  # seconds

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'queue.log',
            'formatter': 'standard',
            'level': logging.INFO,
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': logging.INFO,
        }
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file'],
            'level': logging.INFO,
            'propagate': True
        }
    }
}