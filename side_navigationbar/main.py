from flask import Flask, render_template, request, session, url_for, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Create SQLite Database and Tables
def create_sqlite_database(filename):
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, psw TEXT, phone_number TEXT, location TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS booking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, email TEXT, time TEXT, type TEXT,
            FOREIGN KEY(email) REFERENCES customer_info(email)
        )
    """)
    conn.commit()
    conn.close()

# Save user data to customer_info table
def save_data(filename, name, email, psw, phone_number, location):
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customer_info (name, email, psw, phone_number, location)
        VALUES (?, ?, ?, ?, ?)
    """, (name, email, psw, phone_number, location))
    conn.commit()
    conn.close()

# Check user login credentials
def login_user(filename, email, password):
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customer_info WHERE email = ? AND psw = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return "valid" if user else "invalid"

# Fetch user data
def list_main(filename, email):
    conn = sqlite3.connect(filename)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customer_info WHERE email = ?", (email,))
    data = cursor.fetchone()
    conn.close()
    return data

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

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        psw = request.form["psw"]
        phone_number = request.form["phone_number"]
        location = request.form["location"]
        save_data("customer_info.db", name, email, psw, phone_number, location)
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["psw"]
        if login_user("customer_info.db", email, password) == "valid":
            session["email"] = email  # Store email in session
            return redirect(url_for("profile"))  # Redirect to profile after login
        return render_template("login.html", status="Invalid username or password, try again")
    return render_template("login.html")


@app.route("/profile", methods=['GET'])
def profile():
    if "email" not in session:
        return redirect(url_for("login"))  # Redirect to login if not logged in
    email = session["email"]
    user_data = list_main("customer_info.db", email)

    if user_data:
        name = user_data[1]  # Assuming 'name' is the second column in the table
    else:
        name = "User"  # Default if no data is found

    return render_template("profile.html", logged_in_user=user_data, name=name)



@app.route("/booking", methods=['GET', 'POST'])
def booking():
    if "email" not in session:
        return redirect(url_for("login"))
    if request.method == 'POST':
        email = session["email"]
        date = request.form["date"]
        time = request.form["time"]
        type = request.form["type"]
        conn = sqlite3.connect("customer_info.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO booking (email, date, time, type)
            VALUES (?, ?, ?, ?)
        """, (email, date, time, type))
        conn.commit()
        conn.close()
        return redirect(url_for("profile"))
    return render_template("booking.html")



if __name__ == "__main__":
    app.debug = True  # Enable debug mode
    create_sqlite_database("customer_info.db")
    app.run()