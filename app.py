from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enables requests from iOS app

# In-memory user store (reset on restart)
users = []

@app.route("/users", methods=["GET"])
def list_users():
    return jsonify(users)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if any(u["email"] == email for u in users):
        return jsonify({"message": "User already exists"}), 400

    users.append({"email": email, "password": password})
    return jsonify({"message": "User created"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    for user in users:
        if user["email"] == email and user["password"] == password:
            return jsonify({"message": "Login successful"})
    return jsonify({"message": "Invalid credentials"}), 401

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
