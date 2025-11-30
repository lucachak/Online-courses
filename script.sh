#!/bin/bash
# Get the IP address from your script


IP=$(./helpers/get_ip.sh)
echo


# Run Django server with the IP and port
python manage.py runserver $IP:8000
