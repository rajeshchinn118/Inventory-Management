from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from typing import Dict
# Define the FastAPI app
app = FastAPI()

# Connect to SQLite database
conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

# Create tables if not exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku_id INTEGER,
        name TEXT,
        price REAL,
        quantity INTEGER,
        supplier_id INTEGER,
        FOREIGN KEY (sku_id) REFERENCES skus(id),
        FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        quantity INTEGER,
        customer_name TEXT,
        customer_email TEXT,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS skus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        location TEXT,
        capacity INTEGER
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        quantity INTEGER,
        price REAL,
        sale_date DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
''')
cursor.executemany('''
    INSERT INTO skus (name, location, capacity) VALUES (?, ?, ?)
''', [
    ('Himalaya Factory', 'Bangalore, Karnataka', 100),
    ('Apple Manufacturing', 'Mumbai, Maharashtra', 200),
    ('Kellogg\'s Plant', 'Mumbai, Maharashtra', 150),
    ('Dove Manufacturing', 'Pune, Maharashtra', 80),
    ('Daawat Rice Factory', 'Karnal, Haryana', 250),
    ('Bombay Dyeing Factory', 'Mumbai, Maharashtra', 120),
    ('Tropicana Factory', 'Jaipur, Rajasthan', 180),
    ('Colgate-Palmolive Factory', 'Mumbai, Maharashtra', 90),
    ('Parker Pen Manufacturing', 'Ahmedabad, Gujarat', 50),
    ('ITC Paper Factory', 'Hyderabad, Telangana', 70)
])

# Insert hardcoded data for Suppliers
cursor.executemany('''
    INSERT INTO suppliers (name, email) VALUES (?, ?)
''', [
    ('Supplier 1', 'supplier1@example.com'),
    ('Supplier 2', 'supplier2@example.com'),
    ('Supplier 3', 'supplier3@example.com'),
    ('Supplier 4', 'supplier4@example.com'),
    ('Supplier 5', 'supplier5@example.com')
])

# Insert hardcoded data for Products
cursor.executemany('''
    INSERT INTO products (sku_id, name, price, quantity, supplier_id) VALUES (?, ?, ?, ?, ?)
''', [
    (1, 'Shampoo', 5.99, 50, 1),
    (2, 'Apple', 0.99, 100, 2),
    (3, 'Cereals', 3.49, 80, 3),
    (4, 'Soap', 1.49, 120, 1),
    (5, 'Rice', 2.99, 200, 4),
    (6, 'Towel', 8.99, 30, 5),
    (7, 'Juice', 4.29, 70, 3),
    (8, 'Toothpaste', 2.49, 90, 1),
    (9, 'Pen', 1.99, 60, 2),
    (10, 'Book', 9.99, 20, 4)
])

# Insert hardcoded data for Orders
cursor.executemany('''
    INSERT INTO orders (product_id, quantity, customer_name, customer_email) VALUES (?, ?, ?, ?)
''', [
    (1, 2, 'John Doe', 'john@example.com'),
    (2, 5, 'Jane Smith', 'jane@example.com'),
    (3, 3, 'Alice Johnson', 'alice@example.com'),
    (4, 1, 'Bob Brown', 'bob@example.com'),
    (5, 4, 'Charlie Davis', 'charlie@example.com'),
    (6, 2, 'Eva Wilson', 'eva@example.com'),
    (7, 3, 'Frank Miller', 'frank@example.com'),
    (8, 2, 'Grace Thompson', 'grace@example.com'),
    (9, 1, 'Henry Garcia', 'henry@example.com'),
    (10, 2, 'Ivy Clark', 'ivy@example.com')
])
# Product model
class Product(BaseModel):
    sku_id: int
    name: str
    price: float
    quantity: int
    supplier_id: int


# Order model
class Order(BaseModel):
    product_id: int
    quantity: int
    customer_name: str
    customer_email: str


# Supplier model
class Supplier(BaseModel):
    name: str
    email: str


# SKU model
class SKU(BaseModel):
    name: str
    location: str
    capacity: int






# Sale model
class Sale(BaseModel):
    product_id: int
    quantity: int
    price: float


# CRUD operations for Sales
@app.post("/sales/")
async def create_sale(sale: Sale):
    # Check if product is in stock
    cursor.execute('SELECT quantity FROM products WHERE id = ?', (sale.product_id,))
    product_quantity = cursor.fetchone()
    if product_quantity is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if sale.quantity > product_quantity[0]:
        raise HTTPException(status_code=400, detail="Product is out of stock")
    
    # Calculate total sale amount
    total_price = sale.quantity * sale.price
    
    # Add sale record
    cursor.execute('''
        INSERT INTO sales (product_id, quantity, price)
        VALUES (?, ?, ?)
    ''', (sale.product_id, sale.quantity, total_price))
    
    # Update product quantity
    cursor.execute('''
        UPDATE products
        SET quantity = quantity - ?
        WHERE id = ?
    ''', (sale.quantity, sale.product_id))
    
    conn.commit()
    return {"message": "Sale added successfully"}


# Retrieve sales for a product
@app.get("/sales/{product_id}")
async def get_product_sales(product_id: int):
    cursor.execute('SELECT * FROM sales WHERE product_id = ?', (product_id,))
    sales = cursor.fetchall()
    return {"sales": sales}

# CRUD operations for Products
@app.post("/products/")
async def create_product(product: Product):
    print(product)
    cursor.execute('''
        INSERT INTO products (sku_id, name, price, quantity, supplier_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (product.sku_id, product.name, product.price, product.quantity, product.supplier_id))
    conn.commit()
    return {"message": "Product created successfully"}


@app.get("/products/{product_id}")
async def read_product(product_id: int):
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/products")
async def read_product():
    cursor.execute('SELECT * FROM products ', ())
    product = cursor.fetchall()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}")
async def update_product(product_id: int, product: Product):
    cursor.execute('''
        UPDATE products
        SET sku_id = ?, name = ?, price = ?, quantity = ?, supplier_id = ?
        WHERE id = ?
    ''', (product.sku_id, product.name, product.price, product.quantity, product.supplier_id, product_id))
    conn.commit()
    return {"message": "Product updated successfully"}


@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    return {"message": "Product deleted successfully"}

@app.get("/suppliers/")
async def get_suppliers():
    cursor.execute('SELECT * FROM suppliers')
    suppliers = cursor.fetchall()
    return  suppliers

@app.get("/orders/")
async def get_orders():
    cursor.execute('SELECT * FROM orders')
    orders = cursor.fetchall()
    return  orders

# Get a specific order by ID
@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    order = cursor.fetchone()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    columns = [description[0] for description in cursor.description]  # Get column names
    order_data = dict(zip(columns, order))  # Create a dictionary of column names and values
    return order_data

# Get a specific supplier by ID
@app.get("/suppliers/{supplier_id}")
async def get_supplier(supplier_id: int):
    cursor.execute('SELECT * FROM suppliers WHERE id = ?', (supplier_id,))
    supplier = cursor.fetchone()
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    columns = [description[0] for description in cursor.description]  # Get column names
    supplier_data = dict(zip(columns, supplier))  # Create a dictionary of column names and values
    return supplier_data

# CRUD operations for Orders
@app.post("/orders/")
async def create_order(order: Order):
    cursor.execute('''
        INSERT INTO orders (product_id, quantity, customer_name, customer_email)
        VALUES (?, ?, ?, ?)
    ''', (order.product_id, order.quantity, order.customer_name, order.customer_email))
    conn.commit()
    return {"message": "Order created successfully"}


# CRUD operations for Suppliers
@app.post("/suppliers/")
async def create_supplier(supplier: Supplier):
    cursor.execute('''
        INSERT INTO suppliers (name, email)
        VALUES (?, ?)
    ''', (supplier.name, supplier.email))
    conn.commit()
    return {"message": "Supplier created successfully"}


# CRUD operations for SKUs
@app.post("/skus/")
async def create_sku(sku: SKU):
    cursor.execute('''
        INSERT INTO skus (name, location, capacity)
        VALUES (?, ?, ?)
    ''', (sku.name, sku.location, sku.capacity))
    conn.commit()
    return {"message": "SKU created successfully"}

# Read SKU details
@app.get("/skus/{sku_id}")
async def read_sku(sku_id: int):
    cursor.execute('SELECT * FROM skus WHERE id = ?', (sku_id,))
    sku = cursor.fetchone()
    if sku is None:
        raise HTTPException(status_code=404, detail="SKU not found")
    print(sku)
    return sku

# Read SKU details
@app.get("/skus")
async def read_sku():
    cursor.execute('SELECT * FROM skus ', ())
    sku = cursor.fetchall()
    if sku is None:
        raise HTTPException(status_code=404, detail="SKU not found")
    return sku
# Update SKU details
@app.put("/skus/{sku_id}")
async def update_sku(sku_id: int, sku: SKU):
    cursor.execute('''
        UPDATE skus
        SET name = ?, location = ?, capacity = ?
        WHERE id = ?
    ''', (sku.name, sku.location, sku.capacity, sku_id))
    conn.commit()
    return {"message": "SKU updated successfully"}

# Delete SKU
@app.delete("/skus/{sku_id}")
async def delete_sku(sku_id: int):
    cursor.execute('DELETE FROM skus WHERE id = ?', (sku_id,))
    conn.commit()
    return {"message": "SKU deleted successfully"}

@app.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    conn.commit()
    return {"message": "Order deleted successfully"}

@app.delete("/suppliers/{supplier_id}")
async def delete_supplier(supplier_id: int):
    cursor.execute('DELETE FROM suppliers WHERE id = ?', (supplier_id,))
    conn.commit()
    return {"message": "Supplier deleted successfully"}

# Update an existing order by ID
@app.put("/orders/{order_id}")
async def update_order(order_id: int, updated_order: Order):
    # Check if the order exists
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    existing_order = cursor.fetchone()
    if existing_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update the existing order with the new data
    update_query = 'UPDATE orders SET '
    update_values = []
    
    # Update each attribute individually
    if updated_order.product_id is not None:
        update_query += 'product_id = ?, '
        update_values.append(updated_order.product_id)
    if updated_order.quantity is not None:
        update_query += 'quantity = ?, '
        update_values.append(updated_order.quantity)
    if updated_order.customer_name is not None:
        update_query += 'customer_name = ?, '
        update_values.append(updated_order.customer_name)
    if updated_order.customer_email is not None:
        update_query += 'customer_email = ?, '
        update_values.append(updated_order.customer_email)
    
    # Remove the trailing comma and space
    update_query = update_query.rstrip(', ')
    
    # Add the WHERE clause
    update_query += ' WHERE id = ?'
    update_values.append(order_id)

    # Execute the update query
    cursor.execute(update_query, update_values)
    conn.commit()

    return {"message": "Order updated successfully"}


# Update an existing supplier by ID
@app.put("/suppliers/{supplier_id}")
async def update_supplier(supplier_id: int, updated_supplier: Supplier):
    cursor.execute('SELECT * FROM suppliers WHERE id = ?', (supplier_id,))
    existing_supplier = cursor.fetchone()
    if existing_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Update the existing supplier with the new name and email
    update_query = 'UPDATE suppliers SET name = ?, email = ? WHERE id = ?'
    update_values = (updated_supplier.name, updated_supplier.email, supplier_id)

    cursor.execute(update_query, update_values)
    conn.commit()
    
    return {"message": "Supplier updated successfully"}

#-------------------------analytics------------------------------
@app.get("/capacity-analytics")
async def read_sku():
    cursor.execute('''SELECT 
            s.id AS sku_id, 
            s.name AS sku_name, 
            s.capacity AS total_capacity, 
            COALESCE(SUM(p.quantity), 0) AS used_capacity
        FROM 
            skus s
        LEFT JOIN 
            products p ON s.id = p.sku_id
        GROUP BY 
            s.id, s.name, s.capacity''', ())
    sku = cursor.fetchall()
    if sku is None:
        raise HTTPException(status_code=404, detail="SKU not found")
    return sku
@app.get("/sales-analytics")
async def read_sku():
    cursor.execute('''SELECT 
                p.name AS product_name, 
                COALESCE(SUM(o.quantity), 0) AS total_sold
            FROM 
                products p
            LEFT JOIN 
                orders o ON p.id = o.product_id
            GROUP BY 
                p.name''', ())
    sku = cursor.fetchall()
    if sku is None:
        raise HTTPException(status_code=404, detail="SKU not found")
    return sku

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
