#!/bin/sh

# activate virtual env 
source project_env/bin/activate

# run server 
python -m uvicorn src.server:create_server --factory --host 0.0.0.0 --port 1337 --reload

