from functools import wraps
from halo import Halo

def with_spinner(text="Loading", spinner_type="dots"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with Halo(text=text, spinner=spinner_type) as spinner:
                try:
                    result = func(*args, **kwargs)
                    spinner.succeed()
                    return result
                except Exception as e:
                    spinner.fail(f"Error: {str(e)}")
                    raise
        return wrapper
    return decorator
