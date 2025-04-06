from flask import Flask, render_template, request, session, url_for, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret_key'  # 🔐 Secret key for session management

# ========================================
# 🗂️ DATABASE INITIALIZATION
# ========================================
def create_website_database(filename):
    """Create all necessary tables in the SQLite database if they don't exist."""
    conn = None
    try:
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()

        # Customer info table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                psw TEXT,
                phone_number TEXT,
                location TEXT
            );
        """)

        # Carbon footprint scores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS carbon_score (
                carbon_footprint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT,
                electricity NUMBER,
                gas NUMBER,
                oil NUMBER,
                car NUMBER,
                flights NUMBER,
                recycle_news TEXT,
                recycle_tin TEXT,
                score NUMBER,
                FOREIGN KEY (user_email) REFERENCES customer_info(email)
            );
        """)

        # Bookings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS booking (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT,
                date TEXT,
                time TEXT,
                type TEXT,
                FOREIGN KEY (user_email) REFERENCES customer_info(email)
            );
        """)

        # Energy usage data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS energy_usage (
                energy_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT,
                house_type TEXT,
                bedroom_number INTEGER,
                insulation TEXT, 
                heating TEXT,
                water TEXT,
                cook TEXT,
                energy_usage NUMBER,
                FOREIGN KEY (user_email) REFERENCES customer_info(email)
            );
        """)

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

# ========================================
# 📦 DATABASE HELPERS
# ========================================
def save_data(filename, name, email, psw, phone_number, location):
    """Save new user registration info."""
    try:
        with sqlite3.connect(filename) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO customer_info (name, email, psw, phone_number, location)
                VALUES (?, ?, ?, ?, ?);
            """, (name, email, psw, phone_number, location))
    except sqlite3.Error as e:
        print(f"Database error: {e}")

def list_customer_info(filename):
    """List all customers."""
    try:
        with sqlite3.connect(filename) as conn:
            cursor = conn.cursor()
            return cursor.execute("SELECT * FROM customer_info").fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

def save_data_carbon_score(filename, user_email, electricity, gas, oil, car, flights, recycle_news, recycle_tin, score):
    """Save carbon footprint score."""
    try:
        with sqlite3.connect(filename) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO carbon_score (user_email, electricity, gas, oil, car, flights, recycle_news, recycle_tin, score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (user_email, electricity, gas, oil, car, flights, recycle_news, recycle_tin, score))
    except sqlite3.Error as e:
        print(f"Database error: {e}")

def list_carbon_score_by_user(filename, user_email):
    """Fetch carbon scores for a given user."""
    try:
        with sqlite3.connect(filename) as conn:
            cursor = conn.cursor()
            return cursor.execute("SELECT * FROM carbon_score WHERE user_email = ?", (user_email,)).fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

def save_booking(filename, user_email, date, time, type_):
    """Save booking details."""
    try:
        with sqlite3.connect(filename) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO booking (user_email, date, time, type)
                VALUES (?, ?, ?, ?);
            """, (user_email, date, time, type_))
    except sqlite3.Error as e:
        print(f"Database error: {e}")

def list_bookings_by_user(filename, user_email):
    """Fetch bookings for a user."""
    try:
        with sqlite3.connect(filename) as conn:
            cursor = conn.cursor()
            return cursor.execute("SELECT * FROM booking WHERE user_email = ?", (user_email,)).fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

def save_energy_usage(filename, user_email, house_type, bedroom_number, insulation, heating, water, cook, energy_usage):
    """Save energy usage details."""
    try:
        with sqlite3.connect(filename) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO energy_usage (user_email, house_type, bedroom_number, insulation, heating, water, cook, energy_usage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (user_email, house_type, bedroom_number, insulation, heating, water, cook, energy_usage))
    except sqlite3.Error as e:
        print(f"Database error: {e}")

def list_energy_usage_by_user(filename, user_email):
    """Fetch energy usage data for a user."""
    try:
        with sqlite3.connect(filename) as conn:
            cursor = conn.cursor()
            return cursor.execute("SELECT * FROM energy_usage WHERE user_email = ?", (user_email,)).fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

# ========================================
# 🌐 ROUTES
# ========================================
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/green_product")
def green_product():
    return render_template("green_product.html")

@app.route("/carbon_footprint")
def carbon_footprint():
    return render_template("carbon_footprint.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/carbon_footprint_main")
def carbon_footprint_main ():
    return render_template("carbon_footprint_main.html")


@app.route("/signup", methods=['POST'])
def signupost():
    name = request.form["name"]
    email = request.form["email"]
    psw = request.form["psw"]
    phone_number = request.form["phone_number"]
    location = request.form["location"]
    save_data("customer_info.db", name, email, psw, phone_number, location)
    return render_template("login.html", people=list_customer_info("customer_info.db"))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["psw"]
        user_exists, _ = login_user("customer_info.db", email, password)
        if user_exists == "valid":
            session["email"] = email
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", status="Invalid login")
    return render_template('login.html')

def login_user(filename, email, password):
    """Validate login credentials."""
    try:
        with sqlite3.connect(filename) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customer_info WHERE email = ? AND psw = ?", (email, password))
            user = cursor.fetchone()
            return ("valid", user) if user else ("invalid", None)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return "error", None

@app.route("/carbon_footprint_calc", methods=['GET', 'POST'])
def carbon_footprint_calc():
    if request.method == 'POST':
        user_email = session.get("email")
        if not user_email:
            return redirect(url_for("login"))

        electricity = float(request.form.get("electricity", 0))
        gas = float(request.form.get("gas", 0))
        oil = float(request.form.get("oil", 0))
        car = float(request.form.get("car", 0))
        flights = float(request.form.get("flights", 0))
        recycle_news = request.form.get("recycle_newspaper", "no")
        recycle_tin = request.form.get("recycle_tin", "no")
        score = electricity + gas + oil + car + flights  # Example calc

        save_data_carbon_score("customer_info.db", user_email, electricity, gas, oil, car, flights, recycle_news, recycle_tin, score)
        return redirect(url_for("dashboard"))

    return render_template("carbon_footprint_calc.html")

@app.route("/energy_usage", methods=['GET', 'POST'])
def energy_usage():
    """Collect and save user energy usage (without calculating the score)."""
    user_email = session.get("email")
    if not user_email:
        return redirect(url_for("login"))

    if request.method == 'POST':
        # Collecting form data from the user
        house_type = request.form.get("house_type")
        bedroom_number = int(request.form.get("bedroom_number", 0))  # Default to 0 if not provided
        insulation = request.form.get("insulation")
        heating = request.form.get("heating")  # Heating method (electricity, gas, etc.)
        water = request.form.get("water")  # Water heating type (electricity, gas, etc.)
        cook = request.form.get("cook")  # Cooking method (electricity, gas, etc.)

        energy_usage = None  # You can calculate it later somewhere else

        save_energy_usage("customer_info.db", user_email, house_type, bedroom_number, insulation, heating, water, cook, energy_usage)
        return redirect(url_for("dashboard"))

    return render_template("energy_usage.html")

@app.route("/booking", methods=['GET', 'POST'])
def booking():
    user_email = session.get("email")
    if not user_email:
        return redirect(url_for("login"))

    if request.method == 'POST':
        date = request.form.get("date")
        time = request.form.get("time")
        type_ = request.form.get("type")
        save_booking("customer_info.db", user_email, date, time, type_)
        return redirect(url_for("dashboard"))

    return render_template("booking.html")

@app.route("/dashboard")
def dashboard():
    """Main dashboard page showing user data."""
    user_email = session.get("email")
    if not user_email:
        return redirect(url_for("login"))

    carbon_scores = list_carbon_score_by_user("customer_info.db", user_email)
    bookings = list_bookings_by_user("customer_info.db", user_email)
    energy_usages = list_energy_usage_by_user("customer_info.db", user_email)

    return render_template("dashboard.html", carbon_scores=carbon_scores, bookings=bookings, energy_usages=energy_usages)

@app.route("/reset_password")
def reset_password():
    return render_template("reset_password.html")

# ========================================
# 🚀 MAIN
# ========================================
if __name__ == "__main__":
    create_website_database("customer_info.db")
    app.run(debug=True)
