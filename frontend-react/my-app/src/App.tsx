import React from 'react';
import './App.css';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';


function App() {
    //  state to store EML Data
    const [emlData, setEmlData] = useState({})
    // state to handle submit button able/disable property, initially false
    const [submitBtnDisabled, setSubmitBtnDisable] = useState(false)
    // state to handle feedback button able/disable property, initially false 
    const [feebackBtn, setFeedbackBtn] = useState(false)
    //  state to store EML
    const [emailContent, setEmailContent] = useState("")
    //  state to JSON
    const [updateJSONInput, setUpdateJSONInput] = useState("")

    const navigate = useNavigate()

    // @ts-ignore
    const setMyRedirect = async() => {
      // navigates to feedback page, with the JSON data
        navigate('/feedback', {state:emlData})
    }

//@ts-ignore
  const submitHandler = async() => {
    setSubmitBtnDisable(true) // disabling submit button
    //@ts-ignore
     // Get the file input element
     var submitBtn = document.getElementById('submitBtn');
     //@ts-ignore
     // Disable the submit button
     submitBtn.disabled = true;
     // Create FormData object to send the file to the server
     var formData = new FormData();
     //@ts-ignore
     formData.append('email_conversation',emailContent);
     //@ts-ignore
     // Show file upload message with the file name
     document.getElementById('results').innerText = `Your JSON Is Being Processed. Please wait...`;
     // Create an AbortController to handle the timeout
     const controller = new AbortController();
     const timeoutId = setTimeout(() => controller.abort(), 1040000); // Timeout set to 4 minutes

     try {
        // Send a POST request to the server to handle the file upload
        const response = await fetch('http://34.70.229.241/api/upload_eml', {
          method: 'POST',
          body: formData,
          signal: controller.signal, // Pass the AbortSignal to the fetch request
        });
    
        const data = await response.json();
        setSubmitBtnDisable(false);
    
        // Extract the JSON string from the message
        var jsonString = data && data.message && data.message[0] ? data.message : null;
       
        // Parse the JSON string into a JavaScript object
        var jsonObject = jsonString ? JSON.parse(jsonString) : null;
        
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
      }
  }

  // Form submission handler for updating JSON data
  //@ts-ignore
  const updateJSONFormHandler = async(event) => {
    try{
      // Prevent the default form submission behavior
      event.preventDefault()
      
      // Display a message indicating that JSON update is in progress
      // @ts-ignore
      document.getElementById('results').innerText = "We Are Updating JSON As Per Instructions Please Wait..."
       // Perform a fetch request to the '/api/update_json' endpoint
      const result = await fetch('http://34.70.229.241/api/update_json', {
        method:'POST',
        headers:{
          'Content-Type':'application/json'
      },
        body:JSON.stringify({updateJSONInput, emlData}) // Send JSON payload containing 'updateJSONInput' and 'emlData'
      })
      // Parse the response JSON
      const data = await result.json()
      if(result.ok){
        // Update the results area with the success message
        // @ts-ignore
        document.getElementById('results').innerText = data.message
        // Update the 'emlData' state with the received message
        setEmlData(data.message)
        // Clear the input field with the name 'instructionText'
        // @ts-ignore
        document.getElementsByName('instructionText').value = ''
      }else{
        // Display an alert in case of an error during JSON update
        alert("Error In Updating JSON")
      }
    }catch(err){
      alert(`Error : ${err}`)
    }
  }


  return (
<div className="App">
  <div className="flex flex-col min-h-screen bg-gray-100">
      <div className="container mx-auto p-4 flex flex-col lg:flex-row items-center justify-center">
        {/* Left Side with Heading */}
        <div className="lg:flex-1 w-full mb-8 lg:mb-0">
          <h1 className="text-4xl font-extrabold mb-8 text-center lg:text-left text-blue-500">
            EML Analyzer
          </h1>
          <form id="uploadForm" encType="multipart/form-data">
            <div className="border-dotted border-4 border-blue-500 mb-4 overflow-hidden rounded-md mx-4">
              <textarea
                name="email"
                cols={40}
                rows={13}
                placeholder="Paste Your JSON Here"
                className="w-full p-4 resize-none focus:outline-none"
                onChange={(e) => setEmailContent(e.target.value)}
              ></textarea>
            </div>
            <button
              type="button"
              id="submitBtn"
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none"
              onClick={submitHandler}
              disabled={submitBtnDisabled}
            >
              Submit
            </button>
          </form>
        </div>

        {/* Right Side */}
        <div className="lg:flex-1 w-full">
          <h2 className="text-2xl font-bold mb-2 text-center lg:text-left text-green-500">Results</h2>
          <div
            id="results"
            className="bg-white p-4 border-4 border-green-500 rounded-lg h-96 overflow-scroll mx-4"
          ></div>

          {/* Feedback Buttons */}
          {feebackBtn && (
            <div className="mt-4">
              <div className="text-sm text-gray-600 text-center lg:text-left">
                Is the output correct?
              </div>
              <div className="flex justify-center lg:justify-between mt-2">
                <button
                  className="flex items-center justify-center bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-6 rounded"
                  onClick={setMyRedirect}
                >
                  No
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {Object.keys(emlData).length > 0 && (
        <div className="container mx-auto mt-8">
          <form onSubmit={updateJSONFormHandler}>
            <textarea
              name="instructionText"
              rows={5}
              placeholder="Enter the update instruction here"
              onChange={(e) => setUpdateJSONInput(e.target.value)}
              className="w-full p-4 border border-gray-300 rounded resize-none focus:outline-none"
            ></textarea>
            <button
              type="submit"
              className='bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-6 rounded mt-4'
            >
              Update JSON Result
            </button>
          </form>
        </div>
      )}
    </div>
</div>

  );
}

export default App;
