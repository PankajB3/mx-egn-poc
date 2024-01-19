# Import necessary Flask modules
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv 
from file_ops import *
from json_ops import *
from assistant_gpt.assistant import *
from flask_cors import CORS
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

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

tls_certifi = certifi.where()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize MongoDB connection
mongo_uri = os.getenv("MONGO_URI")  # your MongoDB Atlas connection string
db_name=os.getenv("DATABASE_NAME")
coll_name=os.getenv("COLLECTION_NAME")
client = MongoClient(mongo_uri, tlsCAFile=tls_certifi)
db = client.get_database(db_name)  # your database name
collection = db.get_collection(coll_name)  #  your collection name

os.makedirs('uploads', exist_ok=True)

# The following API handler takes an example output excel sheet in input, which could be used a a reference for our Assistant API
# method POST
# Parameter : Excel Sheet for example output
@app.route('/api/upload_example_output', methods=['POST'])
def upload_example_file():
    try:
        # Check if the POST request has a file part
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})

        file = request.files['file'] # access file in the request, using 'file' as key

        # Check if the file is empty
        if file.filename == '':
            return jsonify({'error': 'No selected file'})

        # Check if the file has an allowed extension
        if file :
            filename = file.filename
            file.save(os.path.join('uploads', filename)) # saving file to uploads directory 
            example_output_to_text_file(filename) # calling the method to convert our file to a text file.
            return jsonify({'message': 'File uploaded successfully'})

        return jsonify({'error': 'Invalid file format'})
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

# The following API handler takes an excel sheet as a input, which could be used to create knowledge base for our Assistant API
# method POST
# Parameter excel file for knowledge base 
@app.route('/api/upload_knowledge_base', methods=['POST'])
def upload_knowledge_base():
    try:
        # Check if the POST request has a file part
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})

        # access file in the request, using 'file' as key
        file = request.files['file']

        # Check if the file is empty
        if file.filename == '':
            return jsonify({'error': 'No selected file'})

        # Check if the file has an allowed extension
        if file :
            filename = file.filename
            file.save(os.path.join('uploads', filename)) # saving file to uploads directory 
            knowledge_base_to_text_file(filename) # calling the method to convert our file to a text file.
            return jsonify({'message': 'File uploaded successfully'})

        return jsonify({'error': 'Invalid file format'})
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


# Define a route to eml data
# method  POST
# Parameters : 
# email_conversations : EML data provided by user    
@app.route('/api/upload_eml', methods=['POST'])
def upload_eml():
    try:
        # Get form data
        data = request.form.get('email_conversation')

        corrected_json = correct_json_text(data)

        # Save the uploaded file to a local folder
        json_file_path = os.path.join('uploads', "output_email.json")
        with open(json_file_path, 'w') as file : 
            file.write(corrected_json)

        extract_first_message(json_file_path)

        (data_file, conv_file, ex_output_file, feedback_file) = upload_file_openai()

        messages = start_assistant(conv_file, data_file, ex_output_file, feedback_file)

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


# Define a route to handle JSON object uploads to MongoDB
# method : POST
@app.route('/api/store_json', methods=['POST'])
def store_json_in_mongo():
    try:
        # Get JSON object from request body
        data = request.json
        data2 = json.loads(data)
        # Insert the JSON object into MongoDB
        result = collection.insert_one(data2)
        # Return success response
        return jsonify({'message': 'JSON object stored successfully', 'id': str(result.inserted_id)}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500


# update json data response as per instruction given by user.
# method POST
# Paramters : 
    # updateJSONInput : user instruction
    # emlData : JSON response object
@app.route('/api/update_json', methods=['POST'])
def update_json():
    try:
        # accessing request body
        body_data = request.get_json()
        # accessing the instruction received from user, on basis of which data needs to be improved
        instruction = body_data.get('updateJSONInput')
        # accessing the particular JSON data for which instruction is passed
        jsonData = body_data.get('emlData')
        # calling menthod, which can improve our Data object according to our instructions
        improved_json = improveJSONData(instruction, jsonData)
        # returning the improved version of our JSON data
        return jsonify({'message': improved_json}), 200
    except Exception as e:
        raise e

# Define a route to handle feedback given by the user
# method : POST
# Paramters : 
    # jsonData : JSON data which would have been created from EML given by user
    # feedbackText : feedback given by user for the particuylar JSON data
@app.route('/api/feedback', methods=['POST'])
def upload_feedback():
    try:
        # Get form data
        data = request.get_json() # accessing request body
        # accessing JSON data which would have been created from EML given by user
        json_data = data.get('jsonData') 
        # accessing feedback given by user for the particuylar JSON data
        feedback_data = data.get('feedbackText') 

        # creating path to store feedback
        feedback_file_path = 'uploads/feedback_data.txt' 
        
        #creating template string which properly establishes feedback with JSON object, enhances understanding for AI assistant 
        feedback_string = f'''\n The JSON data provided by you is {json_data} & related feedback given by user is {feedback_data}.'''

        # Validate data
        if not json_data or not feedback_data:
            return jsonify({'error': 'Invalid data. Both jsonData and feedbackText are required.'}), 400
        
        # checking if our feedback file is in existence or not & accordingly writing data to the file
        if not os.path.exists(feedback_file_path):
            with open(feedback_file_path, 'w') as file:
                file.write(feedback_string)

        with open(feedback_file_path, 'a') as file:
            file.write(feedback_string)
        return jsonify({'message': 'Feedback submitted successfully'}), 200 # returning success message
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


# Home route
@app.route('/api')
def index():
    return jsonify({'message': "Server Running"}), 200

# on start of application we check if our feedback file is ready for AI asistant
create_or_open_text_file()

if __name__ == '__main__':
    app.run("0.0.0.0", port=os.getenv('PORT'))
