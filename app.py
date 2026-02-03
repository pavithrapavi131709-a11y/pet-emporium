from flask import Flask, render_template, redirect, session, request
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "supersecretkey"

def init_db_if_missing():
    if not os.path.exists("database.db"):
        print("Database not found, initializing...")
        try:
            import init_db
            print("Database initialized successfully.")
        except Exception as e:
            print(f"Error initializing database: {e}")

# Initialize DB on startup
init_db_if_missing()

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def is_admin():
    u = session.get('username')
    owner = os.environ.get('ADMIN_USER', 'owner')
    return u in (owner, 'admin')

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not is_admin():
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

# AUTH
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = (request.form.get('username') or "").strip()
        password = request.form.get('password') or ""
        confirm_password = request.form.get('confirm_password') or ""

        if not username or not password:
            return render_template("register.html", error="Username and password are required.")
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match.")

        password_hash = generate_password_hash(password)

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password_hash),
            )
            conn.commit()
            user = conn.execute("SELECT id, username FROM users WHERE username = ?", (username,)).fetchone()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("register.html", error="Username already exists. Please choose another.")

        conn.close()
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect('/')

    return render_template("register.html", error=None)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = (request.form.get('username') or "").strip()
        password = request.form.get('password') or ""

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if not user or not check_password_hash(user['password'], password):
            return render_template("login.html", error="Invalid username or password.")

        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect('/')

    return render_template("login.html", error=None)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect('/')

@app.route('/admin')
@admin_required
def admin():
    conn = get_db()
    users_count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()['c']
    products_count = conn.execute("SELECT COUNT(*) AS c FROM products").fetchone()['c']
    appointments_count = conn.execute("SELECT COUNT(*) AS c FROM appointments").fetchone()['c']
    services_count = conn.execute("SELECT COUNT(*) AS c FROM grooming_services").fetchone()['c']
    recent_appointments = conn.execute("SELECT name, pet, date FROM appointments ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()
    return render_template("admin.html", users_count=users_count, products_count=products_count, appointments_count=appointments_count, services_count=services_count, recent_appointments=recent_appointments)

# HOME / ABOUT
@app.route('/')
def home():
    return render_template("index.html")

# PRODUCTS
@app.route('/products')
def products():
    pet_type = request.args.get('pet_type', '')
    category = request.args.get('category', '')
    
    conn = get_db()
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    
    if pet_type:
        query += " AND pet_type = ?"
        params.append(pet_type)
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    query += " ORDER BY pet_type, category, name"
    items = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template("products.html", items=items, selected_pet=pet_type, selected_category=category)

# ADD TO CART
@app.route('/add-to-cart/<int:pid>')
def add_to_cart(pid):
    cart = session.get('cart', [])
    cart.append(pid)
    session['cart'] = cart
    return redirect('/cart')

# CART
@app.route('/cart')
def cart():
    cart_ids = session.get('cart', [])
    if not cart_ids:
        return render_template("cart.html", items=[], total=0)

    conn = get_db()
    query = f"SELECT * FROM products WHERE id IN ({','.join('?'*len(cart_ids))})"
    items = conn.execute(query, cart_ids).fetchall()
    conn.close()

    total = sum(item['price'] for item in items)
    return render_template("cart.html", items=items, total=total)

# CLEAR CART
@app.route('/clear-cart')
def clear_cart():
    session.pop('cart', None)
    return redirect('/cart')

# CHECKOUT
@app.route('/checkout', methods=['POST'])
def checkout():
    session.pop('cart', None)
    return render_template("cart.html", items=[], total=0, checkout_success=True)

# GROOMING
@app.route('/grooming', methods=['GET','POST'])
def grooming():
    conn = get_db()
    services = conn.execute("SELECT * FROM grooming_services").fetchall()
    conn.close()
    
    if request.method == 'POST':
        return render_template("grooming.html", booked=True, services=services)
    return render_template("grooming.html", booked=False, services=services)

if __name__ == "__main__":
    app.run(debug=True)
