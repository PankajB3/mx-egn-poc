import React from 'react';
import logo from './logo.svg';
import './App.css';
import { useState } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';

function App() {

    const [emlData, setEmlData] = useState({})
    const [fileName, setFileName] = useState("")
    const [submitBtnDisabled, setSubmitBtnDisable] = useState(true)
    const [feebackBtn, setFeedbackBtn] = useState(false)
    const [redirectToFeedback, setRedirectToFeedback] = useState(false)
    const [emailContent, setEmailContent] = useState("")

    const navigate = useNavigate()

    // @ts-ignore
    const setMyRedirect = async() => {    
        navigate('/feedback', {state:emlData})
    }

 //@ts-ignore
    const saveEmlDataToDB = async() =>{
        try{
            // console.log("Hello");
            let res = await fetch('http://34.70.229.241/api/store_json',{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', // Specify the content type as JSON
                },
                body: JSON.stringify(emlData),
            })
            if(res.ok){
                const result = await res.json(); // Await the result of res.json()
                alert(result.message); 
            }else{
                alert("Data Failed to Stored Successsfully")
            }
        }catch(err){
            alert(`Error : ${err}`)
        }
    }

//@ts-ignore
  const submitHandler = async() => {
    setSubmitBtnDisable(true)
    console.log("36");
    //@ts-ignore
     // Get the file input element
     var fileInput = document.getElementById('fileInput');
     var submitBtn = document.getElementById('submitBtn');

     //@ts-ignore
     // Check if a file is selected
     if (fileInput.files.length === 0) {
         alert('Please select an EML file before submitting.');
         return;
     }

     //@ts-ignore
     // Disable the submit button
     submitBtn.disabled = true;

     //@ts-ignore
     // Get the selected file name
     var fileName = fileInput.files[0].name;

     // Create FormData object to send the file to the server
     var formData = new FormData();
     //@ts-ignore
     formData.append('file', fileInput.files[0]);

     //@ts-ignore
     // Show file upload message with the file name
     document.getElementById('results').innerText = `File "${fileName}" Is Being Processed. Please wait...`;
     // Create an AbortController to handle the timeout
     const controller = new AbortController();
     const timeoutId = setTimeout(() => controller.abort(), 120000); // Timeout set to 20 seconds

     try {
        // Send a POST request to the server to handle the file upload
        const response = await fetch('http://34.70.229.241/api/upload_eml', {
          method: 'POST',
          body: formData,
          signal: controller.signal, // Pass the AbortSignal to the fetch request
        });
    
        const data = await response.json();
        setSubmitBtnDisable(false);
        setFileName("");
        console.log("data", data);
    
        // Extract the JSON string from the message
        var jsonString = data && data.message && data.message[0] ? data.message : null;
        console.log("jsonString ==", jsonString);
    
        // Parse the JSON string into a JavaScript object
        var jsonObject = jsonString ? JSON.parse(jsonString) : null;
        console.log("jsonObject == ", jsonObject);
    
        // Format and display the received JSON data
        var formattedJson = JSON.stringify(jsonObject, null, 2);
        setEmlData(formattedJson);
        //@ts-ignore
        document.getElementById('results').innerText = '\n' + formattedJson + '\n';
        setFeedbackBtn(true);
      } catch (error) {
        if (error instanceof Error) {
          if (error.name === 'AbortError') {
            alert('Request timed out. Please try again.');
            window.location.reload()
          } else {
            console.error('Error:', error);
            alert('An error occurred while processing the file. Please try again.');
            window.location.reload()
          }
        } else {
          console.error('Unknown error:', error);
          alert('An unknown error occurred. Please try again.');
          window.location.reload()
        }
      } finally {
        clearTimeout(timeoutId); // Clear the timeout to prevent it from triggering after the request is complete
        //@ts-ignore
        // document.getElementById('results').innerText = ''; // Clear the results message
      }
  }

  //@ts-ignore
  const fileChangeHandler = (e) => {
    // console.log("File Change Handler", e.target.files[0].name);
    
    if(e.target.files.length > 0) {
        // console.log("File Change Handler", e.target.files[0].name);
        setFileName(e.target.files[0].name)
        setSubmitBtnDisable(false)
    }
  }

  return (
    <div className="App">
          <div className="container max-w-5xl mx-auto p-4">
        <div className="flex justify-between gap-4">
            <div className="flex-1">
                <h1 className="text-3xl font-bold mb-8">EML Analyzer</h1>
                <form id="uploadForm" encType="multipart/form-data">
                    <label htmlFor="fileInput" className="cursor-pointer">
                        <div className="bg-white p-10 border-4 border-dashed border-blue-500 rounded-lg mb-4 flex items-center justify-center text-gray-500">
                        {fileName.length == 0 ? "No File Selected" : `${fileName} ✉️ Selected`}
                        </div>
                    </label>
                    <input type="file" id="fileInput" className="hidden" accept=".json" onChange={(e) => fileChangeHandler(e)}/>
                    {/* <div id="dynamicText" className="text-gray-600 mt-2">{fileName.length == 0 ? "No File Selected" : `${fileName} Selected`}</div> */}
                    <button type="button" id="submitBtn" className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" onClick={submitHandler} disabled={submitBtnDisabled}>
                        Submit
                    </button>
                </form>
            </div>
            {/* <!-- Right Side --> */}
            <div className="flex-1">
                <h2 className="text-2xl font-bold mb-2">Results</h2>
                <div id="results" className="bg-white p-10 border-4 border-green-500 rounded-lg h-96" style={{overflow :"scroll"}}></div>
                
                {feebackBtn ? <div>
                    <div className="text-sm text-gray-600 mt-2 text-left">
                    Is the output correct?
                </div>
                <div className="flex justify-between mt-4">
                    <button className="flex items-center justify-center bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-6 rounded" onClick={saveEmlDataToDB}>
                        <span>Yes</span>
                    </button>
                    <button className="flex items-center justify-center bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-6 rounded" onClick={setMyRedirect}>
                        <span>No</span>
                    </button>
                </div>
                </div> : ""}
                
            </div>
        </div>
    </div>
    </div>
  );
}

export default App;
