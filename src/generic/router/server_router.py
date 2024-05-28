from fastapi import APIRouter

class ServerRouter(APIRouter): 
    def __init__(self): 
        self.routes = {}
    
    def add_get_route(self, path, func):
        self.routes[path] = func 
        self.add_api_route(path, func, methods=["GET"])

    def add_post_route(self, path, func):
        self.routes[path] = func 
        self.add_api_route(path, func, methods=["POST"])

    def get(self, path):
        def decorator(func): 
            self.add_get_route(path, func)
        return decorator
        
    def post(self, path): 
        def decorator(func):
            self.add_post_route(path, func)
        return decorator

