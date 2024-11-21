from flask import Flask, render_template, request, redirect, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Replace with your MySQL username
app.config['MYSQL_PASSWORD'] = ''  # Replace with your MySQL password
app.config['MYSQL_DB'] = 'blood_donation'

mysql = MySQL(app)

# Home Route
@app.route('/')
def home():
    return render_template('home.html')

# Donate Blood Route
@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        blood_group = request.form['blood_group']
        contact = request.form['contact']
        
        # Insert data into the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO donors (name, age, blood_group, contact) VALUES (%s, %s, %s, %s)",
                    (name, age, blood_group, contact))
        mysql.connection.commit()
        cur.close()
        
        flash("Thank you for donating blood!", "success")
        return redirect('/donate')
    
    return render_template('donate.html')
# Request Blood Route
@app.route('/request', methods=['GET', 'POST'])
def request_blood():
    if request.method == 'POST':
        name = request.form['name']
        blood_group = request.form['blood_group']
        location = request.form['location']
        contact = request.form['contact']
        
        # Check if donor with the requested blood group exists
        cur = mysql.connection.cursor()
        cur.execute("SELECT name, contact FROM donors WHERE blood_group = %s", (blood_group,))
        donors = cur.fetchall()
        
        if donors:
            # Donor(s) found, show their details
            cur.close()
            return render_template('donors_found.html', blood_group=blood_group, donors=donors)
        else:
            # No donor found, insert the request into the `requests` table
            cur.execute("INSERT INTO requests (name, blood_group, location, contact) VALUES (%s, %s, %s, %s)", 
                        (name, blood_group, location, contact))
            mysql.connection.commit()
            cur.close()
            return render_template('request_submitted.html')
    
    return render_template('request.html')

# Admin Dashboard Route
@app.route('/admin')
def admin_dashboard():
    cur = mysql.connection.cursor()

    # Fetch donors
    cur.execute("SELECT * FROM donors")
    donors = cur.fetchall()

    # Fetch blood requests
    cur.execute("SELECT * FROM requests")
    requests = cur.fetchall()

    cur.close()

    return render_template('admin_dashboard.html', donors=donors, requests=requests)

# Delete Donor
@app.route('/delete_donor/<int:donor_id>', methods=['POST'])
def delete_donor(donor_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM donors WHERE id = %s", (donor_id,))
    mysql.connection.commit()
    cur.close()
    flash("Donor deleted successfully.", "success")
    return redirect('/admin')

@app.route('/update_donor/<int:donor_id>', methods=['GET', 'POST'])
def update_donor(donor_id):
    cur = mysql.connection.cursor()
    
    # Fetch the current donor data
    cur.execute("SELECT * FROM donors WHERE id = %s", (donor_id,))
    donor = cur.fetchone()
    
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        blood_group = request.form['blood_group']
        contact = request.form['contact']
        
        # Update donor data
        cur.execute(
            "UPDATE donors SET name = %s, age = %s, blood_group = %s, contact = %s WHERE id = %s",
            (name, age, blood_group, contact, donor_id)
        )
        mysql.connection.commit()
        cur.close()
        flash("Donor updated successfully!", "success")
        return redirect('/admin_dashboard')
    
    cur.close()
    return render_template('update_donor.html', donor=donor)

# Delete Request
@app.route('/delete_request/<int:request_id>', methods=['POST'])
def delete_request(request_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM requests WHERE id = %s", (request_id,))
    mysql.connection.commit()
    cur.close()
    flash("Request deleted successfully.", "success")
    return redirect('/admin')

@app.route('/update_request/<int:request_id>', methods=['GET', 'POST'])
def update_request(request_id):
    cur = mysql.connection.cursor()
    
    # Fetch the current request data
    cur.execute("SELECT * FROM requests WHERE id = %s", (request_id,))
    request_data = cur.fetchone()
    
    if request.method == 'POST':
        name = request.form['name']
        blood_group = request.form['blood_group']
        location = request.form['location']
        contact = request.form['contact']
        
        # Update request data
        cur.execute(
            "UPDATE requests SET name = %s, blood_group = %s, location = %s, contact = %s WHERE id = %s",
            (name, blood_group, location, contact, request_id)
        )
        mysql.connection.commit()
        cur.close()
        flash("Request updated successfully!", "success")
        return redirect('/admin_dashboard')
    
    cur.close()
    return render_template('update_request.html', request_data=request_data)


# Run the application
if __name__ == '__main__':
    app.run(debug=True)
