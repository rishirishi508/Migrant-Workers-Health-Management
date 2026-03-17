import os
import secrets
import qrcode
from io import BytesIO
import base64
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
import smtplib
from email.mime.text import MIMEText
import random
import string
from utils.pdf_generator import generate_health_card_pdf
from transformers import pipeline

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize Local AI Model
print("Loading local AI model (this may take a minute on startup)...")
try:
    # Using TinyLlama as a small local model that supports system prompts well
    # We load it onto CPU since we don't know if a GPU is available
    chatbot_pipeline = pipeline(
        "text-generation", 
        model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        device_map="cpu"
    )
    print("Local AI model loaded successfully.")
except Exception as e:
    print(f"Error loading AI model: {e}")
    chatbot_pipeline = None

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'mysql_db'),
    'database': os.environ.get('DB_NAME', 'health_records'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'rootpass'),
    'charset': 'utf8mb4'
}

def get_db_connection():
    """Get database connection"""
    return mysql.connector.connect(**DB_CONFIG)

def generate_worker_id():
    """Generate unique Worker ID"""
    return f"MW{random.randint(100000, 999999)}"

def generate_otp():
    """Generate 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp(phone_number, otp):
    """Send OTP to phone number (mock implementation)"""
    print(f"Sending OTP {otp} to {phone_number}")
    return True

def generate_qr_code(data):
    """Generate QR code for worker ID"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()

@app.route('/')
def index():
    return render_template('index.html')

# Worker Routes
@app.route('/worker/register', methods=['GET', 'POST'])
def worker_register():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        occupation = request.form.get('occupation')
        contact = request.form.get('contact')
        relation_name = request.form.get('relation_name')
        relation_phone = request.form.get('relation_phone')
        relation_type = request.form.get('relation_type')
        height = request.form.get('height')
        weight = request.form.get('weight')
        blood_group = request.form.get('blood_group')
        password = request.form.get('password')
        
        # Generate worker ID
        worker_id = generate_worker_id()
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        conn = None

        
        cursor = None

        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insert worker data
            query = """
            INSERT INTO Workers (worker_id, name, age, gender, occupation, contact, 
                               relation_name, relation_phone, relation_type, height, 
                               weight, blood_group, password_hash, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (worker_id, name, age, gender, occupation, contact,
                     relation_name, relation_phone, relation_type, height,
                     weight, blood_group, password_hash, datetime.now())
            
            cursor.execute(query, values)
            conn.commit()
            
            # Generate QR code
            qr_data = generate_qr_code(worker_id)
            
            flash(f'Registration successful! Your Worker ID is: {worker_id}', 'success')
            return redirect(url_for('worker_login'))  # redirect to login page
            # return render_template('worker-dashboard.html', 
            #                      worker_id=worker_id, 
            #                      worker_name=name,
            #                      qr_code=qr_data)
            
        except Error as e:
            flash(f'Registration failed: {e}', 'error')
        finally:
            if conn and conn.is_connected():
                if cursor:
                    cursor.close()
                conn.close()
    
    return render_template('worker-register.html')

@app.route('/worker/login', methods=['GET', 'POST'])
def worker_login():
    if request.method == 'POST':
        worker_id = request.form.get('worker_id')
        password = request.form.get('password')

        conn = None


        cursor = None


        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM Workers WHERE worker_id = %s"
            cursor.execute(query, (worker_id,))
            worker = cursor.fetchone()

            if worker and check_password_hash(worker['password_hash'], password):
                session['worker_id'] = worker_id
                session['user_type'] = 'worker'
                print("Login successful for:", worker_id)
                return redirect(url_for('worker_dashboard'))
            else:
                flash('Invalid Worker ID or password', 'error')
                print("Login failed for:", worker_id)

        except Error as e:
            flash(f'Login failed: {e}', 'error')
            print("Login error:", e)

        finally:
            if conn and conn.is_connected():
                if cursor:
                    cursor.close()
                conn.close()

    # If GET request or failed login, render the login page
    return render_template('worker-login-portal.html')


@app.route('/worker/dashboard')
def worker_dashboard():
    # Check if logged in and user type is worker
    if 'worker_id' not in session or session.get('user_type') != 'worker':
        return redirect(url_for('worker-login'))

    worker_id = session['worker_id']

    conn = None


    cursor = None


    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get worker details
        query = "SELECT * FROM Workers WHERE worker_id = %s"
        cursor.execute(query, (worker_id,))
        worker = cursor.fetchone()

        # Get last medical record (if any)
        query = """
        SELECT * FROM WorkerRecords
        WHERE worker_id = %s
        ORDER BY created_at DESC
        LIMIT 1
        """
        cursor.execute(query, (worker_id,))
        last_record = cursor.fetchone()

        # Generate QR code
        qr_data = generate_qr_code(worker_id)

        return render_template('worker-dashboard.html',
                               worker=worker,
                               last_record=last_record,
                               qr_code=qr_data)

    except Error as e:
        flash(f'Error loading dashboard: {e}', 'error')
        return redirect(url_for('worker-login'))

    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()
@app.route('/worker/download-card')
def download_health_card():
    if 'worker_id' not in session or session.get('user_type') != 'worker':
        return redirect(url_for('worker_login'))
    
    worker_id = session['worker_id']
    
    conn = None

    
    cursor = None

    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM Workers WHERE worker_id = %s"
        cursor.execute(query, (worker_id,))
        worker = cursor.fetchone()
        
        if worker:
            qr_code = generate_qr_code(worker_id)
            pdf_buffer = generate_health_card_pdf(worker, qr_code)
            
            return send_file(
                pdf_buffer,
                as_attachment=True,
                download_name=f'health_card_{worker_id}.pdf',
                mimetype='application/pdf'
            )
        
    except Error as e:
        flash(f'Error generating health card: {e}', 'error')
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()
    
    return redirect(url_for('worker_dashboard'))

# Doctor Routes
@app.route('/doctor/register', methods=['GET', 'POST'])
def doctor_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        license_number = request.form.get('license_number')
        specialization = request.form.get('specialization')
        contact = request.form.get('contact')
        password = request.form.get('password')
        
        password_hash = generate_password_hash(password)
        
        conn = None

        
        cursor = None

        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
            INSERT INTO Doctors (name, email, license_number, specialization, 
                               contact, password_hash, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (name, email, license_number, specialization, 
                     contact, password_hash, datetime.now())
            
            cursor.execute(query, values)
            conn.commit()
            
            flash('Doctor registration successful!', 'success')
            return redirect(url_for('doctor_login'))
            
        except Error as e:
            flash(f'Registration failed: {e}', 'error')
        finally:
            if conn and conn.is_connected():
                if cursor:
                    cursor.close()
                conn.close()
    
    return render_template('doctor-register.html')

@app.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = None

        
        cursor = None

        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM Doctors WHERE email = %s"
            cursor.execute(query, (email,))
            doctor = cursor.fetchone()
            
            if doctor and check_password_hash(doctor['password_hash'], password):
                session['doctor_id'] = doctor['doctor_id']
                session['user_type'] = 'doctor'
                return redirect(url_for('doctor_dashboard'))
            else:
                flash('Invalid email or password', 'error')
                
        except Error as e:
            flash(f'Login failed: {e}', 'error')
        finally:
            if conn and conn.is_connected():
                if cursor:
                    cursor.close()
                conn.close()
    
    return render_template('doctor-login-portal.html')

@app.route('/doctor/dashboard')
def doctor_dashboard():
    if 'doctor_id' not in session or session.get('user_type') != 'doctor':
        return redirect(url_for('doctor_login'))
    
    doctor_id = session['doctor_id']
    
    conn = None

    
    cursor = None

    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get doctor details
        query = "SELECT * FROM Doctors WHERE doctor_id = %s"
        cursor.execute(query, (doctor_id,))
        doctor = cursor.fetchone()
        
        # Get recent access logs
        query = """
        SELECT al.*, w.name as worker_name 
        FROM AccessLogs al
        JOIN Workers w ON al.worker_id = w.worker_id
        WHERE al.doctor_id = %s
        ORDER BY al.access_time DESC
        LIMIT 10
        """
        cursor.execute(query, (doctor_id,))
        recent_access = cursor.fetchall()
        
        return render_template('doctor-dashboard.html', 
                             doctor=doctor, 
                             recent_access=recent_access)
        
    except Error as e:
        flash(f'Error loading dashboard: {e}', 'error')
        return redirect(url_for('doctor_login'))
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

@app.route('/doctor/search', methods=['POST'])
def doctor_search():
    if 'doctor_id' not in session or session.get('user_type') != 'doctor':
        return jsonify({'error': 'Unauthorized'}), 401
    
    worker_id = request.json.get('worker_id')
    
    conn = None

    
    cursor = None

    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT worker_id, name, age, gender, contact, created_at
        FROM Workers 
        WHERE worker_id = %s
        """
        cursor.execute(query, (worker_id,))
        worker = cursor.fetchone()
        
        if worker:
            return jsonify(worker)
        else:
            return jsonify({'error': 'Worker not found'}), 404
            
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

@app.route('/doctor/request-access', methods=['POST'])
def request_access():
    if 'doctor_id' not in session or session.get('user_type') != 'doctor':
        return jsonify({'error': 'Unauthorized'}), 401
    
    worker_id = request.json.get('worker_id')
    doctor_id = session['doctor_id']
    
    conn = None

    
    cursor = None

    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get worker and relation details
        query = "SELECT * FROM Workers WHERE worker_id = %s"
        cursor.execute(query, (worker_id,))
        worker = cursor.fetchone()
        
        if worker:
            # Generate OTP
            otp = generate_otp()
            expires_at = datetime.now() + timedelta(minutes=10)
            
            # Store OTP
            query = """
            INSERT INTO OTPVerifications (worker_id, doctor_id, otp, expires_at)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (worker_id, doctor_id, otp, expires_at))
            conn.commit()
            
            # Send OTP to worker and relation
            send_otp(worker['contact'], otp)
            send_otp(worker['relation_phone'], otp)
            
            return jsonify({'message': 'OTP sent successfully'})
        else:
            return jsonify({'error': 'Worker not found'}), 404
            
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

@app.route('/doctor/verify-otp', methods=['POST'])
def verify_otp():
    if 'doctor_id' not in session or session.get('user_type') != 'doctor':
        return jsonify({'error': 'Unauthorized'}), 401
    
    worker_id = request.json.get('worker_id')
    otp = request.json.get('otp')
    doctor_id = session['doctor_id']
    
    conn = None

    
    cursor = None

    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verify OTP
        query = """
        SELECT * FROM OTPVerifications 
        WHERE worker_id = %s AND doctor_id = %s AND otp = %s 
        AND expires_at > %s AND used = FALSE
        """
        cursor.execute(query, (worker_id, doctor_id, otp, datetime.now()))
        otp_record = cursor.fetchone()
        
        if otp_record:
            # Mark OTP as used
            query = "UPDATE OTPVerifications SET used = TRUE WHERE otp_id = %s"
            cursor.execute(query, (otp_record['otp_id'],))
            
            # Log access
            query = """
            INSERT INTO AccessLogs (doctor_id, worker_id, access_type, reason)
            VALUES (%s, %s, 'OTP_VERIFIED', 'Normal access with consent')
            """
            cursor.execute(query, (doctor_id, worker_id))
            
            # Get full worker details
            query = "SELECT * FROM Workers WHERE worker_id = %s"
            cursor.execute(query, (worker_id,))
            worker = cursor.fetchone()
            
            # Get medical records
            query = "SELECT * FROM WorkerRecords WHERE worker_id = %s ORDER BY created_at DESC"
            cursor.execute(query, (worker_id,))
            records = cursor.fetchall()
            
            conn.commit()
            
            return jsonify({
                'worker': worker,
                'records': records,
                'message': 'Access granted'
            })
        else:
            return jsonify({'error': 'Invalid or expired OTP'}), 400
            
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

@app.route('/doctor/break-glass', methods=['POST'])
def break_glass_access():
    if 'doctor_id' not in session or session.get('user_type') != 'doctor':
        return jsonify({'error': 'Unauthorized'}), 401
    
    worker_id = request.json.get('worker_id')
    reason = request.json.get('reason')
    doctor_id = session['doctor_id']
    
    conn = None

    
    cursor = None

    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Log break glass access
        query = """
        INSERT INTO AccessLogs (doctor_id, worker_id, access_type, reason)
        VALUES (%s, %s, 'BREAK_GLASS', %s)
        """
        cursor.execute(query, (doctor_id, worker_id, reason))
        
        # Get worker details for notifications
        query = "SELECT * FROM Workers WHERE worker_id = %s"
        cursor.execute(query, (worker_id,))
        worker = cursor.fetchone()
        
        if worker:
            # Send notifications (mock implementation)
            print(f"ALERT: Break glass access by Doctor {doctor_id} for Worker {worker_id}")
            print(f"Reason: {reason}")
            
            # Get medical records
            query = "SELECT * FROM WorkerRecords WHERE worker_id = %s ORDER BY created_at DESC"
            cursor.execute(query, (worker_id,))
            records = cursor.fetchall()
            
            conn.commit()
            
            return jsonify({
                'worker': worker,
                'records': records,
                'message': 'Emergency access granted'
            })
        else:
            return jsonify({'error': 'Worker not found'}), 404
            
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

# Admin Routes
@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        role = request.form.get('role')
        department = request.form.get('department')
        password = request.form.get('password')
        
        password_hash = generate_password_hash(password)
        
        conn = None

        
        cursor = None

        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
            INSERT INTO Admins (name, email, role, department, password_hash, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            values = (name, email, role, department, password_hash, datetime.now())
            cursor.execute(query, values)
            conn.commit()
            
            flash('Admin registration successful!', 'success')
            return redirect(url_for('admin_login'))
            
        except Error as e:
            flash(f'Registration failed: {e}', 'error')
        finally:
            if conn and conn.is_connected():
                if cursor:
                    cursor.close()
                conn.close()
    
    return render_template('admin-register.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = None

        
        cursor = None

        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM Admins WHERE email = %s"
            cursor.execute(query, (email,))
            admin = cursor.fetchone()
            
            if admin and check_password_hash(admin['password_hash'], password):
                session['admin_id'] = admin['admin_id']
                session['user_type'] = 'admin'
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid email or password', 'error')
                
        except Error as e:
            flash(f'Login failed: {e}', 'error')
        finally:
            if conn and conn.is_connected():
                if cursor:
                    cursor.close()
                conn.close()
    
    return render_template('admin-login-portal.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('admin_login'))
    
    conn = None

    
    cursor = None

    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) as total_workers FROM Workers")
        total_workers = cursor.fetchone()['total_workers']
        
        cursor.execute("SELECT COUNT(DISTINCT worker_id) as treated_workers FROM WorkerRecords")
        treated_workers = cursor.fetchone()['treated_workers']
        
        cursor.execute("SELECT COUNT(*) as total_doctors FROM Doctors")
        total_doctors = cursor.fetchone()['total_doctors']
        
        # Get break glass events
        query = """
        SELECT al.*, d.name as doctor_name, w.name as worker_name
        FROM AccessLogs al
        JOIN Doctors d ON al.doctor_id = d.doctor_id
        JOIN Workers w ON al.worker_id = w.worker_id
        WHERE al.access_type = 'BREAK_GLASS'
        ORDER BY al.access_time DESC
        LIMIT 20
        """
        cursor.execute(query)
        break_glass_events = cursor.fetchall()
        
        stats = {
            'total_workers': total_workers,
            'treated_workers': treated_workers,
            'total_doctors': total_doctors
        }
        
        return render_template('admin-dashboard.html', 
                             stats=stats,
                             break_glass_events=break_glass_events)
        
    except Error as e:
        flash(f'Error loading dashboard: {e}', 'error')
        return redirect(url_for('admin_login'))
    finally:
        if conn and conn.is_connected():
            if cursor:
                cursor.close()
            conn.close()

# AI Chatbot Route
@app.route('/api/chat', methods=['POST'])
def ai_chat():
    global chatbot_pipeline
    if chatbot_pipeline is None:
        return jsonify({'error': 'AI Chat is currently unavailable (model failed to load locally).'}), 503

    data = request.json
    if not data or not data.get('message'):
        return jsonify({'error': 'Message is required'}), 400

    user_message = data.get('message')

    try:
        # Nexus Care specific knowledge base for the AI Assistant
        nexus_care_context = """
        You are Nexus Care AI, an empathetic and professional Health Assistant for Nexus Care.
        Nexus Care is a digital health records management system designed specifically for migrant workers and healthcare providers.
        
        Key Information about Nexus Care:
        - Worker Portal: Allows migrant workers to register, access their health records, and download a digital health card with a QR code.
        - Doctor Portal: Allows authorized doctors to access patient records with OTP consent verification, manage treatments, and use emergency "Break Glass" override access.
        - Admin Portal: Allows system administrators to monitor statistics, audit access logs, and manage emergency access events.
        - Security Features: OTP verification for routine access, complete audit trails for all data access, and secure PDF health cards.
        
        Guidelines for your responses:
        1. Keep responses concise, clear, and easy to understand.
        2. Provide answers in a supportive and professional tone.
        3. Only use the information provided above to answer questions about Nexus Care.
        4. If a user asks a general health question, provide general advice but advise them to consult a doctor through the Nexus Care platform for specific medical advice.
        5. You are an AI and cannot diagnose illnesses or prescribe medication.
        """
        
        messages = [
            {
                "role": "system",
                "content": nexus_care_context.strip(),
            },
            {"role": "user", "content": user_message},
        ]
        
        prompt = chatbot_pipeline.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        outputs = chatbot_pipeline(prompt, max_new_tokens=250, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
        
        # Extract only the generated response
        reply_text = outputs[0]["generated_text"][len(prompt):].strip()
        
        return jsonify({'reply': reply_text})
    except Exception as e:
        print(f"Chatbot error: {e}")
        return jsonify({'error': 'Failed to generate a response. Please try again later.'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)