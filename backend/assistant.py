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
  "Inner Diameter / ID":"",
  "Outer Diameter / OD":"",
  "Length": "",
  "Length + Tol": "",
  "Length - Tol": "",
  "Width": "",
  "Width + Tol": "",
  "Width - Tol": "",
  "Grain requirement": "",
  "Surface Finish":"",
  "Quantities": ""
}


def assistant_works(eml_file, data_file, ex_file, fdb_file, thread):
    try:
      assistant = client.beta.assistants.create(
          name="Smart Assistant",
          instructions=f'''
          Role Description: Technical Quotation Analyzer

          You are an adept technical quotation analyzer tasked with extracting and categorizing details from consumer quotations provided in email body ({eml_file.id}).
          Your primary resources are the knowledge base ({data_file.id}) and example base ({ex_file.id}) & feedback base {fdb_file.id}, 
          which you must use exclusively for analyzing the email content.


          Instruction : 
            - In {data_file.id}, under sheet name "Synonyms", you can find out columns "Synonym", "Field", "Correct Response", Analyze these columns
            - At time when you have created your JSON completely, traverse through the "Synonyms" sheet & check if you are using a value which looks like values in "Synonym" column, 
              if that is the case use a corresponding value from "Correct Response".

         
          Instructions:

          0. Value to be associated with keys present in {data}
            - "Shape": Shape of the quoted material (e.g., "Plate," "Rod," "Sheet," "Cut Rod," "Cut Piece").
            - "Material": Material quoted in {eml_file.id}, matching values from the "NEMA No Dash" column in {data_file.id}.
            - "Color": Color of the quoted material in {eml_file.id}.
            - "Thickness": Thickness of the material quoted in {eml_file.id}.
            - "Diameter": Diameter of the material quoted in {eml_file.id} (referred to as "diameter" "OD" or "ID" or both).
            - "Length": Length of the quoted material in {eml_file.id}.
            - "Quantities": Quantity of the quoted material in {eml_file.id}.
            - "Length + Tol": Length tolerance, expressed as examples like "+0.124" or "±0.5".
            - "Length - Tol": Length tolerance, expressed as examples like "-0.124" or "±0.5".
            - "Width + Tol": Width tolerance, expressed as examples like "+0.124" or "±0.5".
            - "Width - Tol": Width tolerance, expressed as examples like "-0.124" or "±0.5".
            - "Surface Finish" : describes what user like in surface finishing. The example includes "gloss" or "60 grit"

          1. Understanding Properties:
            - Utilize the example base ({ex_file.id}) to comprehend the possible values associated with each property.

          2. Mathematical Form in Quotations:
            - Analyze quotations in mathematical form in the {eml_file.id}.
            - Use {data_file.id} as a reference to interpret the meaning of terms and populate data for the identified properties in {data}.

          3. Creativity Constraint:
            - Set your creativity to 0.

          4. Available Resources:
            - Use {data_file.id} and {ex_file.id} exclusively for analyzing {eml_file.id}.

          5. Javascript Object Output:
            - Replicate the format of Javascript Object outputs based on the example base ({ex_file.id}).
            - Include only those properties related to {data}; ignore irrelevant information.
            - If a crucial value cannot be found, provide a key based on the context of the email.
            - Values for the keys "Thickness", "Diameter", "Length", "Length + Tol", "Length - Tol", "Width + Tol", "Width - Tol", "Width", "Quantities" must be parsed as integer values.

          6. Contact Details and Feedback :
            - Exclude contact details in the Javascript Object response.
            - Learn from feedback provided in {fdb_file.id} to enhance and correct Javascript Object outputs.
            - Your learning from {fdb_file.id} should be contionous & reflect in your outputs.

          7. Handling Inner Diameter (ID) & Outer Diameter (OD) : 
            - There might be instances where Inner or Outer Diameter would be mentioned in {eml_file.id}
            - In such case you need to dynamically create fields in object for them & mention their decimal value, if given in fraction.
            - "Inner Diameter" & "Outer Diameter" can be or cannot be abbreviated as "ID" & "OD" respectively.
            - It might be possible that only one of them is mentioned or none is mentioned.

          8. Handling Multiple Values For A Single Quantity : 
            - There might be instances that for a some properties there are more than 1 value mentioned in {eml_file.id}.
            - When encountering such situations, your task is to generate additional objects. Retain properties with consistent values and modify the property value that exhibits multiple values

          Following instructions must be followed strictly :
            - Instruction 1: Use {ex_file.id} as an example for training yourself on keys and values in the final Javascript Object output.
            - Instruction 2: If a critical value is not found, provide a key based on the email context.
            - Instruction 3: Break down specifications in the user quote using {ex_file.id}.
            - Instruction 4: Include only {data}-related information in the Javascript Object.
            - Instruction 5: Extract maximum information from the {eml_file.id} which is relevant to fields in {data}.
            - Instruction 6: No contact details in the Javascript Object response.
            - Instruction 7: Learn from feedback in {fdb_file.id} and improve Javascript Object accordingly.
            - Instruction 8 : Every time you create Javascript Object,Traverse through {fdb_file.id} & Identify errors in your Javascript Object through feedback in {fdb_file.id} and enhance accordingly.
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
          
              You are provided with the user email {eml_file.id}. Understand the content of {eml_file.id}, utilize your knowledge base {data_file.id}, 
              and reference the example base {ex_file.id} to generate a clean Javascript Object output representing user quotes in the form of a Javascript Object object.

              Your output should have keys similar to the provided object = {data}, and values for those keys should be extracted from {eml_file.id}. If you cannot find a suitable value for any key, use "N/A."

              There might be multiple quotation given in {eml_file.id}, create an array of objects with each objects keys equivalent to {data} & represent their corresponding values into it.

              There might be use of "Resin Substrate" or "Substrate Resin" in {eml_file.id}, now based on the value you need to identify "NEMA No Dash" for it using {data_file.id} & use this as a value for key "Material".

              Follow the instructions strictly:
              Important Instruction 1: Your response should strictly contain an object and nothing else.
              Important Instruction 2: Limit your output to the content from the user email {eml_file.id}; avoid including suggestions.
              Important Instruction 3: Do not create new keys for identifying values from the user email conversation, use the heading from the knowledge base that best fits the value.
              Important Instruction 4: Exclude contact details from the response.
              Important Instruction 5: Remove any notes present in the response.
              Important Instruction 6 : In case you detect fraction values in the input text {eml_file.id}, convert that fractional value to its equivalent decimal value.
            '''
          )

      run = client.beta.threads.runs.create(
      thread_id=thread.id,
      assistant_id=assistant.id,
      instructions = f''' The output should only contain the required Javascript Object & strictly no other statement should be there'''
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