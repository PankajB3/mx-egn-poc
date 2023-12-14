import time
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

data = {
  "Shape": "",
  "Material": "",
  "Color": "",
  "Thickness": "",
  "Diameter": "",
  "Length": "",
  "Length + Tol": "",
  "Length - Tol": "",
  "Width": "",
  "Width + Tol": "",
  "Width - Tol": "",
  "Grain requirement": "",
  "Quantities": ""
}


def assistant_works(eml_file, data_file, ex_file, fdb_file, thread):
    try:
      assistant = client.beta.assistants.create(
          name="Smart Assistant",
          instructions=f'''
                    
          Role Description: Technical Quotation Analyzer

          You are an adept technical quotation analyzer tasked with extracting and categorizing details from consumer quotations provided in email body ({eml_file.id}).
           Your primary resources are the knowledge base ({data_file.id}) and example base ({ex_file.id}), 
           which you must use exclusively for analyzing the email content.

          Instructions:

          1. Understanding Properties:
            - Utilize the example base ({ex_file.id}) to comprehend the possible values associated with each property.

          2. Mathematical Form in Quotations:
            - Analyze quotations in mathematical form in the {eml_file.id}.
            - Use {data_file.id} as a reference to interpret the meaning of terms and populate data for the identified properties in {data}.

          3. Creativity Constraint:
            - Set your creativity to 0.

          4. Available Resources:
            - Use {data_file.id} and {ex_file.id} exclusively for analyzing {eml_file.id}.

          5. JSON Output:
            - Replicate the format of JSON outputs based on the example base ({ex_file.id}).
            - Include only those properties related to {data}; ignore irrelevant information.
            - If a crucial value cannot be found, provide a key based on the context of the email.
            - Prioritize displaying "NEMA No Dash" or "NEMA Dash" for the "Material" field in JSON.

          6. Contact Details and Feedback:
            - Exclude contact details in the JSON response.
            - Learn from feedback provided in {fdb_file.id} to enhance and correct JSON outputs.

          Important Instructions:
            - Instruction 1: Use {ex_file.id} as an example for training yourself on keys and values in the final JSON output.
            - Instruction 2: If a critical value is not found, provide a key based on the email context.
            - Instruction 3: Break down specifications in the user quote using {ex_file.id}.
            - Instruction 4: Include only {data}-related information in the JSON.
            - Instruction 5: Extract maximum information from the {eml_file.id} which is relevant to fields in {data}.
            - Instruction 6: No contact details in the JSON response.
            - Instruction 7: Learn from feedback in {fdb_file.id} and improve JSON accordingly.
            - Instruction 8: Prioritize "NEMA No Dash" or "NEMA Dash" for "Material" field.
            - Instruction 9: Every time you create JSON,Traverse through {fdb_file.id} & Identify errors in your JSON through feedback in {fdb_file.id} and enhance accordingly.
          ''',
          model="gpt-4-1106-preview",
          tools=[{
              "type": "retrieval",
          }],
          file_ids=[data_file.id, eml_file.id, ex_file.id, fdb_file.id]
          )
      
      message = client.beta.threads.messages.create(
          thread_id=thread.id,
          role="user",
          content=f''' 
              Your Task: Analyze {eml_file.id} to retrieve all relevant information.

              If you observe multiple values being quoted for a single key in the conversations, aggregate them together under the corresponding key in the form of a list.
              If you aggregate values for any key in a list, ensure to replicate that change for other keys as well. Repeat values in the list to maintain the same size for each list.

              You are provided with the user email {eml_file.id}. Understand the content of {eml_file.id}, utilize your knowledge base {data_file.id}, and reference the example base {ex_file.id} to generate a clean JSON output representing user quotes in the form of a JSON object.

              Your output should have keys similar to the provided object = {data}, and values for those keys should be extracted from {eml_file.id}. If you cannot find a suitable value for any key, use "N/A."

              There mmight be multiple quotation given in  {eml_file.id}, club values in such a manner that they are relative for that particular quote in {eml_file.id}, you can also create nested lists for better representation.

              Follow the instructions strictly:
              Important Instruction 1: Your response should strictly contain an object and nothing else.
              Important Instruction 2: Limit your output to the content from the user email {eml_file.id}; avoid including suggestions.
              Important Instruction 3: Do not create new keys for identifying values from the user email conversation; use the heading from the knowledge base that best fits the value.
              Important Instruction 4: Exclude contact details from the response.
              Important Instruction 5: Remove any notes present in the response.
              Important Instruction 6: Club multiple values detected for a single key in a list only.
            '''
          )

      run = client.beta.threads.runs.create(
      thread_id=thread.id,
      assistant_id=assistant.id,
      instructions = f''' The output should only contain the required JSON object & strictly no other statement should be there'''
      )    

      while True:
        # wait until run completes
        while run.status in ['queued', 'in_progress']:
          run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
          )
          time.sleep(2)

        # error
        if run.status == "failed":
          raise Exception("Run Failed. Error: ", run.last_error)
        # return assistant message
        else:
          messages = client.beta.threads.messages.list(
              thread_id = thread.id
          )
          return messages
    except Exception as e:
        raise e


def start_assistant(eml_file, data_file, ex_file, fdb_file):
  try:
    thread = client.beta.threads.create()
    messages = assistant_works(eml_file, data_file, ex_file, fdb_file, thread)
    assistant_answer = []

    # display assistant messages
    for message in reversed(messages.data):
        if message.role == 'assistant':
          assistant_answer.append(message.content[0].text.value)
        # print(message.role + " => " + message.content[0].text.value)
    return assistant_answer
  except Exception as e:
     raise e