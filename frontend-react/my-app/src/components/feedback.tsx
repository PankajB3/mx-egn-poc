import { useNavigate, useLocation } from "react-router-dom"
// @ts-ignore
function Feedback() {
    const data = useLocation()
    const jsonData = data.state
    console.log("Feedback Component",data.state)    
    const navigate = useNavigate()
    // @ts-ignore
    const submitFeedbackForm = async (event) => {
        try{
            event.preventDefault()
            const formData = new FormData(event.target)
            const feedbackText = formData.get('feedbackText')
            const result = await fetch('http://34.70.229.241/api/feedback',
                {
                    method:'POST',
                    headers:{
                        'Content-Type':'application/json'
                    },
                    body: JSON.stringify(
                        {
                            jsonData,
                            feedbackText
                        }
                    )
                }
            )
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
            alert('An unexpected error occurred. Please try again later.');
        }finally{
            navigate('/');
        }
    }
  
    return (
      <div className="bg-gray-100 min-h-screen flex items-center justify-center">
        <div className="bg-white p-8 rounded shadow-md max-w-md w-full">
          <h1 className="text-3xl font-semibold mb-6">Feedback Form</h1>
          <form onSubmit={submitFeedbackForm}>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-600">Json Data</label>
              <input
                type="text"
                value={jsonData}
                readOnly
                className="mt-1 p-2 w-full border border-gray-300 rounded-md focus:outline-none focus:ring focus:border-blue-300"
              />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-600">Feedback</label>
              <textarea
                name="feedbackText"
                cols={13}
                rows={5}
                placeholder="Enter Your Feedback Here"
                className="mt-1 p-2 w-full border border-gray-300 rounded-md focus:outline-none focus:ring focus:border-blue-300"
              ></textarea>
            </div>
            <button
              type="submit"
              className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 focus:outline-none focus:ring focus:border-blue-300"
            >
              Submit
            </button>
          </form>
        </div>
      </div>
    );
  }
  
  export default Feedback;
  