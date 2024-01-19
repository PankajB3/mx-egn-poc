import { useNavigate, useLocation } from "react-router-dom"
// Functional component for the Feedback form
// @ts-ignore
function Feedback() {
  // Extract data from the location object using useLocation hook
    const data = useLocation()
    // Access JSON data from the state
    const jsonData = data.state
    // Access the navigation function for redirecting
    const navigate = useNavigate()

    // Function to handle the submission of the feedback form
    // @ts-ignore
    const submitFeedbackForm = async (event) => {
        try{
          // Prevent the default form submission behavior
            event.preventDefault()
            // Create a FormData object from the form data
            const formData = new FormData(event.target)
            // Extract feedback text from the form data
            const feedbackText = formData.get('feedbackText')
            // Make a POST request to the feedback API endpoint
            const result = await fetch('http://34.70.229.241/api/feedback',
                {
                    method:'POST',
                    headers:{
                        'Content-Type':'application/json'
                    },
                     // Convert feedback data to JSON and send it in the request body
                    body: JSON.stringify(
                        {
                            jsonData,
                            feedbackText
                        }
                    )
                }
            )
            // Check if the request was successful
            if(result.ok){
                // Display success alert
                alert('Feedback submitted successfully!');
    
                // Redirect to the home route
                navigate('/');
            }else {
                alert("Error In Submitting Feedback, Try Again")
                // Redirect to the home route
                navigate('/');
            }
        }catch(err){
          // Display a generic error message in case of unexpected errors
            alert('An unexpected error occurred. Please try again later.');
        }finally{
          // Ensure navigation happens even in case of errors
            navigate('/');
        }
    }

    // Return JSX for the Feedback component
    return (
      <div className="bg-gray-100 min-h-screen flex items-center justify-center">
  <div className="bg-white p-8 rounded shadow-md max-w-md w-full">
    <h1 className="text-4xl font-extrabold text-center text-gray-800 mb-8">Feedback Form</h1>
    <form onSubmit={submitFeedbackForm} className="space-y-4">
      <div className="mb-4">
        <label htmlFor="jsonData" className="block text-sm font-medium text-gray-600">
          JSON Data
        </label>
        <input
          id="jsonData"
          type="text"
          value={jsonData}
          readOnly
          className="mt-1 p-2 w-full border border-gray-300 rounded-md focus:outline-none focus:ring focus:border-blue-300"
        />
      </div>
      <div className="mb-4">
        <label htmlFor="feedbackText" className="block text-sm font-medium text-gray-600">
          Feedback
        </label>
        <textarea
          id="feedbackText"
          name="feedbackText"
          placeholder="Enter Your Feedback Here"
          className="mt-1 p-2 w-full border border-gray-300 rounded-md focus:outline-none focus:ring focus:border-blue-300"
          rows={5}
        ></textarea>
      </div>
      <button
        type="submit"
        className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 focus:outline-none focus:ring focus:border-blue-300 w-full"
      >
        Submit
      </button>
    </form>
  </div>
</div>
    );
  }
  
  export default Feedback;
  