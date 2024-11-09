import pytest
from datetime import datetime
from queue.manager import QueueSystem
from queue.failures import FailureType

@pytest.fixture
def queue_system():
    return QueueSystem()

class TestQueueSystem:
    def test_enqueue(self, queue_system):
        """Test enqueueing a new message"""
        message = {"data": "test"}
        queue_system.enqueue(message)
        assert len(queue_system.queue) == 1
        assert queue_system.queue[0]['data'] == message
        assert 'id' in queue_system.queue[0]
        assert 'timestamp' in queue_system.queue[0]

    def test_process_message_success(self, queue_system):
        """Test successful message processing"""
        message = {"data": "test"}
        queue_system.enqueue(message)
        result = queue_system.process_message(queue_system.queue[0])
        assert result is True
        assert len(queue_system.queue) == 0
        assert len(queue_system.processing) == 0

    def test_process_message_failure(self, queue_system):
        """Test message processing failure"""
        message = {"data": "test", "force_fail": True}
        queue_system.enqueue(message)
        original_message = queue_system.queue[0]
        result = queue_system.process_message(original_message)
        assert result is False
        assert len(queue_system.queue) == 1  # Message requeued
        assert queue_system.queue[0]['attempt'] == 1

    def test_dead_letter_queue(self, queue_system):
        """Test dead letter queue functionality"""
        message = {"data": "test", "force_fail": True}
        queue_system.enqueue(message)
        message = queue_system.queue[0]
        
        # Force multiple failures
        for _ in range(queue_system.max_retries + 1):
            queue_system.process_message(message)
            if queue_system.queue:
                message = queue_system.queue[0]
        
        assert len(queue_system.dead_letter_queue) == 1
        assert len(queue_system.queue) == 0

    def test_recover_processing_messages(self, queue_system):
        """Test recovery of processing messages"""
        message = {"data": "test"}
        queue_system.enqueue(message)
        msg = queue_system.queue[0]
        queue_system.processing[msg['id']] = msg
        queue_system.queue.remove(msg)
        
        queue_system.recover_processing_messages()
        assert len(queue_system.processing) == 0
        assert len(queue_system.queue) == 1

    def test_monitor_health(self, queue_system):
        """Test health monitoring"""
        message = {"data": "test"}
        queue_system.enqueue(message)
        
        health = queue_system.monitor_health()
        assert health['pending'] == 1
        assert health['processing'] == 0
        assert health['dead_letter'] == 0