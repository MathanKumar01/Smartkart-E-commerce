import os
import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartcart.settings")
django.setup()

from products.models import Product


df = pd.read_csv(r"C:\Users\MathanVini\Downloads\flipkart_com-ecommerce_sample.csv\flipkart_com-ecommerce_sample.csv")

# test only 5 products first
df = df.head(5)

for _, row in df.iterrows():

    price = row.get("retail_price", 0)

    image = str(row.get("image", ""))

    # extract first image from list
    if "," in image:
        image = image.split(",")[0]

    image = image.replace("[", "").replace("]", "").replace("'", "").replace('"', "")

    Product.objects.create(
        name=row.get("product_name", "Accessory"),
        description=row.get("description", ""),
        price=float(price) if price else 0,
        stock=20,
        image_url=image,
        category="accessories"
    )

print("✅ 5 accessories imported successfully!")