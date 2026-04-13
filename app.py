from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# =========================
# INDEX PAGE
# =========================
@app.route("/")
def index():
    return render_template("index.html")

# =========================
# LOGIN PAGE
# =========================
@app.route("/login")
def login():
    return render_template("login.html")

# =========================
# PLANNER PAGE
# =========================
@app.route("/planner")
def planner():
    return render_template("planner.html")

# =========================
# RESULT PAGE (MAIN LOGIC)
# =========================
@app.route("/result", methods=['POST'])
def result():

    city = request.form.get('city')
    days = request.form.get('days')

    plan = generate_itinerary(city, days)

    return render_template("result.html", city=city,days=days,plan=plan)


# =========================
# ITINERARY FUNCTION
def generate_itinerary(city_name, days):

    conn = sqlite3.connect("itinerary.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT place_name, hours 
        FROM places 
        WHERE LOWER(city) = LOWER(?)
    """, (city_name,))

    places = cursor.fetchall()
    conn.close()

    itinerary = {}
    day = 1
    total_hours = 0
    max_days = int(days)

    for name, hours in places:

        #  Ensure day exists
        if day not in itinerary:
            itinerary[day] = []

        #  Move to next day if limit exceeded
        if total_hours + hours > 16:
            day += 1
            total_hours = 0

            if day > max_days:
                break

            itinerary[day] = []

        itinerary[day].append((name, hours))
        total_hours += hours

    #  IMPORTANT FIX: ensure all days exist
    for d in range(1, max_days + 1):
        if d not in itinerary:
            itinerary[d] = [("Explore Local Area / Rest", 0)]

    return itinerary
conn = sqlite3.connect("itinerary.db")

# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)