import json
import os

PRODUCTS_FILE = 'products.json'
ORDERS_FILE = 'orders.json'

# ডাটা ফাইল তৈরি করা যদি না থাকে
def init_db():
    if not os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

def get_products():
    with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_products(products):
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=4, ensure_ascii=False)

def add_order(order):
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            orders = json.load(f)
    else:
        orders = []
    
    orders.append(order)
    
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, indent=4, ensure_ascii=False)

# ছবি রাখার ফোল্ডার তৈরি
if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')

init_db()
