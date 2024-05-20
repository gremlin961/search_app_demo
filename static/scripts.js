// Import the Streaming Markdown parser module
import * as smd from '/static/smd.js'; 

// Add an event listener to the "Load" button
document.getElementById("load-button").addEventListener("click", function () {
  // Show the loading screen while fetching data
  document.getElementById("loading-screen").style.display = "block";

  // Prepare data to send in the AJAX request
  const requestData = {
    vais_search_query: document.getElementById("vais_search_query").value, // Get the selected vais search query
    custom_query: document.getElementById("custom_query").value   // Get the custom query (if applicable)
  };

  // Make an AJAX call to the '/load_search_results' endpoint
  fetch("/load_search_results", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(requestData) 
  })
    .then((response) => response.json())
    .then((data) => {
      // Hide the loading screen after data is fetched
      document.getElementById("loading-screen").style.display = "none";
      
      // Replace escaped newline characters with actual line breaks for display
      data = data.replace(/\\n/g, "\n");
      
      // Update the "grounding" div with the received data
      document.getElementById("grounding").innerHTML = data;
    });
});


// Add an event listener to the "Start Chat" button
document.getElementById("generate").addEventListener("click", function () {
  // Show the loading screen while fetching the response
  document.getElementById("loading-screen").style.display = "block";

  // Get the container where chat results will be displayed
  const resultContainer = document.getElementById("generated_result");

  // Prepare data to send in the AJAX request
  const requestData = {
    vais_search_query: document.getElementById("vais_search_query").value,  // Get the selected vais search query
    persona: document.getElementById("persona").value,              // Get the defined persona
    objective: document.getElementById("objective").value,            // Get the conversation objective
    context: document.getElementById("context").value,                // Get additional context information
    grounding: document.getElementById("grounding").innerText,        // Get the grounding data
    output_format: document.getElementById("output_format").value     // Get the desired output format
  };

  // Make an AJAX call to the '/load_gemini_response' endpoint
  fetch("/load_gemini_response", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(requestData)
  })
    .then((response) => {
      // Get a reader for the streaming response body
      const reader = response.body.getReader();

      // Create a div to hold the streamed chat content
      const chunkDiv = document.createElement('div');
      chunkDiv.id = 'gemini';
      resultContainer.appendChild(chunkDiv);

      // Initialize the Streaming Markdown renderer and parser
      const renderer = smd.default_renderer(chunkDiv);
      const parser = smd.parser(renderer)

      // Create a ReadableStream to handle the streamed response
      return new ReadableStream({
        start(controller) {
          function push() {
            reader.read().then(({ done, value }) => {
              if (done) {
                // Close the stream when done
                controller.close();
                smd.parser_end(parser)
                return;
              }
              // Enqueue the received chunk for processing
              controller.enqueue(value);
              
              // Decode the chunk (which is a Uint8Array) to a string
              const textDecoder = new TextDecoder("utf-8");
              const chunk = textDecoder.decode(value);

              // Write the decoded chunk to the Streaming Markdown parser
              smd.parser_write(parser, chunk)

              // Immediately process the next chunk
              push(); 
            });
          }
          push();
        },
      });
    })
    .then((stream) => {
      // Hide the loading screen once the response stream is established
      document.getElementById("loading-screen").style.display = "none";
      // Show the results form 
      document.getElementById("results_form").style.display = "block";
    });
});


// Add an event listener to the "Send" button (for follow-up prompts)
document.getElementById("follow-up").addEventListener("click", function () {
  // Get the user's follow-up prompt
  const userPrompt = document.getElementById("follow-up-prompt").value;
  
  // Append the user prompt to the results area
  document.getElementById("generated_result").innerHTML +=
    '<div id="user">' + userPrompt + "</div>";
  
  // Clear the follow-up prompt input area
  document.getElementById("follow-up-prompt").value = "";

  // Get the container for chat results
  const resultContainer = document.getElementById("generated_result");

  // Make an AJAX call to the '/load_gemini_follow-up' endpoint
  fetch("/load_gemini_follow-up", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ followupprompt: userPrompt }) // Send the follow-up prompt
  })
    .then((response) => {
      const reader = response.body.getReader();
      
      // Create a div to hold the streamed response content
      const chunkDiv = document.createElement('div');
      chunkDiv.id = 'gemini';
      resultContainer.appendChild(chunkDiv);

      // Initialize the Streaming Markdown renderer and parser
      const renderer = smd.default_renderer(chunkDiv);
      const parser = smd.parser(renderer)

      // Create a ReadableStream to handle the streamed response
      return new ReadableStream({
        start(controller) {
          function push() {
            reader.read().then(({ done, value }) => {
              if (done) {
                controller.close();
                smd.parser_end(parser)
                return;
              }
              controller.enqueue(value);
              // Decode the received chunk from Uint8Array to a string
              const textDecoder = new TextDecoder("utf-8");
              const chunk = textDecoder.decode(value);

              // Write the decoded chunk to the Streaming Markdown parser
              smd.parser_write(parser, chunk)

              // Process the next chunk
              push();
            });
          }
          push();
        },
      });
    })
    .then((stream) => {
      // Ensure the results form is visible
      document.getElementById("results_form").style.display = "block";
    });
});

// Allow pressing "Enter" in the follow-up prompt to send the prompt
document.getElementById("follow-up-prompt").addEventListener("keypress", function(event) {
  if (event.key === "Enter") {
    event.preventDefault(); // Prevent default form submission
    document.getElementById("follow-up").click(); // Trigger the 'Send' button click
  };
});

// Add an event listener to the vais search query dropdown
document.getElementById("vais_search_query").addEventListener("change", function () {
  // Show/hide elements based on the selected vais search query 
  if (this.value === "Custom") {
    // If 'Custom' is selected, show the custom query textarea and related elements
    document.getElementById("grounding_label").style.display = "block";
    document.getElementById("grounding").style.display = "block";
    document.getElementById("load-button").style.display = "block";
    document.getElementById("custom_query_label").style.display = "block";
    document.getElementById("custom_query").style.display = "block";
  } else if (this.value === "VAIS") {
    // If 'VAIS' is selected, hide the custom query elements
    document.getElementById("grounding_label").style.display = "none";
    document.getElementById("grounding").style.display = "none";
    document.getElementById("load-button").style.display = "none";
    document.getElementById("custom_query_label").style.display = "none";
    document.getElementById("custom_query").style.display = "none";
  } else {
    // For other vais search queries, show the grounding area but hide custom query elements
    document.getElementById("grounding_label").style.display = "block";
    document.getElementById("grounding").style.display = "block";
    document.getElementById("load-button").style.display = "block";
    document.getElementById("custom_query_label").style.display = "none";
    document.getElementById("custom_query").style.display = "none";
  }
});


// Add an event listener for file uploads
// Add an event listener for file uploads
document.getElementById("fileInput").addEventListener("change", function () { // Changed from 'click' on 'upload_button' to 'change' on 'fileInput'
  const fileInput = document.getElementById("fileInput");
  const files = fileInput.files;

  // Proceed only if files are selected
  if (files.length > 0) {
    
    // Show the loading screen while uploading
    document.getElementById("loading-screen").style.display = "block";

    // Create a FormData object to send the files
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i]);
    }

    // Make an AJAX request to the '/upload' endpoint to handle file upload
    fetch("/upload", {
      method: "POST",
      body: formData
    })
      .then((response) => {
        if (!response.ok) { 
          return response.text().then(data => { throw new Error(data.error); }); 
        }
        
        return response.json(); // Assuming the success response is plain text
        
      })
      .then((data) => {
        // Hide the loading screen after upload is complete
        document.getElementById("loading-screen").style.display = "none";
        
        // Append the response (likely a confirmation message) to the results area
        document.getElementById("generated_result").innerHTML +=
          '<div id="gemini">' + data + "</div>"; 
      })
      .catch(error => {
          // Handle the error
          alert(error.message); 
          // Hide the loading screen if there's an error
          document.getElementById("loading-screen").style.display = "none";
      });
  }
});