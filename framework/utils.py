import time
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

def wait_for_condition(
        condition_func: Callable[[], bool],
        timeout: int = 30,
        interval: int = 2,
        description: str = "condition"
) -> bool:
    """Wait for a condition to be true"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            if condition_func():
                logger.info(f"Condition met: {description}")
                return True
        except Exception as e:
            logger.debug(f"Error checking condition '{description}': {e}")

        time.sleep(interval)

    logger.error(f"Timeout waiting for condition: {description}")
    return False

def retry_on_exception(
        func: Callable,
        max_attempts: int = 3,
        delay: float = 1.0,
        exceptions: tuple = (Exception,)
) -> Any:
    """Retry function execution on exceptions"""
    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            if attempt == max_attempts - 1:
                raise
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
            time.sleep(delay * (attempt + 1))