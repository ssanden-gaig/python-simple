#!/bin/bash
. venv/bin/activate
gunicorn -b 0.0.0.0:8080  main:app --timeout 300 --log-level=info