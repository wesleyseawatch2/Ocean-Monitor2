#!/bin/bash
# Zeabur 部署後腳本

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Deployment complete!"
