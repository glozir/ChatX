from functools import wraps, partial
from enum import Enum

from ..generic.types import ActionType, Status
from ..generic.router.server_router import ServerRouter
from ..generic.session import Session, Thread


class AuthenticationLevel(Enum):
    PROTECTED = 0
    OPEN = 1 
    RESTRICTED = 2 


class Xhandler(): 
    """ Class Xhanlder is Xserver action handler"""
    pending_endpoints = []
    ROUTER = ServerRouter()

    def __init__(self) -> None:

        self.users = {}
        self.sessions: Thread = {}

    @classmethod
    def GET(cls, action_type: ActionType, protection_level : AuthenticationLevel=AuthenticationLevel.OPEN):
        def decorator(callback):
            @wraps(callback)
            def wrapper(self): 
                route_path = f"/{action_type.name}"
                bound_func = cls.validate(partial(callback, self), protection_level) 
                cls.ROUTER.add_get_route(route_path, bound_func)
            cls.pending_endpoints.append(wrapper)
            return wrapper
        return decorator

    @classmethod
    def POST(cls, action_type: ActionType, protection_level : AuthenticationLevel=AuthenticationLevel.OPEN):
        def decorator(callback):
            @wraps(callback)
            def wrapper(self): 
                route_path = f"/{action_type.name}"
                bound_func = cls.validate(partial(callback, self), protection_level) 
                cls.ROUTER.add_post_route(route_path, bound_func)
            cls.pending_endpoints.append(wrapper)
            return wrapper
        return decorator

    @classmethod
    def register_routes(cls, handler):
        for endpoint in cls.pending_endpoints:
            endpoint(handler)
        cls.pending_endpoints.clear()

    @staticmethod
    def validate(callback, protection_level : AuthenticationLevel): 
        if protection_level == AuthenticationLevel.OPEN:
            return callback  
                
        @wraps(callback)
        def wrapper(self, key, **kwargs):
            username = self.users.get(key)
            if username: 
                return callback(self, username=username, **kwargs)
            return Status.FAILURE
        
        def filter_parameters(func, parameter):
            @wraps(func)
            def wrapper(self, **kwargs):
                if parameter in kwargs:
                    return partial(func, filter=kwargs[parameter])
            return wrapper
        
        return filter_parameters(wrapper, 'username')
    
    