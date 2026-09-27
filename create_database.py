import sqlite3

# إنشاء اتصال بقاعدة البيانات (إذا لم تكن موجودة، سيتم إنشاؤها)
conn = sqlite3.connect('emergency_messages.db')

# إنشاء جدول لتخزين الرسائل
conn.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    category TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# لإنشاء جدول المستخدمين، يمكنك أيضاً إضافة جدول للمستخدمين إذا احتجت لذلك:
conn.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    dob DATE NOT NULL,
    role TEXT NOT NULL
);
''')

# حفظ التغييرات وإغلاق الاتصال
conn.commit()
conn.close()

print("Database and tables created successfully.")