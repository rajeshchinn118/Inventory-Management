import requests

def fetch_products():
    url = "http://localhost:8000/products"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch products")
        return []

def fetch_skus():
    url = "http://localhost:8000/skus"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch products")
        return []

def fetch_orders():
    # Implement logic to fetch orders from the API
    pass
