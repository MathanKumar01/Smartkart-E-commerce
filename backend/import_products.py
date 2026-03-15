import os
import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartcart.settings")
django.setup()

from products.models import Product

if Product.objects.exists():
    print("Products already exist. Skipping import.")
    exit()

df = pd.read_csv(r"C:\Users\MathanVini\Downloads\flipkart_laptops (1).csv")

df.columns = df.columns.str.strip()

df = df.head(50)

for _, row in df.iterrows():

    price = str(row["Price"]).replace("₹","").replace(",","")

    Product.objects.create(
        name=row["Title"][:200],
        description=row["Key Features"],   # better description
        price=float(price),
        stock=10,
        image_url=row["Image URL"],
        category="laptop"
    )

print("✅ 50 laptops imported successfully!")