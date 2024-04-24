from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3

app = Flask(__name__, template_folder='template')
app.secret_key = 'asdmwejfwjgkmvergkmeotekmgtojhm'

# Database Initialization
def initialize_database():
    conn = sqlite3.connect('gold_loan.db')
    c = conn.cursor()

    # Create Authentication Table
    c.execute('''CREATE TABLE IF NOT EXISTS authentication
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')

    # Commit changes and close connection
    conn.commit()
    conn.close()

# Initialize Database on Startup
initialize_database()

# Routes
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('signup.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Check if username already exists
        conn = sqlite3.connect('gold_loan.db')
        c = conn.cursor()
        c.execute("SELECT * FROM authentication WHERE username=?", (username,))
        existing_user = c.fetchone()

        if existing_user:
            return "Username already exists!"
        else:
            c.execute("INSERT INTO authentication (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            conn.close()
            session['username'] = username
            session['role'] = role
            return redirect(url_for('dashboard'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('gold_loan.db')
        c = conn.cursor()
        c.execute("SELECT * FROM authentication WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            # Set session variables
            session['username'] = username
            session['role'] = user[2]
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('signup'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        role = session['role']

        if role == 'admin':
            return render_template('admin_dashboard.html', username=username)
        elif role == 'manager':
            return render_template('manager_dashboard.html', username=username)
        elif role == 'customer':
            return render_template('customer_dashboard.html', username=username)
    else:
        return redirect(url_for('login'))
    
@app.route('/create_table', methods=['GET', 'POST'])
def create_table():
    try:
        if request.method == 'POST':
            table_name = request.form['table_name']
            column_names = request.form.getlist('column_names')
            data_types = request.form.getlist('data_types')
            print("Column Names:", column_names)  # Print column names for debugging
            print("Data Types:", data_types)      # Print data types for debugging


            # Create table in the database
            conn = sqlite3.connect('gold_loan.db')
            c = conn.cursor()
            
            # Construct SQL query to create table
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ("
            column_definitions = [f'"{column_names[i]}" {data_types[i]}' for i in range(len(column_names))]
            create_table_query += ", ".join(column_definitions)
            create_table_query += ")"


            print("Create Table Query:", create_table_query)  # Print the SQL query for debugging

            c.execute(create_table_query)
            conn.commit()
            conn.close()

            # Fetch updated list of table names
            conn = sqlite3.connect('gold_loan.db')
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table';")
            table_names = [row[0] for row in c.fetchall()]
            conn.close()

            return render_template('create_table.html', table_names=table_names)

        # Fetch existing table names for rendering in the create table page
        conn = sqlite3.connect('gold_loan.db')
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = [row[0] for row in c.fetchall()]
        conn.close()

        return render_template('create_table.html', table_names=table_names)
    except Exception as e:
        print("An error occurred:", e)  # Print the error message for debugging
        return "An error occurred: " + str(e), 500  # Return error message with 500 status code




# Define a route to fetch table data
@app.route('/get_table_data/<table_name>')
def get_table_data(table_name):
    try:
        conn = sqlite3.connect('gold_loan.db')
        c = conn.cursor()
        c.execute(f"SELECT * FROM {table_name};")
        table_data = c.fetchall()
        conn.close()
        return render_template('table_content.html', table_name=table_name, table_data=table_data)
    except Exception as e:
        traceback.print_exc()  # Print traceback for debugging
        return "An error occurred: " + str(e), 500  # Return error message with 500 status code





@app.route('/add_table', methods=['POST'])
def add_table():
    return redirect(url_for('create_table'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
