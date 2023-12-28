from email.parser import BytesParser
from email import policy
from dotenv import load_dotenv
import os
from openai import OpenAI
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
# USE THIS
def store_as_text_file(eml_file_path):
    try:
        # Load the EML file
        with open(eml_file_path, 'rb') as file:
            msg = BytesParser(policy=policy.default).parse(file)

        # Extract information from the parsed message
        subject = msg['subject'] if 'subject' in msg else 'No Subject'
        from_address = msg['from'] if 'from' in msg else 'Unknown Sender'
        to_address = msg['to'] if 'to' in msg else 'Unknown Recipient'
        date = msg['date'] if 'date' in msg else 'Unknown Date'

        # Extract the email body
        body = ""
        if msg.is_multipart():
            for part in msg.iter_parts():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

        # Save the email content to a text file
        text_file_path = os.path.join('uploads', 'output_email.txt')
        with open(text_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(f'Subject: {subject}\n')
            output_file.write(f'From: {from_address}\n')
            output_file.write(f'To: {to_address}\n')
            output_file.write(f'Date: {date}\n\n')
            output_file.write(body)

        # Remove the EML file
        os.remove(eml_file_path)
    except Exception as e:
        raise e


def improve_josn_response(data):
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        response_format={ "type": "json_object" },
        messages=[
                {"role": "system", "content": f''' You are a helpful assistant. You need to make data provided by user into a valid json'''},
                {"role" :"user", "content" : f''' Data is {data}. Additionally fields such as "Thickness", "Diameter", "Inner Diameter",
                    "Outer Diameter", "Length", "Length+Tol", "Length-Tol", "Width", "Width+Tol, "Width-Tol", "Quantities" are numeric quantities.
                    Trim any non numeric value associated with these keys except "N/A".
                 '''}
            ]
    )
    print("\n\n====correct json 2 ===== \n\n", response.json())
    return response.choices[0].message.content


def correct_json_text(text):
    print("\n\n====Correcting JSON=====\n\n")
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        response_format={ "type": "json_object" },
        messages=[
                {"role": "system", "content": "You are a helpful assistant. You need to make data provided by user into a valid json"},
                {"role" :"user", "content" : f''' Data is {text} '''}
            ]
    )
    print("\nCorrect JSON 1====\n",response)
    return response.choices[0].message.content


def correct_json(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    print("\n\n====Correcting JSON=====\n\n")
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        response_format={ "type": "json_object" },
        messages=[
                {"role": "system", "content": "You are a helpful assistant. You need to make data provided by user into a valid json"},
                {"role" :"user", "content" : f''' Data is {data} '''}
            ]
    ) 
    # Write corrected text back to the JSON file
    with open(json_file_path, 'w') as file:
        file.write(response.choices[0].message.content)

def extract_first_message(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            messages = data.get("Messages", [])

            if messages:
                first_message = messages[0]
                subject = first_message.get("Subject", "")
                blurb = first_message.get("Blurb", "")

                output_text = f'''Email Body \n {blurb}'''

                with open("uploads/output_json.txt", 'w') as output_file:
                    output_file.write(output_text)

                print("First message extracted and stored in output_json.txt.")
            else:
                with open("uploads/output_json.txt", 'w') as output_file:
                    output_file.write("This File Didn't Had Messages")
        os.remove(json_file_path)
    except FileNotFoundError:
        raise FileNotFoundError("File Not Found")
    except json.JSONDecodeError as je:
        raise je
    except Exception as e:
        raise e



def create_or_open_text_file():
    try:
        file_path = 'uploads/feedback_data.txt'
        # Open the file in write and read mode ('w+'), creating it if it doesn't exist
        if not os.path.exists(file_path):
            with open(file_path, 'w+') as file:
                file.write("This is the FEEDBACK given by user after seeing the JSON result generated by you.\n")
                print(f"Text file created or already exists at: {file_path}")
        else:
            pass
    except Exception as e:
        raise e