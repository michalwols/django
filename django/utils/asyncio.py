import asyncio
import functools

from django.conf import settings
from django.core.exceptions import SynchronousOnlyOperation


def async_unsafe(message):
    """
    Decorator to mark functions as async-unsafe. Someone trying to access
    the function while in an async context will get an error message.
    """
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if not getattr(settings, 'ALLOW_ASYNC_UNSAFE', False):
                # Detect a running event loop in this thread.
                try:
                    event_loop = asyncio.get_event_loop()
                except RuntimeError:
                    pass
                else:
                    if event_loop.is_running():
                        raise SynchronousOnlyOperation(message)
            # Pass onwards.
            return func(*args, **kwargs)
        return inner
    # If the message is actually a function, then be a no-arguments decorator.
    if callable(message):
        func = message
        message = 'You cannot call this from an async context - use a thread or sync_to_async.'
        return decorator(func)
    else:
        return decorator
