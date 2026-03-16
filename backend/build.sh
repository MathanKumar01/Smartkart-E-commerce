#!/usr/bin/env bash
set -o errexit

pip install -r backend/requirements.txt

python backend/manage.py migrate
python backend/manage.py collectstatic --no-input

if [ "${SKIP_SEED:-0}" = "1" ]; then
	echo "Skipping product seed because SKIP_SEED=1"
elif python backend/manage.py shell -c "from products.models import Product; import sys; sys.exit(0 if Product.objects.exists() else 1)"; then
	if [ "${FORCE_SEED:-0}" = "1" ]; then
		echo "FORCE_SEED=1, re-importing products from CSV..."
		python backend/import_products.py --delete-existing
	else
		echo "Products already exist. Skipping seed."
	fi
else
	echo "No products found. Importing from CSV..."
	python backend/import_products.py
fi