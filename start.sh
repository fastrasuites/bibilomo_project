#!/bin/bash

# Run the script to create tables
python database.py

# Start Uvicorn processes
exec uvicorn main:app --host 0.0.0.0 --port 8000