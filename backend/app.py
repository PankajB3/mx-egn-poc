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
