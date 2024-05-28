from .server_services import server_handler 
from fastapi import FastAPI

def create_server(): 
    server = server_handler.Xserver()
    app = FastAPI()

    app.include_router(server.route_handler)

    return app

