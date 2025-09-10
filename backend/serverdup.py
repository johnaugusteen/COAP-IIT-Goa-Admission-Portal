from flask import Flask, request, jsonify, make_response
from hashlib import sha256
import psycopg2
from flask_cors import CORS
import base64

app = Flask(__name__)
# Configure CORS for all routes
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Database connection setup
def get_db_connection():
    conn = psycopg2.connect(
        database="COAP_IITGOA",
        user="postgres",
        password="9133457445",
        host="localhost",
        port="5432"
    )
    print(conn)
    return conn

# Register Route
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user with the same regid already exists
    cursor.execute("SELECT * FROM users WHERE coap_reg_id = %s", (data['regid'],))
    existing_user = cursor.fetchone()

    if existing_user:
        return jsonify({'message': 'User already exists'})

    # Encrypt the password using SHA-256
    encrypted_password = sha256(data['pass'].encode()).hexdigest()

    # Insert the new user
    insert_query = """
        INSERT INTO users (user_name, dob, phone_number, mail, coap_reg_id, password_user, year_admission)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    cursor.execute(insert_query, (data['name'], data['dob'], data['mobile'], data['email'], data['regid'], encrypted_password, data['year']))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'Registration successful'})

# Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user with the provided regid exists
    cursor.execute("SELECT * FROM users WHERE coap_reg_id = %s", (data['regid'],))
    user = cursor.fetchone()

    if user:
        encrypted_password = sha256(data['pass'].encode()).hexdigest()
        if encrypted_password == user[5]:  # Assuming the password is in the 6th column
            return jsonify({'message': 'User Matched'})
        else:
            return jsonify({'message': 'Incorrect password'})
    else:
        return jsonify({'message': 'User not found'})

    cursor.close()
    conn.close()

# Change Password Route
@app.route('/changepassword', methods=['POST'])
def change_password():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user with the provided regid exists
    cursor.execute("SELECT * FROM users WHERE coap_reg_id = %s", (data['regid'],))
    user = cursor.fetchone()

    if user:
        encrypted_password = sha256(data['pass'].encode()).hexdigest()
        cursor.execute("UPDATE users SET password_user = %s WHERE coap_reg_id = %s", (encrypted_password, data['regid']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Password changed successfully'})
    else:
        cursor.close()
        conn.close()
        return jsonify({'message': 'User not found'})

@app.route('/storedetails', methods=['POST'])
def store_details():
    # Check if files are part of the request
    if len(list(request.files)) == 0:
        return jsonify({'message': 'No files found in the request'}), 400

    # Extract the data from request
    data = request.form.to_dict()
    files = request.files

    # Convert files to bytes and prepare to insert into database
    file_data = {
        'tenth_certificate': files['10th_certificate'].read(),
        'intermediate_certificate': files['intermediate_certificate'].read(),
        'degree_certificate': files['degree_certificate'].read(),
        'caste_certificate': files['caste_certificate'].read(),
        'aadhaar_card': files['aadhaar_card'].read()
    }

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user with the same regid already exists
    cursor.execute("SELECT * FROM applicant_detail WHERE regid = %s", (data['regid'],))
    existing_user = cursor.fetchone()

    if existing_user:
        # Calculate shortlist status
        shortlist_status = calculate_shortlist_status(data)
        data['shortlist_status'] = shortlist_status
        
        # Update existing user
        update_applicant_detail(data, file_data)
        return jsonify({'message': 'User details updated'})
    else:
        # Insert new user
        insert_applicant_detail(data, file_data)
        return jsonify({'message': 'User details stored'})

    cursor.close()
    conn.close()

def calculate_shortlist_status(data):
    if (data['degreebranch'].lower() in ['cse', 'ee'] and data['degreequal'].lower() == 'masters'):
        if (data['category'].lower() in ['sc', 'st'] and float(data['degree8cgpa']) >= 5.5) or \
        (data['category'].lower() not in ['sc', 'st'] and float(data['degree8cgpa']) >= 6.0):
            return 'Shortlisted'
        return 'Unshortlisted'
    elif data['degreequal'].lower() == 'btech' and float(data['degree8cgpa']) >= 8.0:
        return 'Shortlisted'
    return 'Unshortlisted'

def update_applicant_detail(data, file_data):
    conn = get_db_connection()
    cursor = conn.cursor()

    update_query = """
        UPDATE applicant_detail SET name = %s, appno = %s, dob = %s, addno = %s, mobile = %s, email = %s, category = %s,
        pwd = %s, ews = %s, gender = %s, rank2021 = %s, rollno2021 = %s, score2021 = %s, discipline2021 = %s,
        rank2022 = %s, rollno2022 = %s, score2022 = %s, discipline2022 = %s, rank2023 = %s, rollno2023 = %s,
        score2023 = %s, discipline2023 = %s, hsscdate = %s, hsscpercentage = %s, sscdate = %s, sscpercentage = %s,
        sscboard = %s, degreepassingdate = %s, degree7percentage = %s, degree7cgpa = %s, degree8percentage = %s,
        degree8cgpa = %s, degreequal = %s, degreeinsti = %s, degreebranch = %s, shortlist_status = %s,
        tenth_certificate = %s, intermediate_certificate = %s, degree_certificate = %s,
        caste_certificate = %s, aadhaar_card = %s WHERE regid = %s
    """
    
    cursor.execute(update_query, (
        data['name'], data['appno'], data['dob'], data['addno'], data['mobile'], data['email'], data['category'],
        data['pwd'], data['ews'], data['gender'], data['rank2021'], data['rollno2021'], data['score2021'], data['discipline2021'],
        data['rank2022'], data['rollno2022'], data['score2022'], data['discipline2022'], data['rank2023'], data['rollno2023'],
        data['score2023'], data['discipline2023'], data['hsscdate'], data['hsscpercentage'], data['sscdate'], data['sscpercentage'],
        data['sscboard'], data['degreepassingdate'], data['degree7percentage'], data['degree7cgpa'], data['degree8percentage'],
        data['degree8cgpa'], data['degreequal'], data['degreeinsti'], data['degreebranch'], data['shortlist_status'],
        file_data['tenth_certificate'], file_data['intermediate_certificate'], file_data['degree_certificate'],
        file_data['caste_certificate'], file_data['aadhaar_card'], data['regid']
    ))

    conn.commit()
    cursor.close()
    conn.close()

def insert_applicant_detail(data, file_data):
    conn = get_db_connection()
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO applicant_detail (name, appno, dob, addno, mobile, email, category, pwd, ews, gender,
                                      rank2021, rollno2021, score2021, discipline2021, rank2022, rollno2022, score2022,
                                      discipline2022, rank2023, rollno2023, score2023, discipline2023, hsscdate, hsscpercentage,
                                      sscdate, sscpercentage, sscboard, degreepassingdate, degree7percentage, degree7cgpa, degree8percentage,
                                      degree8cgpa, degreequal, degreeinsti, degreebranch, regid,
                                      tenth_certificate, intermediate_certificate, degree_certificate,
                                      caste_certificate, aadhaar_card)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(insert_query, (
        data['name'], data['appno'], data['dob'], data['addno'], data['mobile'], data['email'], data['category'],
        data['pwd'], data['ews'], data['gender'], data['rank2021'], data['rollno2021'], data['score2021'], data['discipline2021'],
        data['rank2022'], data['rollno2022'], data['score2022'], data['discipline2022'], data['rank2023'], data['rollno2023'],
        data['score2023'], data['discipline2023'], data['hsscdate'], data['hsscpercentage'], data['sscdate'], data['sscpercentage'],
        data['sscboard'], data['degreepassingdate'], data['degree7percentage'], data['degree7cgpa'], data['degree8percentage'],
        data['degree8cgpa'], data['degreequal'], data['degreeinsti'], data['degreebranch'], data['regid'],
        file_data['tenth_certificate'], file_data['intermediate_certificate'], file_data['degree_certificate'],
        file_data['caste_certificate'], file_data['aadhaar_card']
    ))

    conn.commit()
    cursor.close()
    conn.close()

# Get User Details Route
@app.route('/getuserdetails', methods=['GET'])
def get_user_details():
    regid = request.args.get('regid')
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch user details based on regid
    cursor.execute("SELECT * FROM applicant_detail WHERE regid = %s", (regid,))
    user = cursor.fetchone()

    if user:
        column_headings = [
            'name', 'appno', 'dob', 'addno', 'mobile', 'email', 'category',
            'pwd', 'ews', 'gender', 'rank2021', 'rollno2021', 'score2021',
            'discipline2021', 'rank2022', 'rollno2022', 'score2022', 'discipline2022',
            'rank2023', 'rollno2023', 'score2023', 'discipline2023', 'hsscdate',
            'hsscpercentage', 'sscdate', 'sscpercentage', 'sscboard', 'degreepassingdate',
            'degree7percentage', 'degree7cgpa', 'degree8percentage', 'degree8cgpa',
            'degreequal', 'degreeinsti', 'degreebranch', 'regid'
        ]
        user_details = dict(zip(column_headings, user))
        return jsonify(user_details)
    else:
        return jsonify({'error': 'User not found'})

    cursor.close()
    conn.close()

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def get_admin_dashboard_data():
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Invalid JSON'}), 400
    # Retrieve CPI thresholds from the request
    cpi_iit = float(data.get('cpiIIT', 8.0))
    cpi_scst = float(data.get('cpiSCST', 6.5))
    cpi_other = float(data.get('cpiOther', 7.0))
    print(cpi_iit)
    print(cpi_other)
    print(cpi_scst)
    print("hi")
    
    conn = get_db_connection()
    cur = conn.cursor()

    query = f"""
    SELECT * FROM applicant_detail
    WHERE (
        (LOWER(degreeinsti) LIKE 'iit%' AND LOWER(degreequal) = 'btech' AND CAST(degree8cgpa AS FLOAT) >= {cpi_iit}) OR 
        (LOWER(degreeinsti) NOT LIKE 'iit%' AND LOWER(degreequal) = 'btech' AND (
            (LOWER(category) IN ('sc', 'st') AND CAST(degree8cgpa AS FLOAT) >= {cpi_scst}) OR 
            (LOWER(category) NOT IN ('sc', 'st') AND CAST(degree8cgpa AS FLOAT) >= {cpi_other})
        ))
    );
    """
    print("Query:", query)
    print("Parameters:", (cpi_iit, cpi_scst, cpi_other))

    # Execute the query with the correct parameters
    # cur.execute(query, (cpi_iit, cpi_scst, cpi_other))
    data1 = (cpi_iit, cpi_scst, cpi_other)
    try:
        cur.execute(query)
    except Exception as e:
        print("Execution failed:", e)
        raise

    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]

    data = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        for key in row_dict:
            value = row_dict[key]
            if isinstance(value, memoryview):
                value = value.tobytes()
            if isinstance(value, (bytes, bytearray)):
                row_dict[key] = base64.b64encode(value).decode('utf-8')
            else:
                row_dict[key] = 'None' if value is None else str(value)
        data.append(row_dict)

    cur.close()
    conn.close()

    return jsonify(data)

@app.route('/admin_login', methods=['POST'])
def admin_login():
    data = request.json
    adminid = data.get('adminid')
    adminpass = data.get('adminpass')

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM admin WHERE user_name = %s AND pasword = %s"
    cursor.execute(query, (adminid, adminpass))
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if result:
        return jsonify({'message': 'Admin Matched'}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)