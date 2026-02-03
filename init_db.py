import sqlite3

conn = sqlite3.connect('database.db')

conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    loyalty_points INTEGER DEFAULT 0
)
""")

# Check if products table exists and has new columns
try:
    conn.execute("SELECT pet_type, image_url FROM products LIMIT 1")
except sqlite3.OperationalError:
    # Table exists but missing new columns - recreate it
    conn.execute("DROP TABLE IF EXISTS products")

conn.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    pet_type TEXT,
    price REAL,
    image_url TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    pet TEXT,
    date TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS grooming_services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    image_url TEXT
)
""")

# Check if grooming_services table has image_url column
try:
    conn.execute("SELECT image_url FROM grooming_services LIMIT 1")
except sqlite3.OperationalError:
    # Missing column - recreate table (simple approach for dev)
    conn.execute("DROP TABLE IF EXISTS grooming_services")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS grooming_services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        image_url TEXT
    )
    """)

# Product images mapping - using Unsplash for relevant product images
product_images = {
    # DOG FOOD PRODUCTS
    'Premium Dry Dog Food - 15kg': 'https://images.unsplash.com/photo-1589924691995-400dc9ecc119?w=800',
    'Organic Grain-Free Dog Food': 'https://images.unsplash.com/photo-1585849834997-6da8637b3194?w=800',
    'Puppy Starter Food - 10kg': 'https://images.unsplash.com/photo-1608408843596-b311965e04cb?w=800',
    'Senior Dog Food - 12kg': 'https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=800',
    'Wet Dog Food - 12 Cans': 'https://images.unsplash.com/photo-1589924691995-400dc9ecc119?w=800',
    'Dog Treats - Training Pack': 'https://images.unsplash.com/photo-1582798358481-d199fb7347bb?w=800',
    
    # CAT FOOD PRODUCTS
    'Premium Dry Cat Food - 10kg': 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=800',
    'Kitten Starter Food - 5kg': 'https://images.unsplash.com/photo-1574158622682-e40e69881006?w=800',
    'Indoor Cat Food - 8kg': 'https://images.unsplash.com/photo-1511044568932-338cba0fb803?w=800',
    'Wet Cat Food - 24 Cans': 'https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=800',
    'Cat Treats - Variety Pack': 'https://images.unsplash.com/photo-1535591273668-578e31182c4f?w=800',
    
    # DOG ACCESSORIES
    'Dog Leash - Premium Leather': 'https://images.unsplash.com/photo-1576201836106-db1758fd1c97?w=800',
    'Dog Collar - Adjustable': 'https://images.unsplash.com/photo-1611068435298-63795325c81d?w=800',
    'Dog Harness - Comfort Fit': 'https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=800',
    'Dog Bed - Orthopedic': 'https://images.unsplash.com/photo-1591946614720-90a587da4a36?w=800',
    'Dog Bowl Set - Stainless Steel': 'https://images.unsplash.com/photo-1585849834997-6da8637b3194?w=800',
    'Dog Toy - Rope Tug': 'https://images.unsplash.com/photo-1576201836106-db1758fd1c97?w=800',
    'Dog Toy - Tennis Ball Pack': 'https://images.unsplash.com/photo-1576201836106-db1758fd1c97?w=800',
    'Dog Chew Bone - Natural': 'https://images.unsplash.com/photo-1576201836106-db1758fd1c97?w=800',
    'Dog Raincoat - Waterproof': 'https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=800',
    'Dog ID Tag - Engraved': 'https://images.unsplash.com/photo-1535930749574-1399327ce78f?w=800',
    
    # CAT ACCESSORIES
    'Cat Collar - Breakaway': 'https://images.unsplash.com/photo-1615497001839-b0a0eac3274c?w=800',
    'Cat Scratching Post - Tall': 'https://images.unsplash.com/photo-1545249390-6bdfa286032f?w=800',
    'Cat Bed - Cozy Cave': 'https://images.unsplash.com/photo-1519052537078-e6302a4968d4?w=800',
    'Cat Litter Box - Covered': 'https://images.unsplash.com/photo-1513245543132-31f507417b26?w=800',
    'Cat Bowl Set - Elevated': 'https://images.unsplash.com/photo-1543852786-1cf6624b9987?w=800',
    'Cat Toy - Feather Wand': 'https://images.unsplash.com/photo-1545249390-6bdfa286032f?w=800',
    'Cat Toy - Laser Pointer': 'https://images.unsplash.com/photo-1545249390-6bdfa286032f?w=800',
    'Cat Toy - Interactive Ball': 'https://images.unsplash.com/photo-1545249390-6bdfa286032f?w=800',
    'Cat Tree - Multi-Level': 'https://images.unsplash.com/photo-1545249390-6bdfa286032f?w=800',
    'Cat Carrier - Soft Sided': 'https://images.unsplash.com/photo-1596492784531-6e6eb5ea9205?w=800',
    
    # GROOMING PRODUCTS
    'Pet Shampoo - Hypoallergenic': 'https://images.unsplash.com/photo-1516734212186-a967f81ad0d7?w=800',
    'Pet Brush - Slicker Brush': 'https://images.unsplash.com/photo-1520087619250-584c047581ea?w=800',
    'Nail Clippers - Professional': 'https://images.unsplash.com/photo-1623387641168-d9803ddd3f35?w=800',
    'Pet Wipes - 100 Count': 'https://images.unsplash.com/photo-1516734212186-a967f81ad0d7?w=800'
}

existing = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
if existing == 0:
    conn.execute("""
    INSERT INTO products (name, category, pet_type, price, image_url)
    VALUES
    -- DOG FOOD PRODUCTS
    ('Premium Dry Dog Food - 15kg', 'Food', 'Dog', 2499, ?),
    ('Organic Grain-Free Dog Food', 'Food', 'Dog', 2999, ?),
    ('Puppy Starter Food - 10kg', 'Food', 'Dog', 1899, ?),
    ('Senior Dog Food - 12kg', 'Food', 'Dog', 2199, ?),
    ('Wet Dog Food - 12 Cans', 'Food', 'Dog', 899, ?),
    ('Dog Treats - Training Pack', 'Food', 'Dog', 499, ?),
    
    -- CAT FOOD PRODUCTS
    ('Premium Dry Cat Food - 10kg', 'Food', 'Cat', 2299, ?),
    ('Kitten Starter Food - 5kg', 'Food', 'Cat', 1499, ?),
    ('Indoor Cat Food - 8kg', 'Food', 'Cat', 1999, ?),
    ('Wet Cat Food - 24 Cans', 'Food', 'Cat', 1299, ?),
    ('Cat Treats - Variety Pack', 'Food', 'Cat', 399, ?),
    
    -- DOG ACCESSORIES
    ('Dog Leash - Premium Leather', 'Accessories', 'Dog', 899, ?),
    ('Dog Collar - Adjustable', 'Accessories', 'Dog', 599, ?),
    ('Dog Harness - Comfort Fit', 'Accessories', 'Dog', 1299, ?),
    ('Dog Bed - Orthopedic', 'Accessories', 'Dog', 2499, ?),
    ('Dog Bowl Set - Stainless Steel', 'Accessories', 'Dog', 699, ?),
    ('Dog Toy - Rope Tug', 'Accessories', 'Dog', 299, ?),
    ('Dog Toy - Tennis Ball Pack', 'Accessories', 'Dog', 399, ?),
    ('Dog Chew Bone - Natural', 'Accessories', 'Dog', 499, ?),
    ('Dog Raincoat - Waterproof', 'Accessories', 'Dog', 999, ?),
    ('Dog ID Tag - Engraved', 'Accessories', 'Dog', 199, ?),
    
    -- CAT ACCESSORIES
    ('Cat Collar - Breakaway', 'Accessories', 'Cat', 399, ?),
    ('Cat Scratching Post - Tall', 'Accessories', 'Cat', 1799, ?),
    ('Cat Bed - Cozy Cave', 'Accessories', 'Cat', 1499, ?),
    ('Cat Litter Box - Covered', 'Accessories', 'Cat', 1299, ?),
    ('Cat Bowl Set - Elevated', 'Accessories', 'Cat', 799, ?),
    ('Cat Toy - Feather Wand', 'Accessories', 'Cat', 299, ?),
    ('Cat Toy - Laser Pointer', 'Accessories', 'Cat', 199, ?),
    ('Cat Toy - Interactive Ball', 'Accessories', 'Cat', 499, ?),
    ('Cat Tree - Multi-Level', 'Accessories', 'Cat', 3499, ?),
    ('Cat Carrier - Soft Sided', 'Accessories', 'Cat', 1899, ?),
    
    -- GROOMING PRODUCTS
    ('Pet Shampoo - Hypoallergenic', 'Grooming', 'Both', 599, ?),
    ('Pet Brush - Slicker Brush', 'Grooming', 'Both', 399, ?),
    ('Nail Clippers - Professional', 'Grooming', 'Both', 499, ?),
    ('Pet Wipes - 100 Count', 'Grooming', 'Both', 299, ?)
    """, [
        product_images['Premium Dry Dog Food - 15kg'],
        product_images['Organic Grain-Free Dog Food'],
        product_images['Puppy Starter Food - 10kg'],
        product_images['Senior Dog Food - 12kg'],
        product_images['Wet Dog Food - 12 Cans'],
        product_images['Dog Treats - Training Pack'],
        product_images['Premium Dry Cat Food - 10kg'],
        product_images['Kitten Starter Food - 5kg'],
        product_images['Indoor Cat Food - 8kg'],
        product_images['Wet Cat Food - 24 Cans'],
        product_images['Cat Treats - Variety Pack'],
        product_images['Dog Leash - Premium Leather'],
        product_images['Dog Collar - Adjustable'],
        product_images['Dog Harness - Comfort Fit'],
        product_images['Dog Bed - Orthopedic'],
        product_images['Dog Bowl Set - Stainless Steel'],
        product_images['Dog Toy - Rope Tug'],
        product_images['Dog Toy - Tennis Ball Pack'],
        product_images['Dog Chew Bone - Natural'],
        product_images['Dog Raincoat - Waterproof'],
        product_images['Dog ID Tag - Engraved'],
        product_images['Cat Collar - Breakaway'],
        product_images['Cat Scratching Post - Tall'],
        product_images['Cat Bed - Cozy Cave'],
        product_images['Cat Litter Box - Covered'],
        product_images['Cat Bowl Set - Elevated'],
        product_images['Cat Toy - Feather Wand'],
        product_images['Cat Toy - Laser Pointer'],
        product_images['Cat Toy - Interactive Ball'],
        product_images['Cat Tree - Multi-Level'],
        product_images['Cat Carrier - Soft Sided'],
        product_images['Pet Shampoo - Hypoallergenic'],
        product_images['Pet Brush - Slicker Brush'],
        product_images['Nail Clippers - Professional'],
        product_images['Pet Wipes - 100 Count']
    ])
    conn.commit()
    print(f"Inserted {len(product_images)} products with images")
else:
    # Always update existing products with unique images
    updated_count = 0
    for product_name, image_url in product_images.items():
        cursor = conn.execute("UPDATE products SET image_url = ? WHERE name = ?", (image_url, product_name))
        if cursor.rowcount > 0:
            updated_count += 1
    conn.commit()
    print(f"Updated {updated_count} products with new images")

existing_services = conn.execute("SELECT COUNT(*) FROM grooming_services").fetchone()[0]
if existing_services == 0:
    conn.execute("""
    INSERT INTO grooming_services (name, description, price)
    VALUES
    ('Basic Grooming', 'Bath, brush, nail trim, and ear cleaning', 999),
    ('Full Grooming', 'Complete grooming with haircut, bath, nail trim, and styling', 1999),
    ('Deluxe Spa Package', 'Full grooming + teeth cleaning + aromatherapy bath', 2999),
    ('Nail Trimming', 'Professional nail trimming service', 399),
    ('Ear Cleaning', 'Deep ear cleaning and inspection', 499),
    ('Teeth Cleaning', 'Professional teeth cleaning and dental care', 799)
    """)
    conn.commit()

# Add additional services if they don't exist
new_services = [
    ('De-shedding Treatment', 'Specialized treatment to reduce shedding by up to 90%', 1499),
    ('Tick & Flea Bath', 'Medicated bath to eliminate ticks and fleas', 899),
    ('Paw Pad Moisturizing', 'Healing balm application for cracked or dry paws', 299),
    ('Cat Lion Cut', 'Stylish and practical haircut for long-haired cats', 1599),
    ('Puppy\'s First Groom', 'Gentle introduction to grooming for puppies under 6 months', 799)
]

for name, desc, price in new_services:
    exists = conn.execute("SELECT 1 FROM grooming_services WHERE name = ?", (name,)).fetchone()
    if not exists:
        conn.execute("INSERT INTO grooming_services (name, description, price) VALUES (?, ?, ?)", (name, desc, price))
        print(f"Added new service: {name}")

# Grooming images mapping
grooming_images = {
    'Basic Grooming': 'https://images.unsplash.com/photo-1516734212186-a967f81ad0d7?w=800',
    'Full Grooming': 'https://images.unsplash.com/photo-1599443015574-be5fe8a05783?w=800',
    'Deluxe Spa Package': 'https://images.unsplash.com/photo-1535096677941-622839b23b49?w=800',
    'Nail Trimming': 'https://images.unsplash.com/photo-1598133894008-61f7fdb8cc3a?w=800',
    'Ear Cleaning': 'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=800',
    'Teeth Cleaning': 'https://images.unsplash.com/photo-1555685812-4b943f1cb0eb?w=800',
    'De-shedding Treatment': 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=800',
    'Tick & Flea Bath': 'https://images.unsplash.com/photo-1623387641168-d9803ddd3f35?w=800',
    'Paw Pad Moisturizing': 'https://images.unsplash.com/photo-1598133894008-61f7fdb8cc3a?w=800',
    'Cat Lion Cut': 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=800',
    'Puppy\'s First Groom': 'https://images.unsplash.com/photo-1591160690555-5debfba289f0?w=800'
}

# Update grooming services with images
for service_name, image_url in grooming_images.items():
    conn.execute("UPDATE grooming_services SET image_url = ? WHERE name = ?", (image_url, service_name))

conn.commit()
conn.close()

print("Database initialized successfully!")