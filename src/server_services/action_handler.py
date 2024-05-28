from functools import wraps, partial

from ..generic.types import ActionType, Status
from ..generic.router.server_router import ServerRouter

class Xhandler(): 
    """ Class Xhanlder is Xserver action handler"""
    ROUTER = ServerRouter()
    pending_endpoints = []

    @classmethod
    def GET(cls, action_type: ActionType):
        def decorator(func):
            @wraps(func)
            def wrapper(self): 
                route_path = f"/{action_type.name}"
                bound_func = partial(func, self)
                cls.ROUTER.add_get_route(route_path, bound_func)
            cls.pending_endpoints.append(wrapper)
            return wrapper
        return decorator

    @classmethod
    def POST(cls, action_type: ActionType):
        def decorator(func):
            @wraps(func)
            def wrapper(self): 
                route_path = f"/{action_type.name}"
                bound_func = partial(func, self)
                cls.ROUTER.add_post_route(route_path, bound_func)
            cls.pending_endpoints.append(wrapper)
            return wrapper
        return decorator

    @classmethod
    def register_routes(cls, handler):
        for endpoint in cls.pending_endpoints:
            endpoint(handler)
        cls.pending_endpoints.clear()


    
    