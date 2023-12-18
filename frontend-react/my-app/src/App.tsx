import React from 'react';
import './App.css';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';


function App() {

    const [emlData, setEmlData] = useState({})
    const [submitBtnDisabled, setSubmitBtnDisable] = useState(false)
    const [feebackBtn, setFeedbackBtn] = useState(false)
    const [emailContent, setEmailContent] = useState("")
    const [updateJSONInput, setUpdateJSONInput] = useState("")

    const navigate = useNavigate()

    // @ts-ignore
    const setMyRedirect = async() => {
      // const data = JSON.parse(emailContent)
      // let feedBackData = data?.Messages?.[0]?.Blurb || "No Messages Found In The Uploaded JSON"
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
     
     var submitBtn = document.getElementById('submitBtn');

     //@ts-ignore
     // Check if a file is selected
    //  if (fileInput.files.length === 0) {
    //      alert('Please select an EML file before submitting.');
    //      return;
    //  }

     //@ts-ignore
     // Disable the submit button
     submitBtn.disabled = true;

     //@ts-ignore
     // Get the selected file name
    //  var fileName = fileInput.files[0].name;

     // Create FormData object to send the file to the server
     var formData = new FormData();
     //@ts-ignore
     formData.append('email_conversation',emailContent);

    console.log(formData)

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
        // setFileName("");
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
  // const fileChangeHandler = (e) => {
  //   // console.log("File Change Handler", e.target.files[0].name);
    
  //   if(e.target.files.length > 0) {
  //       // console.log("File Change Handler", e.target.files[0].name);
  //       setFileName(e.target.files[0].name)
  //       setSubmitBtnDisable(false)
  //   }
  // }

    //@ts-ignore
  const updateJSONFormHandler = async(event) => {
    try{
      event.preventDefault()
      
      // @ts-ignore
      document.getElementById('results').innerText = "We Are Updating JSON As Per Instructions Please Wait..."
      const result = await fetch('http://34.70.229.241/api/update_json', {
        method:'POST',
        headers:{
          'Content-Type':'application/json'
      },
        body:JSON.stringify({updateJSONInput, emlData})
      })
      const data = await result.json()
      if(result.ok){
        // @ts-ignore
        document.getElementById('results').innerText = data.message
        setEmlData(data.message)
        // @ts-ignore
        document.getElementsByName('instructionText').value = ''
      }else{
        alert("Error In Updating JSON")
      }
    }catch(err){
      alert(`Error : ${err}`)
    }
  }


  return (
<div className="App">
  <div className="container mx-auto p-4 flex flex-col items-center justify-center min-h-screen">
    <div className="lg:flex flex-col lg:flex-row gap-4 w-full">
      {/* Left Side with Heading */}
      <div className="lg:flex-1 w-full mb-8 lg:mb-0">
        <h1 className="text-3xl font-bold mb-8 lg:mb-0 text-center lg:text-left">EML Analyzer</h1>
        <form id="uploadForm" encType="multipart/form-data">
          <div className="border-dotted border-4 border-blue-500 overflow-scroll mb-4">
            <textarea
              name="email"
              cols={47}
              rows={15}
              placeholder='Paste Your JSON Here'
              className="w-full p-2"
              onChange={(e) => setEmailContent(e.target.value)}
            ></textarea>
          </div>
          <button
            type="button"
            id="submitBtn"
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            onClick={submitHandler}
            disabled={submitBtnDisabled}
          >
            Submit
          </button>
        </form>
      </div>

      {/* Right Side */}
      <div className="lg:flex-1 w-full">
        <h2 className="text-2xl font-bold mb-2 text-center lg:text-left">Results</h2>
        <div id="results" className="bg-white p-4 border-4 border-green-500 rounded-lg h-96 overflow-scroll"></div>

        {/* Feedback Buttons */}
        {feebackBtn && (
          <div>
            <div className="text-sm text-gray-600 mt-2 text-center lg:text-left">Is the output correct?</div>
            <div className="flex justify-center lg:justify-between mt-4">
              <button
                className="flex items-center justify-center bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-6 rounded"
                onClick={saveEmlDataToDB}
              >
                <span>Yes</span>
              </button>
              <button
                className="flex items-center justify-center bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-6 rounded"
                onClick={setMyRedirect}
              >
                <span>No</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
    
    {Object.keys(emlData).length > 0 && (
      <div className="mt-8">
        <form onSubmit={updateJSONFormHandler}>
          <textarea
            name="instructionText"
            rows={5}
            cols={40}
            placeholder='Enter the update instruction here'
            onChange={(e) => setUpdateJSONInput(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
          ></textarea>
          <button type="submit" className='bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-6 rounded mt-4'>
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
