import os
import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartcart.settings")
django.setup()

from products.models import Product

df = pd.read_csv(r"C:\Users\MathanVini\Downloads\flipkart_mobile_data.csv")

df = df.head(50)

for _, row in df.iterrows():

    # clean price
    price = row.get("Price", "0")
    price = str(price).replace("₹", "").replace(",", "")
    price = float(price)

    description = f"""
    Brand: {row.get('Brand','')}
    RAM: {row.get('RAM','')}
    Storage: {row.get('Storage','')}
    Battery: {row.get('Battery','')}
    Camera: {row.get('Camera','')}
    """

    Product.objects.create(
        name=row.get("Model", "Mobile Phone"),
        description=description,
        price=price,
        stock=15,
        image_url=row["Image URL"],
        category="phone"
    )

print("✅ 50 mobile phones imported successfully!")