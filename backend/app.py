# Import necessary Flask modules
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv 
from file_ops import *
from json_ops import *
from assistant_gpt.assistant import *
from flask_cors import CORS
# from flask_pymongo import PyMongo
from pymongo import MongoClient
import pandas as pd
import os
import certifi
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

CORS(app)

tls_certifi = certifi.where()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize MongoDB connection
mongo_uri = os.getenv("MONGO_URI")  # your MongoDB Atlas connection string
client = MongoClient(mongo_uri, tlsCAFile=tls_certifi)
db = client.get_database("mx-egn-poc")  # your database name
collection = db.get_collection("emlData")  #  your collection name

os.makedirs('uploads', exist_ok=True)

@app.route('/api/upload_example_output', methods=['POST'])
def upload_example_file():
    try:
        # Check if the POST request has a file part
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})

        file = request.files['file']

        # Check if the file is empty
        if file.filename == '':
            return jsonify({'error': 'No selected file'})

        # Check if the file has an allowed extension
        if file :
            filename = file.filename
            file.save(os.path.join('uploads', filename))
            example_output_to_text_file(filename)
            return jsonify({'message': 'File uploaded successfully'})

        return jsonify({'error': 'Invalid file format'})
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload_knowledge_base', methods=['POST'])
def upload_knowledge_base():
    try:
        # Check if the POST request has a file part
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})

        file = request.files['file']

        # Check if the file is empty
        if file.filename == '':
            return jsonify({'error': 'No selected file'})

        # Check if the file has an allowed extension
        if file :
            filename = file.filename
            file.save(os.path.join('uploads', filename))
            knowledge_base_to_text_file(filename)
            return jsonify({'message': 'File uploaded successfully'})

        return jsonify({'error': 'Invalid file format'})
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

# Define a route to handle JSON object uploads to MongoDB
@app.route('/api/store_json', methods=['POST'])
def store_json_in_mongo():
    try:
        # Get JSON object from request body
        data = request.json

        # print("46",data)
        data2 = json.loads(data)

        # Insert the JSON object into MongoDB
        result = collection.insert_one(data2)

        # Return success response
        return jsonify({'message': 'JSON object stored successfully', 'id': str(result.inserted_id)}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


# Define a route to handle file uploads
@app.route('/api/upload_eml', methods=['POST'])
def upload_eml():
    try:
        # Check if the file is included in the request
        # if 'file' not in request.files:
        #     return jsonify({'error': 'No file provided'}), 400

        # file = request.files['file']

        # Check if the file has the correct extension
        # if not file.filename.endswith('.json'):
        #     return jsonify({'error': 'Invalid file format. Please upload a .json file'}), 400

        # Get form data
        data = request.form.get('email_conversation')

        print(data)

        corrected_json = correct_json_text(data)

        # Save the uploaded file to a local folder
        json_file_path = os.path.join('uploads', "output_email.json")
        with open(json_file_path, 'w') as file : 
            file.write(corrected_json)
        # file.save(file_path)
        # os.rename(file_path, "uploads/output_email.json") # renaming file so that we can have a consistent name

        # json_file_path = "uploads/output_email.json"

        # upload_knowledge_base_file()
        # store_as_text_file(eml_file_path)

        # correct_json(json_file_path)

        extract_first_message(json_file_path)

        (data_file, conv_file, ex_output_file, feedback_file) = upload_file_openai()

        messages = start_assistant(conv_file, data_file, ex_output_file, feedback_file)

        print(messages)

        # os.remove("uploads/output_email.json") # deleting the conversation json from system
        # os.remove("uploads/output_email.txt")

        if messages:
            # If messages list is not empty, access the first element
            response_message = messages[0].replace("\n", "").replace("\ ", "")

            ai_response = improve_josn_response(response_message)
            
            return jsonify({'message': ai_response}), 200
        else:
            # If messages list is empty, provide a default message or handle it accordingly
            return jsonify({'message': 'No messages available'}), 200
    except json.JSONDecodeError as je:
        return jsonify({'error' : "Invalid JSON format"})
    except FileNotFoundError as fe:
        return jsonify({'error': f'File not found: {fe}'}), 404

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


# update json data as per instruction given by user.
@app.route('/api/update_json', methods=['POST'])
def update_json():
    try:
        body_data = request.get_json()
        instruction = body_data.get('updateJSONInput')
        jsonData = body_data.get('emlData')



        improved_json = improveJSONData(instruction, jsonData)
        return jsonify({'message': improved_json}), 200
    except Exception as e:
        raise e

# Define a route to handle feedback given by the user
@app.route('/api/feedback', methods=['POST'])
def upload_feedback():
    try:
        # Get form data
        data = request.get_json()
        json_data = data.get('jsonData')
        feedback_data = data.get('feedbackText')

        feedback_file_path = 'uploads/feedback_data.txt'
        feedback_string = f'''\n The JSON data provided by you is {json_data} & related feedback given by user is {feedback_data}.'''

        # Validate data
        if not json_data or not feedback_data:
            return jsonify({'error': 'Invalid data. Both jsonData and feedbackText are required.'}), 400
        
        if not os.path.exists(feedback_file_path):
            with open(feedback_file_path, 'w') as file:
                file.write(feedback_string)

        with open(feedback_file_path, 'a') as file:
            file.write(feedback_string)
        return jsonify({'message': 'Feedback submitted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# Define a route to display a simple form for file upload
@app.route('/api')
def index():
    return jsonify({'message': "Server Running"}), 200

create_or_open_text_file()

if __name__ == '__main__':
    app.run("0.0.0.0", port=os.getenv('PORT'))
