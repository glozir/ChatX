from .server_services.server_handler import Xserver 
from fastapi import FastAPI

def create_server(): 
    server = Xserver()
    app = FastAPI()

    app.include_router(server.route_handler)

    return app
