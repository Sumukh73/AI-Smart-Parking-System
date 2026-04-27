from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = "mysecretkey"

# ---------------- MYSQL CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Moonwalk@321",
    database="smart_parking"
)

cursor = db.cursor()

# ---------------- CONFIG ----------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

# ---------------- LOGIN PAGE ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Wrong username or password")

    return render_template("login.html")


# ---------------- DASHBOARD PAGE ----------------
@app.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect(url_for("login"))

    cursor.execute("SELECT * FROM parking_data ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()

    if row:
        data = {
            "total": row[1],
            "available": row[2],
            "occupied": row[3],
            "cars": row[4],
            "bikes": row[5],
            "bus": row[6],
            "truck": row[7],
            "capacity": 50,
            "status": "PARKING FULL" if row[1] >= 50 else "PARKING AVAILABLE"
        }
    else:
        data = {
            "cars": 0,
            "bikes": 0,
            "bus": 0,
            "truck": 0,
            "total": 0,
            "available": 0,
            "occupied": 0,
            "capacity": 50,
            "status": "PARKING AVAILABLE"
        }

    return render_template("dashboard.html", data=data)


# ---------------- API FOR LIVE DATA ----------------
@app.route("/api/data")
def api_data():
    cursor.execute("SELECT * FROM parking_data ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()

    if row:
        data = {
            "total": row[1],
            "available": row[2],
            "occupied": row[3],
            "cars": row[4],
            "bikes": row[5],
            "bus": row[6],
            "truck": row[7]
        }
    else:
        data = {
            "cars": 0,
            "bikes": 0,
            "bus": 0,
            "truck": 0,
            "total": 0,
            "available": 0,
            "occupied": 0
        }

    return jsonify(data)


# ---------------- API FOR HISTORY ----------------
@app.route("/api/history")
def api_history():
    if not session.get("admin"):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Simulate a detailed detection history since we currently only store aggregate counts
    # This simulates data that would come from an OCR-integrated system
    cursor.execute("SELECT * FROM parking_data ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    
    import random
    import datetime
    
    vehicle_types = ["Car", "Bike", "Bus", "Truck"]
    states = ["UP32", "DL01", "MH12", "KA05", "TN01"]
    
    history = []
    for i, row in enumerate(rows):
        # We'll generate a few vehicle-level records for each aggregate record
        # This makes the history look like a real-time stream of individual detections
        timestamp = datetime.datetime.now() - datetime.timedelta(minutes=i*15)
        
        # Determine a type based on what was in the aggregate record (cars, bikes, etc)
        v_type = "Car"
        if row[5] > row[4]: v_type = "Bike"
        elif row[6] > 0: v_type = "Bus"
        elif row[7] > 0: v_type = "Truck"
        else: v_type = random.choice(vehicle_types)

        history.append({
            "id": row[0],
            "vehicle_number": f"{random.choice(states)} AB {random.randint(1000, 9999)}",
            "type": v_type,
            "time": timestamp.strftime("%Y-%m-%d %H:%M"),
            "confidence": f"{random.randint(85, 99)}%"
        })
        
    return jsonify(history)


# ---------------- API FOR PARKING LOCATIONS ----------------
@app.route("/api/parking-locations")
def api_parking_locations():
    # Simulate multiple smart parking locations for demo purposes
    locations = [
        {
            "id": 1,
            "name": "Central Hub Parking",
            "lat": 26.8467, # Lucknow coordinates
            "lng": 80.9462,
            "total_slots": 50,
            "available_slots": 12,
            "address": "Hazratganj, Lucknow, UP"
        },
        {
            "id": 2,
            "name": "Smart Plaza Parking",
            "lat": 26.8550,
            "lng": 80.9550,
            "total_slots": 30,
            "available_slots": 5,
            "address": "Gomti Nagar, Lucknow, UP"
        },
        {
            "id": 3,
            "name": "Tech Park A1",
            "lat": 26.8300,
            "lng": 80.9200,
            "total_slots": 100,
            "available_slots": 45,
            "address": "Alambagh, Lucknow, UP"
        }
    ]
    return jsonify(locations)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)