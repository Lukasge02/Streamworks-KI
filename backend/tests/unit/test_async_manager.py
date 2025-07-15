"""
Async Manager Unit Tests
Comprehensive testing for async task management and stability
"""
import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta, timezone

from app.core.async_manager import (
    AsyncTaskManager,
    TaskStatus,
    TaskInfo,
    AsyncTaskContext,
    safe_gather,
    run_with_retries,
    managed_task,
    task_manager
)


class TestTaskInfo:
    """Test TaskInfo dataclass"""
    
    def test_task_info_creation(self):
        """Test TaskInfo creation with defaults"""
        task_info = TaskInfo(task_id="test_123", name="test_task")
        
        assert task_info.task_id == "test_123"
        assert task_info.name == "test_task"
        assert task_info.status == TaskStatus.PENDING
        assert isinstance(task_info.created_at, datetime)
        assert task_info.retry_count == 0
        assert task_info.max_retries == 3
        assert task_info.timeout_seconds == 300.0
    
    def test_task_info_with_custom_values(self):
        """Test TaskInfo with custom values"""
        custom_time = datetime.now(timezone.utc)
        task_info = TaskInfo(
            task_id="custom_task",
            name="custom_name",
            status=TaskStatus.RUNNING,
            created_at=custom_time,
            max_retries=5,
            timeout_seconds=600.0,
            metadata={"key": "value"}
        )
        
        assert task_info.task_id == "custom_task"
        assert task_info.status == TaskStatus.RUNNING
        assert task_info.created_at == custom_time
        assert task_info.max_retries == 5
        assert task_info.timeout_seconds == 600.0
        assert task_info.metadata["key"] == "value"


@pytest.mark.asyncio
class TestAsyncTaskManager:
    """Test AsyncTaskManager functionality"""
    
    async def setup_method(self):
        """Setup for each test"""
        self.manager = AsyncTaskManager(
            max_concurrent_tasks=5,
            max_queue_size=10,
            default_timeout=30.0,
            cleanup_interval=5.0
        )
        await self.manager.start()
    
    async def teardown_method(self):
        """Cleanup after each test"""
        await self.manager.stop(timeout=10.0)
    
    async def test_manager_initialization(self):
        """Test manager initialization"""
        assert self.manager.max_concurrent_tasks == 5
        assert self.manager.max_queue_size == 10
        assert self.manager.default_timeout == 30.0
        assert self.manager._running
    
    async def test_submit_simple_task(self):
        """Test submitting a simple task"""
        async def simple_task():
            await asyncio.sleep(0.1)
            return "completed"
        
        task_id = await self.manager.submit_task(simple_task(), name="simple_test")
        assert task_id is not None
        assert task_id.startswith("task_")
        
        # Wait for completion
        result = await self.manager.wait_for_task(task_id, timeout=5.0)
        assert result == "completed"
        
        # Check task info
        task_info = await self.manager.get_task_status(task_id)
        assert task_info.status == TaskStatus.COMPLETED
        assert task_info.result == "completed"
    
    async def test_submit_task_with_timeout(self):
        """Test task timeout handling"""
        async def slow_task():
            await asyncio.sleep(10.0)  # Longer than timeout
            return "should_not_complete"
        
        task_id = await self.manager.submit_task(
            slow_task(), 
            name="slow_test",
            timeout=0.5  # Short timeout
        )
        
        with pytest.raises(asyncio.TimeoutError):
            await self.manager.wait_for_task(task_id, timeout=2.0)
        
        # Check task status
        task_info = await self.manager.get_task_status(task_id)
        assert task_info.status == TaskStatus.TIMEOUT
    
    async def test_submit_task_with_error(self):
        """Test task error handling"""
        async def failing_task():
            await asyncio.sleep(0.1)
            raise ValueError("Test error")
        
        task_id = await self.manager.submit_task(failing_task(), name="failing_test")
        
        with pytest.raises(ValueError):
            await self.manager.wait_for_task(task_id, timeout=5.0)
        
        # Check task status
        task_info = await self.manager.get_task_status(task_id)
        assert task_info.status == TaskStatus.FAILED
        assert "Test error" in task_info.error
    
    async def test_task_retry_mechanism(self):
        """Test task retry functionality"""
        call_count = 0
        
        async def flaky_task():
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # Fail twice, succeed on third try
                raise RuntimeError(f"Attempt {call_count} failed")
            return f"success_on_attempt_{call_count}"
        
        task_id = await self.manager.submit_task(
            flaky_task(), 
            name="flaky_test",
            max_retries=3
        )
        
        result = await self.manager.wait_for_task(task_id, timeout=10.0)
        assert result == "success_on_attempt_3"
        assert call_count == 3
        
        # Check task info
        task_info = await self.manager.get_task_status(task_id)
        assert task_info.status == TaskStatus.COMPLETED
        assert task_info.retry_count == 2  # 3 attempts = 2 retries
    
    async def test_task_retry_exhausted(self):
        """Test task retry exhaustion"""
        async def always_failing_task():
            raise RuntimeError("Always fails")
        
        task_id = await self.manager.submit_task(
            always_failing_task(), 
            name="always_failing",
            max_retries=2
        )
        
        with pytest.raises(RuntimeError):
            await self.manager.wait_for_task(task_id, timeout=10.0)
        
        # Check task status
        task_info = await self.manager.get_task_status(task_id)
        assert task_info.status == TaskStatus.FAILED
        assert task_info.retry_count == 2
    
    async def test_concurrent_task_limit(self):
        """Test concurrent task limiting"""
        # Submit more tasks than the semaphore allows
        async def slow_task(task_num):
            await asyncio.sleep(1.0)
            return f"task_{task_num}"
        
        task_ids = []
        start_time = time.time()
        
        # Submit 8 tasks (more than max_concurrent_tasks=5)
        for i in range(8):
            task_id = await self.manager.submit_task(
                slow_task(i), 
                name=f"concurrent_test_{i}"
            )
            task_ids.append(task_id)
        
        # Wait for all to complete
        results = []
        for task_id in task_ids:
            result = await self.manager.wait_for_task(task_id, timeout=10.0)
            results.append(result)
        
        end_time = time.time()
        
        # Should take at least 2 seconds (2 batches of 1 second each)
        assert end_time - start_time >= 1.5
        assert len(results) == 8
    
    async def test_queue_size_limit(self):
        """Test queue size limiting"""
        # Fill up the queue
        async def dummy_task():
            await asyncio.sleep(10.0)  # Long running
        
        task_ids = []
        
        # Fill the queue to capacity
        for i in range(self.manager.max_queue_size):
            task_id = await self.manager.submit_task(dummy_task(), name=f"queue_test_{i}")
            task_ids.append(task_id)
        
        # Next submission should fail
        with pytest.raises(RuntimeError, match="Task queue full"):
            await self.manager.submit_task(dummy_task(), name="overflow_test")
        
        # Cancel all tasks
        for task_id in task_ids:
            await self.manager.cancel_task(task_id)
    
    async def test_cancel_task(self):
        """Test task cancellation"""
        async def cancellable_task():
            try:
                await asyncio.sleep(10.0)
                return "should_not_complete"
            except asyncio.CancelledError:
                return "cancelled"
        
        task_id = await self.manager.submit_task(cancellable_task(), name="cancel_test")
        
        # Let it start
        await asyncio.sleep(0.1)
        
        # Cancel the task
        cancelled = await self.manager.cancel_task(task_id)
        assert cancelled
        
        # Check task status
        task_info = await self.manager.get_task_status(task_id)
        assert task_info.status == TaskStatus.CANCELLED
    
    async def test_manager_statistics(self):
        """Test manager statistics"""
        # Submit some tasks
        async def quick_task(result):
            await asyncio.sleep(0.1)
            return result
        
        task_ids = []
        for i in range(3):
            task_id = await self.manager.submit_task(quick_task(f"result_{i}"), name=f"stats_test_{i}")
            task_ids.append(task_id)
        
        # Wait for completion
        for task_id in task_ids:
            await self.manager.wait_for_task(task_id, timeout=5.0)
        
        # Check statistics
        stats = self.manager.get_stats()
        assert stats["total_tasks"] >= 3
        assert stats["completed_tasks"] >= 3
        assert stats["current_tasks"] == 0  # All should be completed
        assert stats["avg_execution_time"] > 0
    
    async def test_graceful_shutdown(self):
        """Test graceful manager shutdown"""
        # Submit some long-running tasks
        async def long_task():
            await asyncio.sleep(5.0)
            return "completed"
        
        task_ids = []
        for i in range(3):
            task_id = await self.manager.submit_task(long_task(), name=f"shutdown_test_{i}")
            task_ids.append(task_id)
        
        # Start shutdown
        await self.manager.stop(timeout=2.0)
        
        # Manager should be stopped
        assert not self.manager._running
        
        # Tasks should be cancelled
        for task_id in task_ids:
            task_info = await self.manager.get_task_status(task_id)
            assert task_info.status == TaskStatus.CANCELLED


@pytest.mark.asyncio
class TestAsyncTaskContext:
    """Test AsyncTaskContext functionality"""
    
    async def setup_method(self):
        """Setup for each test"""
        self.manager = AsyncTaskManager(max_concurrent_tasks=3)
        await self.manager.start()
    
    async def teardown_method(self):
        """Cleanup after each test"""
        await self.manager.stop()
    
    async def test_context_manager_success(self):
        """Test successful context manager usage"""
        async def quick_task(value):
            await asyncio.sleep(0.1)
            return value
        
        async with AsyncTaskContext(self.manager) as ctx:
            task_id1 = await ctx.submit(quick_task("result1"), name="ctx_test1")
            task_id2 = await ctx.submit(quick_task("result2"), name="ctx_test2")
            
            results = await ctx.wait_all(timeout=5.0)
        
        assert len(results) == 2
        assert "result1" in results
        assert "result2" in results
    
    async def test_context_manager_with_exception(self):
        """Test context manager with exception handling"""
        async def failing_task():
            await asyncio.sleep(0.1)
            raise ValueError("Test error")
        
        async def normal_task():
            await asyncio.sleep(2.0)  # Should be cancelled
            return "should_not_complete"
        
        with pytest.raises(ValueError):
            async with AsyncTaskContext(self.manager) as ctx:
                await ctx.submit(normal_task(), name="normal")
                await ctx.submit(failing_task(), name="failing")
                raise ValueError("Context error")
        
        # Tasks should be cancelled due to context exception
        await asyncio.sleep(0.5)  # Let cancellation propagate


@pytest.mark.asyncio
class TestUtilityFunctions:
    """Test utility functions"""
    
    async def setup_method(self):
        """Setup for each test"""
        # Use the global task manager for these tests
        if not task_manager._running:
            await task_manager.start()
    
    async def test_safe_gather(self):
        """Test safe_gather utility"""
        async def quick_task(value):
            await asyncio.sleep(0.1)
            return value
        
        async def failing_task():
            await asyncio.sleep(0.1)
            raise ValueError("Test error")
        
        results = await safe_gather(
            quick_task("success1"),
            failing_task(),
            quick_task("success2"),
            timeout=5.0
        )
        
        assert len(results) == 3
        assert results[0] == "success1"
        assert isinstance(results[1], ValueError)
        assert results[2] == "success2"
    
    async def test_run_with_retries(self):
        """Test run_with_retries utility"""
        call_count = 0
        
        async def flaky_coro():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError(f"Attempt {call_count}")
            return "success"
        
        # This should work but we need to wait for task completion
        task_id = await run_with_retries(
            flaky_coro(),
            max_retries=3,
            timeout=10.0,
            name="retry_test"
        )
        
        result = await task_manager.wait_for_task(task_id, timeout=15.0)
        assert result == "success"
        assert call_count == 3
    
    async def test_managed_task_decorator(self):
        """Test managed_task decorator"""
        call_count = 0
        
        @managed_task(timeout=5.0, max_retries=2)
        async def decorated_task(value):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)
            return f"decorated_{value}"
        
        result = await decorated_task("test")
        assert result == "decorated_test"
        assert call_count == 1


@pytest.mark.asyncio
class TestAsyncManagerIntegration:
    """Integration tests for async manager"""
    
    async def test_memory_management(self):
        """Test memory management and cleanup"""
        manager = AsyncTaskManager(
            max_concurrent_tasks=2,
            cleanup_interval=1.0  # Fast cleanup for testing
        )
        await manager.start()
        
        try:
            # Submit many small tasks
            async def tiny_task(i):
                await asyncio.sleep(0.01)
                return i
            
            task_ids = []
            for i in range(20):
                task_id = await manager.submit_task(tiny_task(i), name=f"tiny_{i}")
                task_ids.append(task_id)
            
            # Wait for all tasks
            for task_id in task_ids:
                await manager.wait_for_task(task_id, timeout=5.0)
            
            # Wait for cleanup
            await asyncio.sleep(2.0)
            
            # Check that old tasks are cleaned up
            stats = manager.get_stats()
            assert stats["memory_tasks"] < 20  # Some should be cleaned up
            
        finally:
            await manager.stop()
    
    async def test_error_resilience(self):
        """Test error resilience and recovery"""
        manager = AsyncTaskManager(max_concurrent_tasks=3)
        await manager.start()
        
        try:
            # Mix of successful and failing tasks
            async def mixed_task(should_fail):
                await asyncio.sleep(0.1)
                if should_fail:
                    raise RuntimeError("Intentional failure")
                return "success"
            
            task_ids = []
            
            # Submit mix of tasks
            for i in range(10):
                should_fail = i % 3 == 0  # Every 3rd task fails
                task_id = await manager.submit_task(
                    mixed_task(should_fail), 
                    name=f"mixed_{i}"
                )
                task_ids.append(task_id)
            
            # Collect results
            successes = 0
            failures = 0
            
            for task_id in task_ids:
                try:
                    await manager.wait_for_task(task_id, timeout=5.0)
                    successes += 1
                except RuntimeError:
                    failures += 1
            
            # Should have both successes and failures
            assert successes > 0
            assert failures > 0
            assert successes + failures == 10
            
            # Manager should still be functional
            stats = manager.get_stats()
            assert stats["total_tasks"] >= 10
            assert stats["completed_tasks"] > 0
            assert stats["failed_tasks"] > 0
            
        finally:
            await manager.stop()
    
    async def test_concurrent_managers(self):
        """Test multiple concurrent managers"""
        manager1 = AsyncTaskManager(max_concurrent_tasks=2)
        manager2 = AsyncTaskManager(max_concurrent_tasks=2)
        
        await manager1.start()
        await manager2.start()
        
        try:
            async def manager_task(manager_id, value):
                await asyncio.sleep(0.1)
                return f"manager_{manager_id}_{value}"
            
            # Submit tasks to both managers
            task1_id = await manager1.submit_task(
                manager_task(1, "test"), 
                name="manager1_test"
            )
            task2_id = await manager2.submit_task(
                manager_task(2, "test"), 
                name="manager2_test"
            )
            
            # Both should complete successfully
            result1 = await manager1.wait_for_task(task1_id, timeout=5.0)
            result2 = await manager2.wait_for_task(task2_id, timeout=5.0)
            
            assert result1 == "manager_1_test"
            assert result2 == "manager_2_test"
            
        finally:
            await manager1.stop()
            await manager2.stop()


@pytest.mark.performance
@pytest.mark.asyncio
class TestAsyncManagerPerformance:
    """Performance tests for async manager"""
    
    async def test_task_submission_performance(self):
        """Test task submission performance"""
        manager = AsyncTaskManager(max_concurrent_tasks=10)
        await manager.start()
        
        try:
            async def noop_task():
                return "done"
            
            start_time = time.time()
            
            # Submit many tasks quickly
            task_ids = []
            for i in range(100):
                task_id = await manager.submit_task(noop_task(), name=f"perf_test_{i}")
                task_ids.append(task_id)
            
            submission_time = time.time() - start_time
            
            # Wait for all tasks
            start_wait = time.time()
            for task_id in task_ids:
                await manager.wait_for_task(task_id, timeout=10.0)
            wait_time = time.time() - start_wait
            
            # Performance assertions (adjust based on hardware)
            assert submission_time < 1.0  # Should submit 100 tasks in under 1 second
            assert wait_time < 5.0  # Should complete 100 simple tasks in under 5 seconds
            
            print(f"Submission time: {submission_time:.3f}s")
            print(f"Wait time: {wait_time:.3f}s")
            
        finally:
            await manager.stop()
    
    async def test_memory_usage_stability(self):
        """Test memory usage remains stable"""
        import psutil
        import os
        
        manager = AsyncTaskManager(
            max_concurrent_tasks=5,
            cleanup_interval=0.5
        )
        await manager.start()
        
        try:
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            
            # Run many tasks in batches
            for batch in range(5):
                async def memory_task(i):
                    # Do some work
                    data = [i] * 1000
                    await asyncio.sleep(0.01)
                    return sum(data)
                
                task_ids = []
                for i in range(20):
                    task_id = await manager.submit_task(
                        memory_task(i), 
                        name=f"memory_batch_{batch}_{i}"
                    )
                    task_ids.append(task_id)
                
                # Wait for batch completion
                for task_id in task_ids:
                    await manager.wait_for_task(task_id, timeout=5.0)
                
                # Allow cleanup
                await asyncio.sleep(1.0)
            
            final_memory = process.memory_info().rss
            memory_growth = final_memory - initial_memory
            
            # Memory growth should be reasonable (less than 50MB)
            assert memory_growth < 50 * 1024 * 1024
            
            print(f"Memory growth: {memory_growth / 1024 / 1024:.2f} MB")
            
        finally:
            await manager.stop()


if __name__ == "__main__":
    pytest.main([__file__])