# mx-egn-poc

## Overview
The AI tool is designed to take EML (Email) data from the user, extract relevant information, and present it in JSON format. Additionally, a user feedback system is integrated to allow users to provide feedback on the generated JSON responses, contributing to continuous improvement. It also helps users to modify the presented response in real time.

## Technical Stack
To develop the Analyzer, following technologies have been used.

- Python3
- Flask
- Open AI
- Open AI Assistant API
- Reactjs


## Backend Setup
To use the backend, we need to follow the following steps

- Create virtual environment

    **Note**: If you do not have virtual environment setup, follow below steps

    ### For Linux

    1. If pip is not in your system

    > $ sudo apt-get install python-pip

    2. Then we need to install virtualenv

    > $ pip install virtualenv

    3. Create a virtual environment now,

    > $ virtualenv virtualenv_name

    4. Now at last we just need to activate it, using command

    > $ source virtualenv_name/bin/activate

    ### For Windows

    1. Install virtualenv using

    > pip install virtualenv

    2. Now in which ever directory you are, this line below will create a virtualenv there

    > virtualenv myenv

    And here also you can name it anything.

    3. Now if you are same directory then type,

    > myenv\Scripts\activate

    You can explicitly specify your path too.

    Similarly like Linux you can deactivate it like

    > deactivate


- Create `.env` file for our environment variables. Use `.env.example` as a reference for creating it.

- Run following command inside **backend** directory to install all the necessary modules
        
    ```
        pip install -r requirements.txt
    ```

- To run the application, use following command

    ```
    python3 app.py
    ```
    

## Frontend Setup

To use the frontend setup, we need to follow the following steps

- Inside **frontend-react** directory, run following command

    ```
    num install
    ```

- To start the application run following command

    ```
    npm run start
    ```