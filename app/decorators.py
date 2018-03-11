from functools import wraps
from flask import abort
from flask_login import current_user
from . models import Permission

def permissionRequired(permission):
    def decorator(f):
        @wraps(f)
        def decoratedFunction(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decoratedFunction
    return decorator

def adminRequired(f):
    return permissionRequired(Permission.ADMINISTER)(f)
