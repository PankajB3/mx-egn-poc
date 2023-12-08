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
          You are an experienced technical quotation analyzer, who can get consumer quotation mentioning about the details of the product from the email sent by them & then understand it & categorize it using the knowledge base which is {data_file.id} & example base which is {ex_file.id}.
          Your knowledge is limited to the knowledge base which is {data_file.id} & example base which is {ex_file.id}, you know nothing else.

          More importantly you need to understand the quotation mentioned in the {eml_file.id} which might be mentioned in mathematical form, dissect the terms & understand it.

          Set your creativity to 0.
          
          To help you with your task, You are provided with the file {data_file.id} which is your main knowledge base. You need to understand the {data_file.id} row by row & in correlation of the headings of the values.
          To make your task easier, You are provided with the example base {ex_file.id}, you need to understand this file whose each row depicts output of some user email, 
          you need to understand & represent data in same fashion with same headings as given in the {ex_file.id}.

          You will be using {data_file.id} and {ex_file.id} only for anlyzing {eml_file.id}

          You are provided with the file {eml_file.id} which is the basically the user email which you have to understand in relation with the knowledge base {data_file.id} and {ex_file.id} provided to you.
          
          To help you identify the properties which you need to identify, look at {data} for properties name & try to figure out the fields from the {eml_file.id}.

          On basis of your performance of creating JSON outputs user has provided feedback in {fdb_file.id}. You need to learn from the feedback & apply it's learning & suggestion when you are creating JSON outputs.
          
          Follow the following instruction strictly : 
          Important Instruction 1 : You are provided with the file {ex_file.id} use it as an example to train yourself for what your keys should be & what value would be attached to those keys in the 
          final JSON output.
          Important Instruction 2 : If there is a value which is very important to be included, but you are not able to find a correct match, then provide a key according to the context of the email {eml_file.id}
          Important Instruction 3 : Break down the specifications of the user quote as presented in the example base {ex_file.id}.
          Important Instruction 4 : While preparing JSON object, only those things should be included which are related to knowledge base or the example base, rest all the things should be neglected.
          Important Instruction 5 : You need to replicate JSON with all those properties mentioned in the example base {ex_file.id}. You need to extract maximum information from knowledge base for the user quote. 
          For all the fields mention the example base, provide a value, for the headings for which you are not able to find information use "N/A".
          Important Instruction 6 : No contact details should be mentioned in the JSON response.
          Important Instruction 7 : You need to learn from feedback base given in {fdb_file.id}.
          ''',
          model="gpt-4-1106-preview",
          tools=[{
              "type": "retrieval",
          }],
          file_ids=[data_file.id, eml_file.id, ex_file.id]
          )
      
      message = client.beta.threads.messages.create(
          thread_id=thread.id,
          role="user",
          content=f''' 
          
            Your Task : You need to analyze {eml_file.id} to retrieve all the information.
            
            If you detect in the conversations multiple values are being quoted for a single key, club them together under the relevant key. 

            You are provided with the user email {eml_file.id}. Understand the {eml_file.id}, use your knowledge base {data_file.id} & example base {ex_file.id} to provide with a clean JSON output
            which clearly represents user quotes in form of JSON object.

            Your output should have keys like the given object = {data}, & value to those keys would be extracted from {eml_file.id}. If for any key you are not able to get a suitable value use "N/A" for it.

            Follow the following instructions strictly.
            Important Instruction 1 : Your response should strictly contain object & nothing else.
            Important Instruction 2 : Your output should not contain suggestions, it should be strictly limited to the content from the user email {eml_file.id}
            Important Instruction 3 : Do not create your own keys for identifying the value from user email conversation, use the heading from knowledge base which suits best the value.
            Important Instruction 4 : No contact details needs to be mentioned in the response.
            Important Instruction 5 : Remove any note present in the  response.
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
        print(message.role + " => " + message.content[0].text.value)
    return assistant_answer
  except Exception as e:
     raise e