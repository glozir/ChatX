#!/bin/sh

uvicorn src.server:create_server --factory --host 0.0.0.0 --port 1337 --reload 

