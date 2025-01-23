import json
from functools import wraps


def validate_event_data(func):
    """
    Decorator to validate the event data before passing it to the wrapped function.

    This decorator checks if the event data is a dictionary or a string:
    - If it's a dictionary, it converts it to a JSON string.
    - If it's neither a string nor a dictionary, it raises a ValueError.
    """
    @wraps(func)
    async def wrapper(self, event_data, *args, **kwargs):
        if isinstance(event_data, dict):
            event_data = json.dumps(event_data)
        elif not isinstance(event_data, str):
            raise ValueError("Event data must be a string or a dictionary.")

        return await func(self, event_data, *args, **kwargs)

    return wrapper
