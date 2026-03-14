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

# remove extra spaces in column names
df.columns = df.columns.str.strip()

df = df.head(50)

for _, row in df.iterrows():

    price = str(row["Price"]).replace("₹","").replace(",","")

    Product.objects.create(
        name=row["Product Link"][:200],
        description="Laptop imported from Flipkart dataset",
        price=float(price),
        stock=10,
        image_url=row["Image URL"],   # ← dataset image
        category="laptop"
    )

print("✅ 50 laptops imported successfully!")