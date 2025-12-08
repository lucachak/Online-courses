#!/bin/bash

IP=$(./helpers/get_ip.sh)
echo


source .venv/bin/activate; python3 manage.py runserver $IP:8000
