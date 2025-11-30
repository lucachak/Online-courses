#!/bin/bash
# Stop Django and Tailwind development servers

echo "Stopping Django and Tailwind servers..."

# Kill Django runserver processes
pkill -f "python.*manage.py.*runserver" 2>/dev/null

# Kill Tailwind processes
pkill -f "tailwind" 2>/dev/null
pkill -f "npm.*watch" 2>/dev/null

# Kill processes on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

sleep 1
echo "All servers stopped!"








