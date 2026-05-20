import pymysql

try:
    # Try connecting to XAMPP MySQL
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='denguetrackingsystem'
    )
    print("✅ Successfully connected to XAMPP MySQL!")
    connection.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")