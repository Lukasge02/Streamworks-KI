"""
Enterprise Async Processing Manager for StreamWorks-KI
Provides robust async task management with proper resource cleanup and error handling
"""
import asyncio
import logging
from typing import Optional, Dict, Any, List, Callable, Awaitable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import weakref
import gc
import traceback
from concurrent.futures import ThreadPoolExecutor
import threading
import signal
import sys

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class TaskInfo:
    """Task information tracking"""
    task_id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: float = 300.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AsyncTaskManager:
    """Enterprise-grade async task management with resource limits and cleanup"""
    
    def __init__(self, 
                 max_concurrent_tasks: int = 50,
                 max_queue_size: int = 1000,
                 default_timeout: float = 300.0,
                 cleanup_interval: float = 60.0):
        
        self.max_concurrent_tasks = max_concurrent_tasks
        self.max_queue_size = max_queue_size
        self.default_timeout = default_timeout
        self.cleanup_interval = cleanup_interval
        
        # Task tracking
        self._tasks: Dict[str, asyncio.Task] = {}
        self._task_info: Dict[str, TaskInfo] = {}
        self._task_semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self._task_counter = 0
        self._lock = asyncio.Lock()
        
        # Resource management
        self._running = False
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Statistics
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "cancelled_tasks": 0,
            "timeout_tasks": 0,
            "avg_execution_time": 0.0,
            "peak_concurrent_tasks": 0,
            "current_tasks": 0
        }
        
        # Thread pool for CPU-bound operations
        self._thread_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="StreamWorks")
        
        logger.info(f"🚀 AsyncTaskManager initialized (max_tasks={max_concurrent_tasks}, queue_size={max_queue_size})")
    
    async def start(self) -> None:
        """Start the task manager"""
        if self._running:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Setup signal handlers for graceful shutdown
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self._signal_handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, self._signal_handler)
        
        logger.info("✅ AsyncTaskManager started")
    
    async def stop(self, timeout: float = 30.0) -> None:
        """Stop the task manager gracefully"""
        if not self._running:
            return
        
        logger.info("🛑 Stopping AsyncTaskManager...")
        self._running = False
        self._shutdown_event.set()
        
        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await asyncio.wait_for(self._cleanup_task, timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
        
        # Cancel all running tasks
        await self._cancel_all_tasks(timeout=timeout)
        
        # Shutdown thread pool
        self._thread_pool.shutdown(wait=True, timeout=10.0)
        
        logger.info("✅ AsyncTaskManager stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📡 Received signal {signum}, initiating graceful shutdown...")
        asyncio.create_task(self.stop())
    
    async def submit_task(self, 
                         coro: Awaitable,
                         name: str = None,
                         timeout: float = None,
                         max_retries: int = 3,
                         metadata: Dict[str, Any] = None) -> str:
        """Submit a new async task with resource management"""
        
        if not self._running:
            raise RuntimeError("AsyncTaskManager is not running")
        
        # Check queue size
        if len(self._tasks) >= self.max_queue_size:
            raise RuntimeError(f"Task queue full (max: {self.max_queue_size})")
        
        # Generate task ID
        async with self._lock:
            self._task_counter += 1
            task_id = f"task_{self._task_counter}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Create task info
        task_info = TaskInfo(
            task_id=task_id,
            name=name or "unnamed_task",
            timeout_seconds=timeout or self.default_timeout,
            max_retries=max_retries,
            metadata=metadata or {}
        )
        
        # Wrap coroutine with management
        managed_coro = self._manage_task(coro, task_info)
        
        # Create and start task
        task = asyncio.create_task(managed_coro, name=f"StreamWorks_{task_id}")
        
        # Store task references
        self._tasks[task_id] = task
        self._task_info[task_id] = task_info
        
        # Update statistics
        self.stats["total_tasks"] += 1
        self.stats["current_tasks"] = len(self._tasks)
        if self.stats["current_tasks"] > self.stats["peak_concurrent_tasks"]:
            self.stats["peak_concurrent_tasks"] = self.stats["current_tasks"]
        
        logger.info(f"📋 Task submitted: {task_id} ({name})")
        return task_id
    
    async def _manage_task(self, coro: Awaitable, task_info: TaskInfo) -> Any:
        """Manage task execution with semaphore, timeout, and error handling"""
        task_id = task_info.task_id
        
        try:
            # Wait for semaphore (resource limiting)
            async with self._task_semaphore:
                task_info.status = TaskStatus.RUNNING
                task_info.started_at = datetime.utcnow()
                
                logger.debug(f"🏃 Task started: {task_id}")
                
                # Execute with timeout
                result = await asyncio.wait_for(coro, timeout=task_info.timeout_seconds)
                
                # Task completed successfully
                task_info.status = TaskStatus.COMPLETED
                task_info.completed_at = datetime.utcnow()
                task_info.result = result
                
                self.stats["completed_tasks"] += 1
                self._update_avg_execution_time(task_info)
                
                logger.info(f"✅ Task completed: {task_id}")
                return result
                
        except asyncio.TimeoutError:
            task_info.status = TaskStatus.TIMEOUT
            task_info.completed_at = datetime.utcnow()
            task_info.error = f"Task timed out after {task_info.timeout_seconds}s"
            
            self.stats["timeout_tasks"] += 1
            logger.warning(f"⏰ Task timeout: {task_id}")
            
            # Try to cancel gracefully
            await self._cleanup_task_references(task_id)
            raise asyncio.TimeoutError(task_info.error)
            
        except asyncio.CancelledError:
            task_info.status = TaskStatus.CANCELLED
            task_info.completed_at = datetime.utcnow()
            task_info.error = "Task was cancelled"
            
            self.stats["cancelled_tasks"] += 1
            logger.info(f"🚫 Task cancelled: {task_id}")
            
            await self._cleanup_task_references(task_id)
            raise
            
        except Exception as e:
            task_info.status = TaskStatus.FAILED
            task_info.completed_at = datetime.utcnow()
            task_info.error = str(e)
            
            self.stats["failed_tasks"] += 1
            logger.error(f"❌ Task failed: {task_id} - {e}")
            logger.debug(f"Task traceback: {traceback.format_exc()}")
            
            # Handle retries
            if task_info.retry_count < task_info.max_retries:
                task_info.retry_count += 1
                task_info.status = TaskStatus.PENDING
                
                logger.info(f"🔄 Retrying task: {task_id} (attempt {task_info.retry_count}/{task_info.max_retries})")
                
                # Exponential backoff
                delay = min(2 ** task_info.retry_count, 60)
                await asyncio.sleep(delay)
                
                # Retry
                return await self._manage_task(coro, task_info)
            
            await self._cleanup_task_references(task_id)
            raise
        
        finally:
            # Ensure cleanup happens
            await self._cleanup_task_references(task_id)
    
    async def _cleanup_task_references(self, task_id: str) -> None:
        """Clean up task references and update stats"""
        try:
            # Remove from active tasks
            if task_id in self._tasks:
                del self._tasks[task_id]
            
            # Update current task count
            self.stats["current_tasks"] = len(self._tasks)
            
            # Optionally keep task_info for a while for debugging
            # But limit the size to prevent memory leaks
            if len(self._task_info) > 1000:
                # Remove oldest completed tasks
                completed_tasks = [
                    (tid, info) for tid, info in self._task_info.items()
                    if info.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.TIMEOUT]
                ]
                
                # Sort by completion time and remove oldest 200
                completed_tasks.sort(key=lambda x: x[1].completed_at or datetime.min)
                for tid, _ in completed_tasks[:200]:
                    if tid in self._task_info:
                        del self._task_info[tid]
        
        except Exception as e:
            logger.error(f"Error cleaning up task references: {e}")
    
    def _update_avg_execution_time(self, task_info: TaskInfo) -> None:
        """Update average execution time statistics"""
        if task_info.started_at and task_info.completed_at:
            execution_time = (task_info.completed_at - task_info.started_at).total_seconds()
            
            completed_count = self.stats["completed_tasks"]
            current_avg = self.stats["avg_execution_time"]
            
            # Calculate new average
            new_avg = ((current_avg * (completed_count - 1)) + execution_time) / completed_count
            self.stats["avg_execution_time"] = new_avg
    
    async def _cleanup_loop(self) -> None:
        """Periodic cleanup of completed tasks and resources"""
        while self._running and not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                if not self._running:
                    break
                
                # Clean up completed tasks
                await self._cleanup_completed_tasks()
                
                # Force garbage collection periodically
                if self.stats["total_tasks"] % 100 == 0:
                    collected = gc.collect()
                    logger.debug(f"🧹 Garbage collected {collected} objects")
                
                # Memory usage check
                await self._check_memory_usage()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_completed_tasks(self) -> None:
        """Clean up references to completed tasks"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=30)
        
        completed_task_ids = []
        for task_id, task_info in self._task_info.items():
            if (task_info.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED, TaskStatus.TIMEOUT] 
                and task_info.completed_at 
                and task_info.completed_at < cutoff_time):
                completed_task_ids.append(task_id)
        
        for task_id in completed_task_ids:
            await self._cleanup_task_references(task_id)
        
        if completed_task_ids:
            logger.debug(f"🧹 Cleaned up {len(completed_task_ids)} old tasks")
    
    async def _check_memory_usage(self) -> None:
        """Check and log memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            if memory_mb > 1000:  # More than 1GB
                logger.warning(f"⚠️ High memory usage: {memory_mb:.1f}MB")
                
                if memory_mb > 2000:  # More than 2GB
                    logger.error(f"🚨 Critical memory usage: {memory_mb:.1f}MB")
                    # Force garbage collection
                    collected = gc.collect()
                    logger.info(f"Emergency GC collected {collected} objects")
        
        except ImportError:
            pass  # psutil not available
        except Exception as e:
            logger.error(f"Error checking memory usage: {e}")
    
    async def _cancel_all_tasks(self, timeout: float = 30.0) -> None:
        """Cancel all running tasks with timeout"""
        if not self._tasks:
            return
        
        logger.info(f"🚫 Cancelling {len(self._tasks)} running tasks...")
        
        # Cancel all tasks
        for task_id, task in self._tasks.items():
            if not task.done():
                task.cancel()
                logger.debug(f"Cancelled task: {task_id}")
        
        # Wait for cancellation with timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*self._tasks.values(), return_exceptions=True),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"⏰ Some tasks did not cancel within {timeout}s")
        
        # Force cleanup
        task_ids = list(self._tasks.keys())
        for task_id in task_ids:
            await self._cleanup_task_references(task_id)
    
    async def get_task_status(self, task_id: str) -> Optional[TaskInfo]:
        """Get status of a specific task"""
        return self._task_info.get(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a specific task"""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            if not task.done():
                task.cancel()
                logger.info(f"🚫 Cancelled task: {task_id}")
                return True
        return False
    
    async def wait_for_task(self, task_id: str, timeout: float = None) -> Any:
        """Wait for a specific task to complete"""
        if task_id not in self._tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self._tasks[task_id]
        
        try:
            if timeout:
                return await asyncio.wait_for(task, timeout=timeout)
            else:
                return await task
        except asyncio.CancelledError:
            logger.info(f"Task {task_id} was cancelled while waiting")
            raise
        except Exception as e:
            logger.error(f"Task {task_id} failed while waiting: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive task manager statistics"""
        return {
            **self.stats,
            "running_tasks": len([t for t in self._tasks.values() if not t.done()]),
            "pending_tasks": len([info for info in self._task_info.values() if info.status == TaskStatus.PENDING]),
            "memory_tasks": len(self._task_info),
            "is_running": self._running,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "max_queue_size": self.max_queue_size
        }
    
    async def run_in_thread(self, func: Callable, *args, **kwargs) -> Any:
        """Run a CPU-bound function in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._thread_pool, func, *args, **kwargs)


# Global task manager instance
task_manager = AsyncTaskManager()


async def initialize_async_manager() -> None:
    """Initialize the global task manager"""
    await task_manager.start()
    logger.info("🚀 Global async task manager initialized")


async def shutdown_async_manager() -> None:
    """Shutdown the global task manager"""
    await task_manager.stop()
    logger.info("🛑 Global async task manager shutdown")


# Context manager for safe task submission
class AsyncTaskContext:
    """Context manager for safe async task management"""
    
    def __init__(self, manager: AsyncTaskManager = None):
        self.manager = manager or task_manager
        self.task_ids: List[str] = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cancel all tasks submitted in this context if there was an exception
        if exc_type is not None:
            for task_id in self.task_ids:
                await self.manager.cancel_task(task_id)
    
    async def submit(self, coro: Awaitable, name: str = None, **kwargs) -> str:
        """Submit a task within this context"""
        task_id = await self.manager.submit_task(coro, name=name, **kwargs)
        self.task_ids.append(task_id)
        return task_id
    
    async def wait_all(self, timeout: float = None) -> List[Any]:
        """Wait for all tasks in this context"""
        results = []
        for task_id in self.task_ids:
            try:
                result = await self.manager.wait_for_task(task_id, timeout=timeout)
                results.append(result)
            except Exception as e:
                logger.error(f"Task {task_id} failed: {e}")
                results.append(e)
        return results


# Utility functions for common patterns
async def safe_gather(*coros, return_exceptions: bool = True, timeout: float = None) -> List[Any]:
    """Safe gather with timeout and exception handling"""
    async with AsyncTaskContext() as ctx:
        task_ids = []
        for i, coro in enumerate(coros):
            task_id = await ctx.submit(coro, name=f"gather_task_{i}")
            task_ids.append(task_id)
        
        return await ctx.wait_all(timeout=timeout)


async def run_with_retries(coro: Awaitable, 
                          max_retries: int = 3, 
                          timeout: float = 300.0,
                          name: str = None) -> Any:
    """Run coroutine with retries and timeout"""
    return await task_manager.submit_task(
        coro, 
        name=name,
        max_retries=max_retries,
        timeout=timeout
    )


# Decorator for automatic task management
def managed_task(timeout: float = 300.0, max_retries: int = 3):
    """Decorator to automatically manage async functions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            coro = func(*args, **kwargs)
            task_id = await task_manager.submit_task(
                coro,
                name=func.__name__,
                timeout=timeout,
                max_retries=max_retries
            )
            return await task_manager.wait_for_task(task_id)
        return wrapper
    return decorator