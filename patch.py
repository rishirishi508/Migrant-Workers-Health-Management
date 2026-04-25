import re

with open('app.py', 'r') as f:
    code = f.read()

# Make get_db_connection raise Error instead of returning None
code = code.replace('''def get_db_connection():
    \"\"\"Get database connection\"\"\"
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None''', '''def get_db_connection():
    \"\"\"Get database connection\"\"\"
    return mysql.connector.connect(**DB_CONFIG)''')

# Before 'try:', insert 'conn = None\n        cursor = None' 
# But only for blocks that do 'conn = get_db_connection()'
pattern = r'(\s*)try:\n(\s*)conn = get_db_connection\(\)'
replacement = r'\1conn = None\n\1cursor = None\n\1try:\n\2conn = get_db_connection()'
code = re.sub(pattern, replacement, code)

# Fix finally blocks
finally_pattern = r'(\s*)finally:\n(\s*)if conn\.is_connected\(\):\n(\s*)cursor\.close\(\)\n(\s*)conn\.close\(\)'
finally_repl = r'\1finally:\n\2if conn and conn.is_connected():\n\3if cursor:\n\3    cursor.close()\n\4conn.close()'

code = re.sub(finally_pattern, finally_repl, code)

with open('app.py', 'w') as f:
    f.write(code)

print('Patched app.py successfully!')
