from src.generic.types import ActionType, Status


class ActionHandler:
    """ Class ActionHandler allows to decorate method functions for action handling,
        it injects the action type into the method"""

    def __init__(self):
        self.handlers = {}

    def __call__(self, action_type, **kwargs):
        def decorator(func):
            self.handlers[action_type] = func
            return func
        return decorator

    def handle_action(self, action_type: ActionType, **kwargs) -> Status:
        """ Used to decorate action functions with its respective action type to call it 
            in case the action type is used


        Args:
            action_type (ActionType): the action type you want to assign the function to. 

        Returns:
            Status: returns the exist status of the action function used 
        """

        handler_func = self.handlers.get(action_type)
        if not handler_func:
            return Status.NOT_FOUND
        return handler_func(**kwargs)


class Xhandler(ActionHandler):
    """ Class Xhanlder is Xserver action handler"""

    def __init__(self):
        super().__init__()

    def handle_action(self, action_type: ActionType,  **kwargs):
        return super().handle_action(action_type, **kwargs)
