#!/bin/bash
fastapi run app/main.py --port 8000 &
taskiq worker app.broker:broker &

wait -n
exit $?
