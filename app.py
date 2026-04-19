from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import secrets
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = '8f4e2d1a9b7c3e5f6a8d9b2c4e1f7a3b5c8d9e2f1a4b7c9d3e5f8a2b1c4d6e8f'

# =========================
# SIMPLE USER STORAGE (In-memory for demo)
# =========================
# You can change these credentials to anything you want
VALID_USERS = {
    'admin': {
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'admin123'
    },
    'user': {
        'username': 'user',
        'email': 'user@example.com',
        'password': 'user123'
    }
}

# =========================
# LOGIN PAGE
# =========================
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/api/login", methods=['POST'])
def login_api():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not username or not email or not password:
            return jsonify({'success': False, 'message': 'All fields are required!'}), 400
        
        # Check if user exists with matching credentials
        user_found = None
        for user_id, user_data in VALID_USERS.items():
            if user_data['username'] == username and user_data['email'] == email and user_data['password'] == password:
                user_found = user_data
                break
        
        if user_found:
            session['user_id'] = username
            session['username'] = user_found['username']
            session['email'] = user_found['email']
            return jsonify({'success': True, 'message': 'Login successful! Redirecting...'}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid username, email, or password!'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': 'Login failed! Try again.'}), 500

# =========================
# FORGOT PASSWORD (Simple reset without database)
# =========================
@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot-password.html")

@app.route("/api/forgot-password", methods=['POST'])
def forgot_password_api():
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required!'}), 400
        
        # Check if email exists in our valid users
        user_found = None
        for user_id, user_data in VALID_USERS.items():
            if user_data['email'] == email:
                user_found = user_data
                break
        
        if not user_found:
            return jsonify({'success': False, 'message': 'Email not found! Please check your email.'}), 404
        
        # Generate a simple reset token
        token = secrets.token_hex(16)
        
        # Store token in session (simple method)
        session['reset_token'] = token
        session['reset_email'] = email
        session['reset_expires'] = (datetime.now() + timedelta(hours=1)).timestamp()
        
        # In a real app, you'd send this token via email
        # For demo, we'll show it in the response
        return jsonify({'success': True, 'message': f'Reset token: {token}', 'token': token}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to process request!'}), 500

@app.route("/api/reset-password", methods=['POST'])
def reset_password_api():
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        token = data.get('token', '').strip()
        new_password = data.get('new_password', '')
        
        if not email or not token or not new_password:
            return jsonify({'success': False, 'message': 'All fields are required!'}), 400
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters!'}), 400
        
        # Verify token from session
        if (session.get('reset_token') == token and 
            session.get('reset_email') == email and
            session.get('reset_expires', 0) > datetime.now().timestamp()):
            
            # Update password in our in-memory storage
            for user_id, user_data in VALID_USERS.items():
                if user_data['email'] == email:
                    VALID_USERS[user_id]['password'] = new_password
                    break
            
            # Clear reset session
            session.pop('reset_token', None)
            session.pop('reset_email', None)
            session.pop('reset_expires', None)
            
            return jsonify({'success': True, 'message': 'Password reset successful! Please login with new password.'}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid or expired token!'}), 400
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to reset password!'}), 500

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# =========================
# INDEX PAGE
# =========================
@app.route("/")
def index():
    return render_template("index.html")

# =========================
# PLANNER PAGE (Protected)
# =========================
@app.route("/planner")
def planner():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cities = [
        'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 
        'Ahmedabad', 'Jaipur', 'Lucknow', 'Nagpur', 'Indore', 'Bhopal', 'Visakhapatnam',
        'Patna', 'Vadodara', 'Guwahati', 'Chandigarh', 'Coimbatore', 'Mysore', 
        'Nashik', 'Ranchi', 'Bhubaneswar', 'Rajkot', 'Kochi', 'Jodhpur', 'Madurai',
        'Agra', 'Varanasi', 'Srinagar', 'Amritsar', 'Allahabad', 'Gwalior', 'Vijayawada',
        'Jalandhar', 'Thiruvananthapuram', 'Raipur', 'Dehradun', 'Shimla',
        'Gangtok', 'Udaipur', 'Pondicherry', 'Ooty', 'Manali', 'Goa', 'Darjeeling', 'Rishikesh'
    ]
    return render_template("planner.html", cities=cities, username=session.get('username'))

# =========================
# RESULT PAGE
# =========================
@app.route("/result", methods=['POST'])
def result():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    city = request.form.get('city')
    days = request.form.get('days')
    
    plan = generate_itinerary(city, days)
    
    weather = {
        'temperature': 28,
        'feels_like': 26,
        'condition': 'Sunny',
        'humidity': 65,
        'wind_speed': 12,
        'pressure': 1012,
        'icon': '01d',
        'rain_possibility': 'Low'
    }
    
    return render_template("result.html", city=city, days=days, plan=plan, weather=weather)

def generate_itinerary(city_name, days):
    itinerary = {}
    sample_places = [
        ("City Center & Heritage Walk", 4),
        ("Famous Temple/Mosque", 3),
        ("Local Market Exploration", 3),
        ("Museum & Art Gallery", 3),
        ("Park & Garden Visit", 2),
        ("Sunset Point", 2),
        ("Cultural Show", 3),
        ("Street Food Tour", 2),
    ]
    
    for day in range(1, int(days) + 1):
        start_index = (day - 1) * 3
        end_index = start_index + 3
        itinerary[day] = sample_places[start_index:end_index] if end_index <= len(sample_places) else sample_places[:3]
    
    return itinerary

if __name__ == "__main__":
    app.run(debug=True)