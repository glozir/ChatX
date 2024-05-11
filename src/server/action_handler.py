from src.generic.types import * 

class ActionHandler:
    def __init__(self):
        self.handlers = {} 
        
    def __call__(self, action_type, **kwargs):
        def decorator(func):
            self.handlers[action_type] = func
            return func
        return decorator

    def handle_action(self, action_type, **kwargs):
        handler_func = self.handlers.get(action_type)
        if not handler_func:
            return Status.NOT_FOUND
        return handler_func(**kwargs)

class Xhandler(ActionHandler): 
    def __init__(self):
        super().__init__()

    def handle_action(self, action_type, **kwargs):
        return super().handle_action(action_type, **kwargs)
