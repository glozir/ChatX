from ..generic.types import ActionType, Status
from ..generic.router.server_router import ServerRouter

class Xhandler(): 
    """ Class Xhanlder is Xserver action handler"""
    ROUTER = ServerRouter()

    @classmethod
    def __call__(cls, action_type : ActionType): 
        def decorator(func): 
            cls.ROUTER.add_get_route(action_type.name, func)
        return decorator
