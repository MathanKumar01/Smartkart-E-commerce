#!/usr/bin/env bash
set -o errexit

pip install -r backend/requirements.txt

python backend/manage.py migrate
python backend/manage.py collectstatic --no-input

# Normalize fixture encoding so loaddata always reads UTF-8 JSON.
python - <<'PY'
from pathlib import Path

fixture = Path("backend/data.json")
raw = fixture.read_bytes()

for encoding in ("utf-8", "utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"):
	try:
		text = raw.decode(encoding)
		fixture.write_text(text, encoding="utf-8", newline="\n")
		print(f"Normalized {fixture} from {encoding} to utf-8")
		break
	except UnicodeDecodeError:
		continue
else:
	raise SystemExit(f"Unable to decode fixture file: {fixture}")
PY

if [ "${SKIP_SEED:-0}" = "1" ]; then
	echo "Skipping fixture load because SKIP_SEED=1"
elif python backend/manage.py shell -c "from products.models import Product; import sys; sys.exit(0 if Product.objects.exists() else 1)"; then
	if [ "${FORCE_SEED:-0}" = "1" ]; then
		echo "FORCE_SEED=1, loading fixture even though products already exist"
		python backend/manage.py loaddata backend/data.json
	else
		echo "Products already exist. Skipping fixture load."
	fi
else
	echo "No products found. Loading fixture data."
	python backend/manage.py loaddata backend/data.json
fi