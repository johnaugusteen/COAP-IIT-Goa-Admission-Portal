from flask import Flask, request, jsonify
import csv
from hashlib import sha256
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5500","127.0.0.1:5500","127.0.0.1:5000","http://127.0.0.1:5000"]}})

@app.route('/register', methods=['POST'])
def register():
    data = request.json

    # Check if user with the same regid already exists
    with open('./users.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[4] == data['regid']:
                return jsonify({'message': 'User already exists'})

    # Encrypt the password using SHA-256
    encrypted_password = sha256(data['pass'].encode()).hexdigest()

    # Prepare the data to be written in CSV format
    user_data = [data['name'], data['dob'], data['mobile'], data['email'], data['regid'], encrypted_password, data['year']]

    # Write the data to the CSV file
    with open('./backend/users.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(user_data)

    return jsonify({'message': 'Registration successful'})
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    # Check if user with the provided regid exists
    with open('./backend/users.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[4] == data['regid']:
                # Decrypt and compare the password using SHA-256
                encrypted_password = sha256(data['pass'].encode()).hexdigest()
                if encrypted_password == row[5]:
                    # Password matches, redirect to applicantdetails.html
                    return jsonify({'message': 'User Matched'})
                else:
                    return jsonify({'message': 'Incorrect password'})

    return jsonify({'message': 'User not found'})
@app.route('/changepassword', methods=['POST'])
def change_password():
    data = request.json

    # Check if user with the provided regid exists
    with open('./backend/users.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        rows = list(reader)
        for row in rows:
            if row[4] == data['regid']:
                # Encrypt the new password using SHA-256
                encrypted_password = sha256(data['pass'].encode()).hexdigest()
                # Update the password in the CSV file
                row[5] = encrypted_password
                # Rewrite the CSV file with updated password
                with open('./backend/users.csv', mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(rows)
                return jsonify({'message': 'Password changed successfully'})

    return jsonify({'message': 'User not found'})
# @app.route('/storedetails', methods=['POST'])
# def store_details():
#     data = request.json

#     # Check if user with the same regid already exists
#     with open('./data.csv', mode='r', newline='') as file:
#         reader = csv.reader(file)
#         for row in reader:
#             if row[4] == data['regid']:
#                 # If the user already exists, update their details
#                 row_index = reader.line_num - 1
#                 break
#         else:
#             # If the user does not exist, append their details to the CSV
#             row_index = None

#     with open('./data.csv', mode='a', newline='') as file:
#         writer = csv.writer(file)

#         if row_index is not None:
#             # Update existing user's details
#             writer.writerow([data[field] for field in data])  # Assuming all fields are in correct order
#             return jsonify({'message': 'User details updated'})
#         else:
#             # Append new user's details
#             writer.writerow([data[field] for field in data])  # Assuming all fields are in correct order
#             return jsonify({'message': 'User details stored'})
@app.route('/storedetails', methods=['POST'])
def store_details():
    data = request.json

    # Check if user with the same regid already exists
    with open('./backend/data.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        rows = list(reader)

    regid_exists = False
    for row in rows:
        if row and row[-1] == data['regid']:  # Assuming regid is the last field in the CSV
            # If the user already exists, update their details
            row_index = rows.index(row)
            regid_exists = True
            break

    # Prepare data for writing to CSV
    user_data = [
        data['name'], data['appno'], data['dob'], data['addno'], data['mobile'], data['email'], data['category'],
        data['pwd'], data['ews'], data['gender'], data['rank2021'], data['rollno2021'], data['score2021'],
        data['discipline2021'], data['rank2022'], data['rollno2022'], data['score2022'], data['discipline2022'],
        data['rank2023'], data['rollno2023'], data['score2023'], data['discipline2023'], data['hsscdate'],
        data['hsscpercentage'], data['sscdate'], data['sscpercentage'], data['sscboard'], data['degreepassingdate'],
        data['degree7percentage'], data['degree7cgpa'], data['degree8percentage'], data['degree8cgpa'],
        data['degreequal'], data['degreeinsti'], data['degreebranch'], data['regid']
    ]
    # print(data["regid"])

    # Write or update user details in CSV
    with open('./backend/data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        if regid_exists:
            rows[row_index] = user_data
            writer.writerows(rows)
            return jsonify({'message': 'User details updated'})
        else:
            writer.writerow(user_data)
            return jsonify({'message': 'User details stored'})
@app.route('/getuserdetails', methods=['GET'])
def get_user_details():
    regid = request.args.get('regid')

    with open('./backend/data.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        rows = list(reader)

    # Get column headings from the first row of the CSV
    column_headings = [
        'name', 'appno', 'dob', 'addno', 'mobile', 'email', 'category',
        'pwd', 'ews', 'gender', 'rank2021', 'rollno2021', 'score2021',
        'discipline2021', 'rank2022', 'rollno2022', 'score2022', 'discipline2022',
        'rank2023', 'rollno2023', 'score2023', 'discipline2023', 'hsscdate',
        'hsscpercentage', 'sscdate', 'sscpercentage', 'sscboard', 'degreepassingdate',
        'degree7percentage', 'degree7cgpa', 'degree8percentage', 'degree8cgpa',
        'degreequal', 'degreeinsti', 'degreebranch', 'regid'
    ]

    # Search for the user with the provided regid
    for row in rows:
        if row and row[-1] == regid:  # Assuming regid is the last field in the CSV
            user_details = dict(zip(column_headings, row))
            return jsonify(user_details)

    # If user not found, return appropriate message
    return jsonify({'error': 'User not found'})


if __name__ == '__main__':
    app.run(debug=True)
