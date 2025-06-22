import os
import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib

app = Flask(__name__)
CORS(app)

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "user"),
        password=os.getenv("DB_PASSWORD", "password"),
        database=os.getenv("DB_NAME", "d2dcrm")
    )

@app.route("/users", methods=["GET"])
def list_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, email FROM users")
    users = cursor.fetchall()

    for user in users:
        email = user["email"]

        cursor.execute("SELECT id FROM trips WHERE userEmail = %s", (email,))
        trips = cursor.fetchall()
        user["tripIds"] = [trip["id"] for trip in trips]

        cursor.execute("SELECT id FROM prospects WHERE userEmail = %s", (email,))
        prospects = cursor.fetchall()
        user["prospectIds"] = [p["id"] for p in prospects]

        cursor.execute("SELECT id FROM customers WHERE userEmail = %s", (email,))
        customers = cursor.fetchall()
        user["customerIds"] = [c["id"] for c in customers]

    cursor.close()
    conn.close()
    return jsonify(users)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    raw_password = data.get("password")
    hashed_password = hash_password(raw_password)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check for existing email
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"message": "User already exists"}), 400

    cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, hashed_password))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "User created"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    raw_password = data.get("password")
    hashed_password = hash_password(raw_password)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, hashed_password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return jsonify({"message": "Login successful"})
    return jsonify({"message": "Invalid credentials"}), 401

@app.route("/prospects", methods=["POST"])
def create_prospect():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO prospects (fullName, address, count, list, userEmail, contactEmail, contactPhone, notes, latitude, longitude)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
""", (
    data["fullName"], data["address"], data.get("count", 0),
    data.get("list", "Prospects"), data["userEmail"],
    data.get("contactEmail", ""), data.get("contactPhone", ""),
    data.get("notes", ""), data["latitude"], data["longitude"]
))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Prospect created"}), 201


@app.route("/prospects", methods=["GET"])
def get_prospects():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Step 1: Get all prospects
    cursor.execute("SELECT * FROM prospects")
    prospects = cursor.fetchall()

    # Step 2: For each prospect, fetch and merge notes
    for prospect in prospects:
        prospect_id = prospect["id"]
        cursor.execute("SELECT content FROM notes WHERE prospectId = %s ORDER BY date ASC", (prospect_id,))
        notes = cursor.fetchall()

        # Merge notes into a single string (or use an array if preferred)
        note_texts = [n["content"] for n in notes]
        all_notes = [prospect["notes"]] if prospect["notes"] else []
        prospect["notes"] = all_notes + note_texts

    cursor.close()
    conn.close()
    return jsonify(prospects)


@app.route("/prospects/<int:prospect_id>", methods=["PUT"])
def update_prospect(prospect_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE prospects
        SET fullName=%s, address=%s, count=%s, list=%s, userEmail=%s, contactEmail=%s, contactPhone=%s, notes=%s
        WHERE id=%s
    """, (
        data["fullName"], data["address"], data.get("count", 0),
        data.get("list", "Prospects"), data["userEmail"],
        data.get("contactEmail", ""), data.get("contactPhone", ""),
        data.get("notes", ""), prospect_id
    ))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Prospect updated"})


@app.route("/prospects/<int:prospect_id>", methods=["DELETE"])
def delete_prospect(prospect_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prospects WHERE id = %s", (prospect_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Prospect deleted"})

@app.route("/prospects/<int:prospect_id>/notes", methods=["POST"])
def add_note(prospect_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notes (prospectId, content, authorEmail, date)
        VALUES (%s, %s, %s, %s)
    """, (
        prospect_id,
        data["content"],
        data["authorEmail"],
        data.get("date")  # Optional; can be null to default to current timestamp
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Note added"}), 201


@app.route("/prospects/<int:prospect_id>/notes", methods=["GET"])
def get_notes(prospect_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notes WHERE prospectId = %s ORDER BY date DESC", (prospect_id,))
    notes = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(notes)


@app.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Note deleted"})

@app.route("/prospects/<int:prospect_id>/knocks", methods=["POST"])
def add_knock(prospect_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Step 1: Insert knock
    cursor.execute("""
        INSERT INTO knocks (prospectId, date, status, latitude, longitude, userEmail)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        prospect_id,
        data["date"],
        data["status"],
        data["latitude"],
        data["longitude"],
        data["userEmail"]
    ))

    # Step 2: Increment count for the prospect
    cursor.execute("""
        UPDATE prospects
        SET count = count + 1
        WHERE id = %s
    """, (prospect_id,))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Knock added and count updated"}), 201


@app.route("/prospects/<int:prospect_id>/knocks", methods=["GET"])
def get_knocks(prospect_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM knocks WHERE prospectId = %s ORDER BY date DESC", (prospect_id,))
    knocks = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(knocks)

@app.route("/prospects/<int:prospect_id>", methods=["GET"])
def get_prospect_by_id(prospect_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch the prospect
    cursor.execute("SELECT * FROM prospects WHERE id = %s", (prospect_id,))
    prospect = cursor.fetchone()

    if not prospect:
        cursor.close()
        conn.close()
        return jsonify({"error": "Prospect not found"}), 404

    # Fetch related notes
    cursor.execute("SELECT content FROM notes WHERE prospectId = %s ORDER BY date ASC", (prospect_id,))
    notes = cursor.fetchall()

    # Combine existing text notes with note table entries
    note_texts = [n["content"] for n in notes]
    all_notes = [prospect["notes"]] if prospect["notes"] else []
    prospect["notes"] = all_notes + note_texts

    cursor.close()
    conn.close()
    return jsonify(prospect)

@app.route("/customers", methods=["POST"])
def create_customer():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO customers (fullName, address, count, userEmail, contactEmail, contactPhone, notes, latitude, longitude)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data["fullName"],
        data["address"],
        data.get("count", 0),
        data["userEmail"],
        data.get("contactEmail", ""),
        data.get("contactPhone", ""),
        data.get("notes", ""),
        data.get("latitude", 0.0),
        data.get("longitude", 0.0)
    ))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Customer created"}), 201

@app.route("/customers", methods=["GET"])
def get_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Step 1: Get all customers
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()

    # Step 2: Attach notes to each customer
    for customer in customers:
        customer_id = customer["id"]
        cursor.execute("SELECT content FROM notes WHERE customerId = %s ORDER BY date ASC", (customer_id,))
        notes = cursor.fetchall()

        note_texts = [n["content"] for n in notes]
        all_notes = [customer["notes"]] if customer["notes"] else []
        customer["notes"] = all_notes + note_texts

    cursor.close()
    conn.close()
    return jsonify(customers)

@app.route("/customers/<int:customer_id>", methods=["GET"])
def get_customer_by_id(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers WHERE id = %s", (customer_id,))
    customer = cursor.fetchone()
    cursor.close()
    conn.close()

    if customer:
        return jsonify(customer)
    return jsonify({"error": "Customer not found"}), 404

@app.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Customer deleted"})

@app.route("/customers/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE customers
        SET fullName = %s, address = %s, count = %s, userEmail = %s,
            contactEmail = %s, contactPhone = %s, notes = %s
        WHERE id = %s
    """, (
        data["fullName"], data["address"], data.get("count", 0),
        data["userEmail"], data.get("contactEmail", ""),
        data.get("contactPhone", ""), data.get("notes", ""), customer_id
    ))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Customer updated"})

@app.route("/customers/<int:customer_id>/notes", methods=["POST"])
def add_note_to_customer(customer_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notes (customerId, content, authorEmail, date)
        VALUES (%s, %s, %s, %s)
    """, (
        customer_id,
        data["content"],
        data["authorEmail"],
        data.get("date")
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Customer note added"}), 201

@app.route("/customers/<int:customer_id>/notes", methods=["GET"])
def get_notes_for_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notes WHERE customerId = %s ORDER BY date DESC", (customer_id,))
    notes = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(notes)

@app.route("/customers/<int:customer_id>/knocks", methods=["POST"])
def add_knock_to_customer(customer_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert knock for customer
    cursor.execute("""
        INSERT INTO knocks (customerId, date, status, latitude, longitude, userEmail)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        customer_id,
        data["date"],
        data["status"],
        data["latitude"],
        data["longitude"],
        data["userEmail"]
    ))

    # Increment knock count
    cursor.execute("""
        UPDATE customers
        SET count = count + 1
        WHERE id = %s
    """, (customer_id,))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Customer knock added and count updated"}), 201

@app.route("/customers/<int:customer_id>/knocks", methods=["GET"])
def get_knocks_for_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM knocks WHERE customerId = %s ORDER BY date DESC", (customer_id,))
    knocks = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(knocks)


@app.route("/trips", methods=["POST"])
def create_trip():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO trips (id, userEmail, startAddress, endAddress, miles, date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data["id"],
        data["userEmail"],
        data["startAddress"],
        data["endAddress"],
        data["miles"],
        data["date"]
    ))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Trip created"}), 201

@app.route("/trips", methods=["GET"])
def get_trips():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM trips ORDER BY date DESC")
    trips = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(trips)

@app.route("/trips/<trip_id>", methods=["DELETE"])
def delete_trip(trip_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM trips WHERE id = %s", (trip_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Trip deleted"})

@app.route("/users/<user_email>/prospects", methods=["GET"])
def get_prospects_for_user(user_email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM prospects WHERE userEmail = %s", (user_email,))
    prospects = cursor.fetchall()

    for prospect in prospects:
        prospect_id = prospect["id"]
        cursor.execute("SELECT content FROM notes WHERE prospectId = %s ORDER BY date ASC", (prospect_id,))
        notes = cursor.fetchall()
        note_texts = [n["content"] for n in notes]
        all_notes = [prospect["notes"]] if prospect["notes"] else []
        prospect["notes"] = all_notes + note_texts

    cursor.close()
    conn.close()
    return jsonify(prospects)

@app.route("/users/<int:user_id>/prospects", methods=["GET"])
def get_prospects_by_user_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Look up the user's email
    cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404

    email = user["email"]

    # Get all prospects for the user
    cursor.execute("SELECT * FROM prospects WHERE userEmail = %s", (email,))
    prospects = cursor.fetchall()

    for prospect in prospects:
        prospect_id = prospect["id"]
        cursor.execute("SELECT content FROM notes WHERE prospectId = %s ORDER BY date ASC", (prospect_id,))
        notes = cursor.fetchall()
        note_texts = [n["content"] for n in notes]
        all_notes = [prospect["notes"]] if prospect["notes"] else []
        prospect["notes"] = all_notes + note_texts

    cursor.close()
    conn.close()
    return jsonify(prospects)

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, email FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404

    email = user["email"]

    cursor.execute("SELECT id FROM trips WHERE userEmail = %s", (email,))
    trips = cursor.fetchall()
    user["tripIds"] = [trip["id"] for trip in trips]

    cursor.execute("SELECT id FROM prospects WHERE userEmail = %s", (email,))
    prospects = cursor.fetchall()
    user["prospectIds"] = [p["id"] for p in prospects]

    cursor.execute("SELECT id FROM customers WHERE userEmail = %s", (email,))
    customers = cursor.fetchall()
    user["customerIds"] = [c["id"] for c in customers]

    cursor.close()
    conn.close()
    return jsonify(user)

@app.route("/users/<user_email>/customers", methods=["GET"])
def get_customers_for_user(user_email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM customers WHERE userEmail = %s", (user_email,))
    customers = cursor.fetchall()

    for customer in customers:
        customer_id = customer["id"]
        cursor.execute("SELECT content FROM notes WHERE customerId = %s ORDER BY date ASC", (customer_id,))
        notes = cursor.fetchall()
        note_texts = [n["content"] for n in notes]
        all_notes = [customer["notes"]] if customer["notes"] else []
        customer["notes"] = all_notes + note_texts

    cursor.close()
    conn.close()
    return jsonify(customers)

@app.route("/users/<int:user_id>/customers", methods=["GET"])
def get_customers_by_user_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404

    user_email = user["email"]

    cursor.execute("SELECT * FROM customers WHERE userEmail = %s", (user_email,))
    customers = cursor.fetchall()

    for customer in customers:
        customer_id = customer["id"]
        cursor.execute("SELECT content FROM notes WHERE customerId = %s ORDER BY date ASC", (customer_id,))
        notes = cursor.fetchall()
        note_texts = [n["content"] for n in notes]
        all_notes = [customer["notes"]] if customer["notes"] else []
        customer["notes"] = all_notes + note_texts

    cursor.close()
    conn.close()
    return jsonify(customers)

@app.route("/users/<int:user_id>/customers/<int:customer_id>", methods=["GET"])
def get_customer_for_user(user_id, customer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Step 1: Look up user email
    cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404

    user_email = user["email"]

    # Step 2: Look up the customer with the given ID and user's email
    cursor.execute("SELECT * FROM customers WHERE id = %s AND userEmail = %s", (customer_id, user_email))
    customer = cursor.fetchone()
    if not customer:
        cursor.close()
        conn.close()
        return jsonify({"error": "Customer not found for this user"}), 404

    # Step 3: Attach notes
    cursor.execute("SELECT content FROM notes WHERE customerId = %s ORDER BY date ASC", (customer_id,))
    notes = cursor.fetchall()
    note_texts = [n["content"] for n in notes]
    all_notes = [customer["notes"]] if customer["notes"] else []
    customer["notes"] = all_notes + note_texts

    cursor.close()
    conn.close()
    return jsonify(customer)

@app.route("/users/<int:user_id>/prospects/<int:prospect_id>", methods=["GET"])
def get_prospect_for_user(user_id, prospect_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Step 1: Look up the user's email
    cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404

    user_email = user["email"]

    # Step 2: Get the prospect with the given ID and userEmail
    cursor.execute("SELECT * FROM prospects WHERE id = %s AND userEmail = %s", (prospect_id, user_email))
    prospect = cursor.fetchone()
    if not prospect:
        cursor.close()
        conn.close()
        return jsonify({"error": "Prospect not found for this user"}), 404

    # Step 3: Attach notes
    cursor.execute("SELECT content FROM notes WHERE prospectId = %s ORDER BY date ASC", (prospect_id,))
    notes = cursor.fetchall()
    note_texts = [n["content"] for n in notes]
    all_notes = [prospect["notes"]] if prospect["notes"] else []
    prospect["notes"] = all_notes + note_texts

    cursor.close()
    conn.close()
    return jsonify(prospect)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)