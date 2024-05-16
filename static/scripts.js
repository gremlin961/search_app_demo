import * as smd from '/static/smd.js'; 


document.getElementById("load-button").addEventListener("click", function () {
  // Show the loading screen
  document.getElementById("loading-screen").style.display = "block";

  // Make AJAX call to load search results
  fetch("/load_search_results", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      hunting_ground: document.getElementById("hunting_ground").value,
      custom_query: document.getElementById("custom_query").value,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      // Hide the loading screen
      document.getElementById("loading-screen").style.display = "none";
      // Replace \n characters with actual line breaks
      data = data.replace(/\\n/g, "\n");
      //console.log(data);
      // Update the search-results textarea with the response
      document.getElementById("grounding").innerHTML = data;
    });
});


document.getElementById("generate").addEventListener("click", function () {
  // Show the loading screen
  document.getElementById("loading-screen").style.display = "block";
  // Set the variable for the parent div
  const resultContainer = document.getElementById("generated_result");

  // Make AJAX call to load search results
  fetch("/load_gemini_response", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      hunting_ground: document.getElementById("hunting_ground").value,
      persona: document.getElementById("persona").value,
      objective: document.getElementById("objective").value,
      context: document.getElementById("context").value,
      grounding: document.getElementById("grounding").innerText,
      output_format: document.getElementById("output_format").value,
    }),
  })
    .then((response) => {
      const reader = response.body.getReader();
      const chunkDiv = document.createElement('div');
      chunkDiv.id = 'gemini';
      resultContainer.appendChild(chunkDiv);

      const renderer = smd.default_renderer(chunkDiv);
      const parser = smd.parser(renderer)

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
              // Convert Uint8Array to string, decode and display
              const textDecoder = new TextDecoder("utf-8");
              const chunk = textDecoder.decode(value);
              
              // **Append the chunk directly to the container**
              smd.parser_write(parser, chunk)
              // Immediately call push() to process the next chunk
              push(); 
            });
          }
          push();
        },
      });
    })
    .then((stream) => {
      // Hide the loading screen
      document.getElementById("loading-screen").style.display = "none";
      // Show the form with results
      document.getElementById("results_form").style.display = "block";
    });
});

document.getElementById("follow-up").addEventListener("click", function () {
  // Update the search-results textarea with the response
  document.getElementById("generated_result").innerHTML +=
    '<div id="user">' +
    document.getElementById("follow-up-prompt").value +
    "</div>";
  const userPrompt = document.getElementById("follow-up-prompt").value;
  // Clear the follow-up-prompt text area
  document.getElementById("follow-up-prompt").value = "";

  const resultContainer = document.getElementById("generated_result");

  // Make AJAX call to load search results
  fetch("/load_gemini_follow-up", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      followupprompt: userPrompt,
    }),
  })
    .then((response) => {
      const reader = response.body.getReader();
      const chunkDiv = document.createElement('div');
      chunkDiv.id = 'gemini';
      resultContainer.appendChild(chunkDiv);

      const renderer = smd.default_renderer(chunkDiv);
      const parser = smd.parser(renderer)

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
              // Convert Uint8Array to string, decode and display
              const textDecoder = new TextDecoder("utf-8");
              const chunk = textDecoder.decode(value);

              //console.log(chunk_html)

              // **Append the chunk directly to the container**
              smd.parser_write(parser, chunk)

              // Immediately call push() to process the next chunk
              push();
            });
          }
          push();
        },
      });
    })
    .then((stream) => {
      // Show the form with results
      document.getElementById("results_form").style.display = "block";
    });
});

document.getElementById("follow-up-prompt").addEventListener("keypress", function(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    document.getElementById("follow-up").click();
  };
});

// Add event listener for the dropdown selection change
document.getElementById("hunting_ground").addEventListener("change", function () {
  // Check if "custom" is selected
  if (this.value === "Custom") {
    //console.log(this.value);
    // Show the custom query textarea and label
    document.getElementById("grounding_label").style.display = "block";
    document.getElementById("grounding").style.display = "block";
    document.getElementById("load-button").style.display = "block";
    document.getElementById("custom_query_label").style.display = "block";
    document.getElementById("custom_query").style.display = "block";
  } else if (this.value === "VAIS") {
    //console.log(this.value);
    // Hide the custom query textarea and label
    document.getElementById("grounding_label").style.display = "none";
    document.getElementById("grounding").style.display = "none";
    document.getElementById("load-button").style.display = "none";
    document.getElementById("custom_query_label").style.display = "none";
    document.getElementById("custom_query").style.display = "none";
  } else {
    //console.log(this.value);
    // Hide the custom query textarea and label
    document.getElementById("grounding_label").style.display = "block";
    document.getElementById("grounding").style.display = "block";
    document.getElementById("load-button").style.display = "block";
    document.getElementById("custom_query_label").style.display = "none";
    document.getElementById("custom_query").style.display = "none";
  }
});

document.getElementById("upload_button").addEventListener("click", function () {
  const fileInput = document.getElementById("fileInput");
  const files = fileInput.files;

  if (files.length > 0) {
    // Show the loading screen
    document.getElementById("loading-screen").style.display = "block";
    const formData = new FormData();

    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i]);
    }

    fetch("/upload", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        // Hide the loading screen
        document.getElementById("loading-screen").style.display = "none";
        document.getElementById("generated_result").innerHTML +=
          '<div id="gemini">' + data + "</div>";
        //console.log(data);
      });
  }
});