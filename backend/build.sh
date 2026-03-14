#!/usr/bin/env bash
set -o errexit

pip install -r backend/requirements.txt

python backend/manage.py migrate
python backend/manage.py collectstatic --no-input

# Import products (only if DB is empty)
python backend/import_products.py
python backend/import_mobiles.py
python backend/import_accessories.py