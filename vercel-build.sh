#!/bin/bash
set -e

echo "=== Building frontend assets ==="
npm run build

echo "=== Running Django collectstatic ==="
python manage.py collectstatic --noinput

echo "=== Running Django migrations ==="
python manage.py migrate --noinput

echo "=== Build complete ==="
