
from flask import Flask, request, jsonify, make_response
from hashlib import sha256
import psycopg2
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Database connection setup
def get_db_connection():
    conn = psycopg2.connect(
        database="COAP_IITGOA",
        user="postgres",
        password="9133457445",
        host="localhost",
        port="5432"
    )
    return conn



# Register Route
@app.route('/register', methods=['POST','OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        # Preflight request
        response = jsonify({'message': 'CORS preflight'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200

    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user with the same regid already exists
    cursor.execute("SELECT * FROM users WHERE coap_reg_id = %s", (data['regid'],))
    existing_user = cursor.fetchone()

    if existing_user:
        response = make_response(jsonify({'message': 'User already exists'}))
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response

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
    
    response = make_response(jsonify({'message': 'Registration successful'}))
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
    return response

# Login Route
@app.route('/login', methods=['POST','OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        # Preflight request
        response = jsonify({'message': 'CORS preflight'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200

    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user with the provided regid exists
    cursor.execute("SELECT * FROM users WHERE coap_reg_id = %s", (data['regid'],))
    user = cursor.fetchone()

    if user:
        encrypted_password = sha256(data['pass'].encode()).hexdigest()
        if encrypted_password == user[5]:  # Assuming the password is in the 6th column
            # print("User Matched")
            response = make_response(jsonify({'message': 'User Matched'}))
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
            return response
        else:
            # print("Incorrect Password")
            response = make_response(jsonify({'message': 'Incorrect password'}))
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
            return response
    else:
        # print("User not Found")
        response = make_response(jsonify({'message': 'User not found'}))
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response
        # return jsonify({'message': 'User not found'})

    cursor.close()
    conn.close()

# Change Password Route
@app.route('/changepassword', methods=['POST','OPTIONS'])
def change_password():
    if request.method == 'OPTIONS':
        # Preflight request
        response = jsonify({'message': 'CORS preflight'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200

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
        response = make_response(jsonify({'message': 'Password changed successfully'}))
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response
    else:
        cursor.close()
        conn.close()
        response = make_response(jsonify({'message': 'User not found'}))
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response


@app.route('/storedetails', methods=['POST', 'OPTIONS'])
def store_details():
    if request.method == 'OPTIONS':
        # Preflight request
        response = jsonify({'message': 'CORS preflight'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200

    # Check if files are part of the request
    print(request.files)
    if len(list(request.files))==0:
        response = make_response(jsonify({'message': 'No files found in the request'}))
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 400

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
        # If the user exists, update their details
        # Calculate shortlist status
        if (data['degreebranch'].lower() in ['cse', 'ee'] and data['degreequal'].lower() == 'masters'):
            if (data['category'].lower() in ['sc', 'st'] and float(data['degree8cgpa']) >= 5.5) or \
            (data['category'].lower() not in ['sc', 'st'] and float(data['degree8cgpa']) >= 6.0):
                shortlist_status = 'Shortlisted'
            else:
                shortlist_status = 'Unshortlisted'
        elif data['degreequal'].lower() == 'btech' and float(data['degree8cgpa']) >= 8.0:
            shortlist_status = 'Shortlisted'
        else:
            shortlist_status = 'Unshortlisted'

        # Add the shortlist status to the data dictionary
        data['shortlist_status'] = shortlist_status

       
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

        # Execute the query
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
        response = make_response(jsonify({'message': 'User details updated'}))
    else:
        # Insert new user's details
        insert_applicant_detail(data, file_data)
        response = make_response(jsonify({'message': 'User details stored'}))

    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
    return response

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
@app.route('/getuserdetails', methods=['GET','OPTIONS'])
def get_user_details():
    if request.method == 'OPTIONS':
        # Preflight request
        response = jsonify({'message': 'CORS preflight'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response, 200

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
        response = make_response(jsonify(user_details))
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response
    else:
        response = make_response(jsonify({'error': 'User not found'}))
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response

    cursor.close()
    conn.close()

import base64
# from flask import jsonify, make_response, request

@app.route('/admin_dashboard', methods=['GET', 'OPTIONS','POST'])
def get_admin_dashboard_data():
    data = request.get_json()
    
    # Retrieve CPI thresholds from the request
    cpi_iit = data.get('cpiIIT', 8.0)
    cpi_scst = data.get('cpiSCST', 6.5)
    cpi_other = data.get('cpiOther', 7.0)

    conn = get_db_connection()
    cur = conn.cursor()

    # Define the SQL query to filter applicants based on the CPI criteria
    query = """
    SELECT * FROM applicant_detail
    WHERE (
        (LOWER(degreeinsti) LIKE 'iit%' AND LOWER(degreequal) = 'btech' AND CAST(degree8cgpa AS FLOAT) >= %s) OR 
        (LOWER(degreeinsti) NOT LIKE 'iit%' AND LOWER(degreequal) = 'btech' AND (
            (LOWER(%s) IN ('sc', 'st') AND CAST(degree8cgpa AS FLOAT) >= %s) OR 
            (LOWER(%s) NOT IN ('sc', 'st') AND CAST(degree8cgpa AS FLOAT) >= %s)
        ))
    );
    """

    # Execute the query with the provided CPI thresholds
    cur.execute(query, (cpi_iit, 'sc', cpi_scst, 'sc', cpi_other))
    rows = cur.fetchall()

    # Define column names
    columns = [desc[0] for desc in cur.description]

    # Convert rows to a list of dictionaries
    data = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        # Convert binary data to base64-encoded strings for specific columns
        for key in row_dict:
            value = row_dict[key]
        
            if isinstance(value, memoryview):
                # Convert memoryview to bytes
                value = value.tobytes()
            if isinstance(value, (bytes, bytearray)):
                # Convert binary data to a base64 string
                # print(row_dict[key])
                row_dict[key] = base64.b64encode(value).decode('utf-8')
            else:
                # If the value is None, send 'None' as a string; otherwise, convert to string
                row_dict[key] = 'None' if value is None else str(value)
        
        data.append(row_dict)

    cur.close()
    conn.close()

    # Return the JSON response with the data
    response = make_response(jsonify(data))
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
    return response


@app.route('/admin_login', methods=['POST','OPTIONS'])
def admin_login():
    if request.method == 'OPTIONS':
        # Preflight request
        response = jsonify({'message': 'CORS preflight'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
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
        # return jsonify({'message': 'Admin Matched'}), 200
        response = make_response(jsonify({"message":'Admin Matched'}))
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    else:
        # return jsonify({'message': 'Invalid credentials'}), 401
        response = make_response(jsonify({"message": 'Invalid credentials'}))
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 401

if __name__ == '__main__':
    app.run(debug=True)
