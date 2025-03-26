from flask import Flask, render_template, request, session, url_for, redirect
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session


# Create a database connection to an SQLite database
def create_sqlite_database(filename):
    conn = None
    try:
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        # Create a table called customer_info if it doesn't exist
        query1 = ("CREATE TABLE IF NOT EXISTS customer_info"
                  "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                  "name TEXT, email TEXT, psw TEXT, phone_number TEXT ,location TEXT);")
        cursor.execute(query1)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

# Saves the data that the user used to sign up in the customer_info table
def save_data(filename, name, email, psw, phone_number, location):
    conn = None
    try:
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        # Use parameterized query to avoid SQL injection
        query3 = ("INSERT INTO customer_info (name, email, psw, phone_number , location) "
                  "VALUES (?, ?, ?, ?, ?);")  # Using customer_info table
        cursor.execute(query3, (name, email, psw, phone_number , location))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def list_data(filename):
    conn = None
    try:
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        query = "SELECT * FROM customer_info"  # Querying customer_info table
        result = cursor.execute(query)
        data = result.fetchall()
        conn.commit()
        return data
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

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

# Route for the signup page (Data saving)
@app.route("/signup", methods=['POST'])
def signupost():
    name = request.form["name"]
    email = request.form["email"]
    psw = request.form["psw"]
    phone_number = request.form["phone_number"]
    location = request.form["location"]
    # Save the user data to the customer_info table
    save_data("customer_info.db", name, email, psw, phone_number , location)
    return render_template("login.html", people=list_data("customer_info.db"))


# Route for the login page
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["psw"]
        user_exists, user_role = login_user("customer_info.db", email, password)

        if user_exists == "valid":
            session["email"] = email
            return redirect(url_for("home"))  # Redirect to home after login
        else:
            return render_template("login.html", status="Invalid username or password, try again")
    return render_template('login.html')


# Function to log in a user
def login_user(filename, email, password):
    conn = None
    try:
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customer_info WHERE email = ? AND psw = ?", (email, password))
        user = cursor.fetchone()
        if user:
            return "valid", [2]
        else:
            return "invalid", None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return "error", None
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    app.debug = True  # Enable debug mode for detailed error messages
    create_sqlite_database("customer_info.db")
    app.run()
