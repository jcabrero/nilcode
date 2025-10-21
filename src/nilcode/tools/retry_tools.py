"""
Retry mechanism tools for handling failed requests with exponential backoff.
These tools provide robust retry logic for API calls and operations.
"""

import time
import random
from typing import Callable, Any, Dict, List, Optional
from langchain.tools import tool


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        backoff_factor: float = 1.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.backoff_factor = backoff_factor


def retry_with_backoff(
    func: Callable,
    *args,
    retry_config: RetryConfig = None,
    retry_on_exceptions: tuple = (Exception,),
    **kwargs
) -> Any:
    """
    Execute a function with retry logic and exponential backoff.
    
    Args:
        func: Function to execute
        *args: Arguments to pass to function
        retry_config: Retry configuration
        retry_on_exceptions: Tuple of exceptions to retry on
        **kwargs: Keyword arguments to pass to function
        
    Returns:
        Result of function execution
        
    Raises:
        Last exception if all retries fail
    """
    if retry_config is None:
        retry_config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(retry_config.max_retries + 1):
        try:
            return func(*args, **kwargs)
        except retry_on_exceptions as e:
            last_exception = e
            
            if attempt == retry_config.max_retries:
                # Last attempt failed
                raise e
            
            # Calculate delay with exponential backoff
            delay = retry_config.base_delay * (retry_config.exponential_base ** attempt)
            delay = min(delay, retry_config.max_delay)
            delay *= retry_config.backoff_factor
            
            # Add jitter to prevent thundering herd
            if retry_config.jitter:
                jitter = random.uniform(0.1, 0.3) * delay
                delay += jitter
            
            print(f"⚠️ Attempt {attempt + 1} failed: {str(e)}")
            print(f"⏳ Retrying in {delay:.2f} seconds...")
            time.sleep(delay)
    
    # This should never be reached, but just in case
    raise last_exception


@tool
def retry_operation(
    operation_name: str,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0
) -> str:
    """
    Configure retry settings for an operation.
    
    Args:
        operation_name: Name of the operation to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        
    Returns:
        Retry configuration message
    """
    config = RetryConfig(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay
    )
    
    return f"🔄 Retry configured for '{operation_name}': max_retries={config.max_retries}, base_delay={config.base_delay}s, max_delay={config.max_delay}s"


@tool
def check_retry_status(operation_name: str, attempt: int, max_retries: int, last_error: str = "") -> str:
    """
    Check the current retry status for an operation.
    
    Args:
        operation_name: Name of the operation
        attempt: Current attempt number (1-based)
        max_retries: Maximum number of retries
        last_error: Last error encountered
        
    Returns:
        Status message
    """
    remaining = max_retries - attempt + 1
    
    if attempt > max_retries:
        return f"❌ Operation '{operation_name}' failed after {max_retries} retries. Last error: {last_error}"
    
    if remaining > 0:
        return f"🔄 Operation '{operation_name}': attempt {attempt}/{max_retries + 1}, {remaining} retries remaining. Last error: {last_error}"
    else:
        return f"✅ Operation '{operation_name}' succeeded on attempt {attempt}"


@tool
def calculate_retry_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0, exponential_base: float = 2.0) -> str:
    """
    Calculate the delay for the next retry attempt.
    
    Args:
        attempt: Current attempt number (0-based)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        
    Returns:
        Calculated delay information
    """
    delay = base_delay * (exponential_base ** attempt)
    delay = min(delay, max_delay)
    
    # Add jitter
    jitter = random.uniform(0.1, 0.3) * delay
    final_delay = delay + jitter
    
    return f"⏳ Retry delay for attempt {attempt + 1}: {final_delay:.2f}s (base: {delay:.2f}s + jitter: {jitter:.2f}s)"


class RetryManager:
    """Manages retry state and operations."""
    
    def __init__(self):
        self.retry_states: Dict[str, Dict[str, Any]] = {}
    
    def start_operation(self, operation_name: str, max_retries: int = 3) -> str:
        """Start tracking an operation for retries."""
        self.retry_states[operation_name] = {
            "attempt": 0,
            "max_retries": max_retries,
            "start_time": time.time(),
            "last_error": "",
            "delays": []
        }
        return f"🔄 Started tracking operation '{operation_name}' with {max_retries} max retries"
    
    def record_attempt(self, operation_name: str, success: bool, error: str = "") -> str:
        """Record an attempt for an operation."""
        if operation_name not in self.retry_states:
            return f"❌ Operation '{operation_name}' not being tracked"
        
        state = self.retry_states[operation_name]
        state["attempt"] += 1
        state["last_error"] = error
        
        if success:
            elapsed = time.time() - state["start_time"]
            del self.retry_states[operation_name]
            return f"✅ Operation '{operation_name}' succeeded on attempt {state['attempt']} after {elapsed:.2f}s"
        else:
            remaining = state["max_retries"] - state["attempt"]
            if remaining <= 0:
                elapsed = time.time() - state["start_time"]
                del self.retry_states[operation_name]
                return f"❌ Operation '{operation_name}' failed after {state['attempt']} attempts in {elapsed:.2f}s. Last error: {error}"
            else:
                return f"🔄 Operation '{operation_name}' attempt {state['attempt']} failed, {remaining} retries remaining. Error: {error}"
    
    def get_retry_delay(self, operation_name: str, base_delay: float = 1.0) -> float:
        """Get the calculated retry delay for an operation."""
        if operation_name not in self.retry_states:
            return base_delay
        
        state = self.retry_states[operation_name]
        attempt = state["attempt"]
        
        # Exponential backoff
        delay = base_delay * (2.0 ** attempt)
        delay = min(delay, 60.0)  # Cap at 60 seconds
        
        # Add jitter
        jitter = random.uniform(0.1, 0.3) * delay
        final_delay = delay + jitter
        
        state["delays"].append(final_delay)
        return final_delay
    
    def get_status(self, operation_name: str) -> str:
        """Get the current status of an operation."""
        if operation_name not in self.retry_states:
            return f"❌ Operation '{operation_name}' not being tracked"
        
        state = self.retry_states[operation_name]
        remaining = state["max_retries"] - state["attempt"]
        elapsed = time.time() - state["start_time"]
        
        return f"🔄 Operation '{operation_name}': attempt {state['attempt']}/{state['max_retries'] + 1}, {remaining} retries remaining, elapsed: {elapsed:.2f}s"


# Global retry manager instance
retry_manager = RetryManager()


@tool
def start_retry_tracking(operation_name: str, max_retries: int = 3) -> str:
    """
    Start tracking an operation for retry purposes.
    
    Args:
        operation_name: Name of the operation to track
        max_retries: Maximum number of retry attempts
        
    Returns:
        Confirmation message
    """
    return retry_manager.start_operation(operation_name, max_retries)


@tool
def record_retry_attempt(operation_name: str, success: bool, error: str = "") -> str:
    """
    Record an attempt for a tracked operation.
    
    Args:
        operation_name: Name of the operation
        success: Whether the attempt was successful
        error: Error message if unsuccessful
        
    Returns:
        Status message
    """
    return retry_manager.record_attempt(operation_name, success, error)


@tool
def get_retry_status(operation_name: str) -> str:
    """
    Get the current retry status for an operation.
    
    Args:
        operation_name: Name of the operation
        
    Returns:
        Status message
    """
    return retry_manager.get_status(operation_name)


@tool
def wait_for_retry(operation_name: str, base_delay: float = 1.0) -> str:
    """
    Wait for the calculated retry delay for an operation.
    
    Args:
        operation_name: Name of the operation
        base_delay: Base delay in seconds
        
    Returns:
        Wait confirmation message
    """
    delay = retry_manager.get_retry_delay(operation_name, base_delay)
    print(f"⏳ Waiting {delay:.2f} seconds before retry...")
    time.sleep(delay)
    return f"✅ Waited {delay:.2f} seconds for retry of '{operation_name}'"


# Export all tools
retry_tools = [
    retry_operation,
    check_retry_status,
    calculate_retry_delay,
    start_retry_tracking,
    record_retry_attempt,
    get_retry_status,
    wait_for_retry
]
