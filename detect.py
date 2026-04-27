import mysql.connector
from ultralytics import YOLO
import cv2
import time

# ---------------- MYSQL CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Moonwalk@321",
    database="smart_parking"
)

cursor = db.cursor()

# ---------------- YOLO MODEL ----------------
model = YOLO("yolov8n.pt")

PARKING_CAPACITY = 50

cap = cv2.VideoCapture("video.mp4")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, stream=True)

    car = bike = bus = truck = 0

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            if cls == 2:
                car += 1
            elif cls == 3:
                bike += 1
            elif cls == 5:
                bus += 1
            elif cls == 7:
                truck += 1

    total = car + bike + bus + truck
    available = max(0, PARKING_CAPACITY - total)
    occupied = total

    # ---------------- SAVE TO MYSQL (FULL DATA) ----------------
    cursor.execute("""
        INSERT INTO parking_data 
        (total, available, occupied, cars, bikes, bus, truck)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (total, available, occupied, car, bike, bus, truck))

    db.commit()

    # ---------------- DISPLAY ----------------
    frame = cv2.resize(frame, (1280, 720))

    cv2.putText(frame, f"Cars: {car}", (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    cv2.putText(frame, f"Bikes: {bike}", (30, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0), 2)
    cv2.putText(frame, f"Bus: {bus}", (30, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2)
    cv2.putText(frame, f"Truck: {truck}", (30, 160),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

    cv2.putText(frame, f"Total Vehicles: {total}",
                (30, 210), cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0,255,255), 3)

    status = "PARKING FULL" if total >= PARKING_CAPACITY else "PARKING AVAILABLE"
    color = (0,0,255) if total >= PARKING_CAPACITY else (0,255,0)

    cv2.putText(frame, f"Status: {status}",
                (30, 270), cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                color, 4)

    cv2.imshow("Smart Parking AI", frame)

    # Exit on ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

    # Delay (important)
    time.sleep(0.5)

cap.release()
cv2.destroyAllWindows()