#!/bin/bash
. venv/bin/activate
gunicorn --port 5000 -w 5 main:app --timeout 300