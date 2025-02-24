#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Pillow first
pip install --no-cache-dir Pillow==11.1.0

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate 