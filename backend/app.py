import os
import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
    cursor.execute("SELECT email FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check for existing email
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"message": "User already exists"}), 400

    cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "User created"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
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
        INSERT INTO prospects (fullName, address, count, list, userEmail, contactEmail, contactPhone, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data["fullName"], data["address"], data.get("count", 0),
        data.get("list", "Prospects"), data["userEmail"],
        data.get("contactEmail", ""), data.get("contactPhone", ""),
        data.get("notes", "")
    ))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Prospect created"}), 201


@app.route("/prospects", methods=["GET"])
def get_prospects():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM prospects")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)


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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)