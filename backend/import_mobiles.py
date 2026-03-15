import os
import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartcart.settings")
django.setup()

from products.models import Product

df = pd.read_csv(r"C:\Users\MathanVini\Downloads\flipkart_mobile_data.csv")

df = df.head(50)

for _, row in df.iterrows():

    price = str(row["Price"]).replace("₹","").replace(",","")

    Product.objects.create(
        name=row["Title"],
        description=row["Key Features"],
        price=float(price),
        stock=15,
        image_url=row["Image URL"],
        category="phone"
    )

print("✅ 50 phones imported successfully!")