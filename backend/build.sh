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
	if python backend/import_products.py; then
		echo "CSV import completed."
	else
		echo "CSV import command failed. Trying fallback fixture load..."
	fi

	if python backend/manage.py shell -c "from products.models import Product; import sys; sys.exit(0 if Product.objects.exists() else 1)"; then
		echo "Products available after seed step."
	else
		echo "Products still empty. Loading fallback fixture from backend/data.json..."
		python backend/manage.py loaddata backend/data.json
	fi
fi

if python backend/manage.py shell -c "from products.models import Product; import sys; required={'laptop','phone'}; present=set(Product.objects.values_list('category', flat=True)); sys.exit(0 if required.issubset(present) else 1)"; then
	echo "Required categories present (laptop, phone)."
else
	echo "Missing laptop/phone categories. Loading fallback fixture from backend/data.json..."
	python backend/manage.py loaddata backend/data.json
fi

python backend/manage.py normalize_image_urls