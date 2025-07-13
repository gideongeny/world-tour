from functools import wraps
from flask import current_app

def cache_result(timeout=300):
    """Caching decorator using Flask-Caching"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache = current_app.extensions['cache']
            cache_key = f"{f.__name__}:{hash(str(args) + str(kwargs))}"
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            return result
        return decorated_function
    return decorator 