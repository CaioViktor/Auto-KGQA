#!/bin/bash
gunicorn --bind 0.0.0.0:5000 --log-level=debug --workers 1 --timeout 0 wsgi:app #Put IP host (Server) here