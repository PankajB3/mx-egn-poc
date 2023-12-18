from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
import json

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def knowledge_base_to_text_file(filename):
    try:
        # read the excel file
        file_path = os.path.join('uploads', filename)
        df = pd.ExcelFile(file_path)
        #  Specify the path for the text file
        text_file_path = 'uploads/knowledge_base.txt'

        if len(df.sheet_names) > 1 :
            # Iterate through each sheet and append to the text file
            with open(text_file_path, 'a', encoding='utf-8') as text_file:
                for sheet_name in df.sheet_names:
                    # Read the sheet
                    df = pd.read_excel(file_path, sheet_name)

                    # Add sheet name as a heading
                    text_file.write(f"\n\nSheet Name: {sheet_name}\n")

                    # Save the DataFrame to a tab-delimited text file
                    df.to_csv(text_file, sep='\t', index=False, header=True, mode='a')
        elif len(df.sheet_names) == 1:
            # Save the DataFrame to the text file, tab-separated
            df = pd.read_excel(file_path)
            df.to_csv(text_file_path, sep='\t', index=False, header=True, mode='a')
    except Exception as e:
        raise e


def example_output_to_text_file(filename):
    try:
        # read the excel file
        file_path = os.path.join('uploads', filename)
        df = pd.ExcelFile(file_path)
        #  Specify the path for the text file
        text_file_path = 'uploads/example_output_data.txt'
        
        if len(df.sheet_names) > 1 :
            # Iterate through each sheet and append to the text file
            with open(text_file_path, 'a', encoding='utf-8') as text_file:
                print(df.sheet_names)
                for sheet_name in df.sheet_names:
                    # Read the sheet
                    df = pd.read_excel(file_path, sheet_name)

                    # Add sheet name as a heading
                    text_file.write(f"\n\nSheet Name: {sheet_name}\n")

                    # Save the DataFrame to a tab-delimited text file
                    df.to_csv(text_file, sep='\t', index=False, header=True, mode='a')
        elif len(df.sheet_names) == 1:
            # Save the DataFrame to the text file, tab-separated
            df = pd.read_excel(file_path)
            df.to_csv(text_file_path, sep='\t', index=False, header=True, mode='a')
    except Exception as e:
        raise e


def upload_file_openai():
    try:
        if(os.path.exists("uploads/knowledge_base.txt") and 
        os.path.exists("uploads/example_output_data.txt") and 
        os.path.exists("uploads/output_json.txt") and 
        os.path.exists("uploads/feedback_data.txt")):
            
            # Upload a file with an "assistants" purpose
            data_file = client.files.create(
            file=open("uploads/knowledge_base.txt", "rb"),
            purpose='assistants'
            ) 
            # Upload a file with an "assistants" purpose
            example_output_file = client.files.create(
            file=open("uploads/example_output_data.txt", "rb"),
            purpose='assistants'
            )   
            # Upload a eml file with an "assistants" purpose
            eml_file = client.files.create(
            file=open("uploads/output_json.txt", "rb"),
            purpose='assistants'
            )
            # Upload a file with an "assistants" purpose
            feedback_file = client.files.create(
            file=open("uploads/feedback_data.txt", "rb"),
            purpose='assistants'
            )   
            return data_file, eml_file, example_output_file, feedback_file
        else :
            raise FileNotFoundError("Files Are Missing")
    except Exception as e:
        raise e

def improveJSONData(instruction, json_data):
    response = client.chat.completions.create(
    model="gpt-4-1106-preview",
    response_format={ "type": "json_object" },
    messages=[
                {"role": "system", "content": "You are a helpful assistant. You will be provided with instruction & JSON Data by the user. You need to update the JSON data as per the instruction given by user."},
                {"role" :"user", "content" : f''' JSON Data is {json_data} & instruction given are {instruction}. Return a clean JSON output without anything extra attached to it.'''}
            ]
    )
    return response.choices[0].message.content