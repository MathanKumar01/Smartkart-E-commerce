import pandas as pd

# load dataset
df = pd.read_csv(r"C:\Users\MathanVini\Downloads\archive (8)\flipkart_com-ecommerce_sample.csv")

# remove rows without price
df = df.dropna(subset=["retail_price"])

# extract main category
df["category"] = df["product_category_tree"].str.split(">>").str[0]

# remove brackets and quotes
df["category"] = df["category"].str.replace(r"[\[\]\"']", "", regex=True)

# remove extra spaces
df["category"] = df["category"].str.strip()

# select useful columns
df = df[
    [
        "product_name",
        "retail_price",
        "discounted_price",
        "description",
        "image",
        "brand",
        "product_rating",
        "category",
    ]
]

# remove rows with missing product name
df = df.dropna(subset=["product_name"])

# fill missing brand and rating
df["brand"] = df["brand"].fillna("Unknown")
df["product_rating"] = df["product_rating"].fillna(0)

# limit 50 products per category
df = df.groupby("category").head(50)

# reset index
df = df.reset_index(drop=True)

# save cleaned dataset
df.to_csv("smartkart_products_clean.csv", index=False)

print("Dataset cleaned successfully!")
print("Total products:", len(df))
print("Total categories:", df["category"].nunique())