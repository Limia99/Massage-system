from flask import Flask, request, render_template, redirect, url_for, session, flash
from datetime import datetime
import joblib
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

# Ensure model files exist
model_path = 'svm_model.pkl'
vectorizer_path = 'tfidf_vectorizer.pkl'
label_encoder_path = 'label_encoder.pkl'

if os.path.exists(model_path) and os.path.exists(vectorizer_path) and os.path.exists(label_encoder_path):
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    label_encoder = joblib.load(label_encoder_path)
else:
    raise FileNotFoundError("Model, vectorizer, or label encoder files are missing.")

# Database helpers
def execute_query(query, args=(), fetch=False):
    conn = sqlite3.connect('emergency_messages.db')
    cursor = conn.cursor()
    cursor.execute(query, args)
    data = cursor.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

# Add message to database
def add_message_to_db(message, category):
    execute_query(
        'INSERT INTO messages (message, category) VALUES (?, ?)',
        (message, category)
    )

# Find user by email
def find_user_by_email(email):
    result = execute_query('SELECT * FROM users WHERE email = ?', (email,), fetch=True)
    return result[0] if result else None

# Register a new user
def register_user(name, email, password, dob, role):
    hashed_password = generate_password_hash(password)
    execute_query(
        'INSERT INTO users (name, email, password, dob, role) VALUES (?, ?, ?, ?, ?)',
        (name, email, hashed_password, dob, role)
    )

@app.route('/')
def index():
    title = "الصفحة الرئيسية"
    return render_template('index.html', title=title)

@app.route('/register', methods=['GET', 'POST'])
def register():
    title = "إنشاء حساب جديد"
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        dob = request.form['dob']
        role = request.form['role']
        
        if find_user_by_email(email):
            flash('البريد الالكتروني مسجل ، الرجاء تسجيل الدخول', 'warning')
            return redirect(url_for('login'))
        
        # Age verification
        birth_date = datetime.strptime(dob, '%Y-%m-%d')
        age = (datetime.today() - birth_date).days // 365
        if age < 18:
            flash('يجب ان يكون عمرك 18 عاما على الاقل للتسجيل', 'danger')
            return redirect(url_for('register'))

        register_user(name, email, password, dob, role)
        # Automatically log in user after registration
        session['user_id'] = find_user_by_email(email)[0]
        session['user_name'] = name
        session['user_role'] = role
        flash('التسجيل ناجح ، مرحبا بك', 'success')
        return redirect(url_for('message'))

    return render_template('register.html', title=title)

@app.route('/login', methods=['GET', 'POST'])
def login():
    title = "تسجيل الدخول"
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = find_user_by_email(email)
        if user and check_password_hash(user[3], password):  # Compare hashed passwords
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_role'] = user[5]
            flash('تسجيل الدخول ناجح ، مرحبا بك', 'success')
            return redirect(url_for('message'))
        flash('خطأ في البريد الالكتروني او كلمة المرور ، الرجاء اعادة المحاولة', 'danger')
    return render_template('login.html', title=title)

@app.route('/message', methods=['GET', 'POST'])
def message():
    title = "إضافة رسالة طوارئ"
    if 'user_id' not in session:
        flash('الرجاء تسجيل الدخول للمواصلة', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        message = request.form['message']
        message_vector = vectorizer.transform([message])
        prediction = model.predict(message_vector)
        predicted_category = label_encoder.inverse_transform(prediction)[0]
        add_message_to_db(message, predicted_category)
        flash('تم اضافة الرسالة بنجاح', 'success')
        return redirect(url_for('result', message=message, category=predicted_category, is_admin=session.get('user_role') == 'admin'))

    return render_template('message.html', user_name=session.get('user_name'), title=title)

@app.route('/result')
def result():
    title = "النتيجة"
    message = request.args.get('message', '')
    category = request.args.get('category', '')
    return render_template('result.html', message=message, category=category, is_admin=session.get('user_role') == 'admin', title=title)

@app.route('/messages')
def messages():
    title = "عرض الرسائل"
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('الدخول لهذه الصفحة مقيد للمسؤولين فقط ، الرجاء تسجيل الدخول مجددا', 'danger')
        return redirect(url_for('login'))

    messages_list = execute_query('SELECT * FROM messages ORDER BY created_at DESC', fetch=True)
    return render_template('messages.html', messages=messages_list, title=title)

@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح ، وداعا', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
