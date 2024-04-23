document.getElementById("load-button").addEventListener("click", function() {
  // Show the loading screen
  document.getElementById("loading-screen").style.display = "block";

  // Make AJAX call to load search results
  fetch("/load_search_results", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      hunting_ground: document.getElementById("hunting_ground").value,
      custom_query: document.getElementById("custom_query").value
    })
  })
  .then(response => response.text())
  .then(data => {
      // Hide the loading screen
      document.getElementById("loading-screen").style.display = "none";
      // Replace \n characters with actual line breaks
      data = data.replace(/\\n/g, "\n");
      // Update the search-results textarea with the response
      document.getElementById("grounding").value = data;
  });
});




document.getElementById("generate").addEventListener("click", function() {
// Show the loading screen
document.getElementById("loading-screen").style.display = "block";

// Make AJAX call to load search results
fetch("/load_gemini_response", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    hunting_ground: document.getElementById("hunting_ground").value,
    persona: document.getElementById("persona").value,
    objective: document.getElementById("objective").value,
    context: document.getElementById("context").value,
    grounding: document.getElementById("grounding").value,
    output_format: document.getElementById("output_format").value
  })
})
.then(response => response.text())
.then(data => {
    // Hide the loading screen
    document.getElementById("loading-screen").style.display = "none";
    // Replace \n characters with actual line breaks
    data = data.replace(/\\n/g, "\n");
    // Update the search-results textarea with the response
    //document.getElementById("generated_result").value = data;
    document.getElementById("generated_result").innerHTML = data;
    // Show the form with results
    document.getElementById("results_form").style.display = "block";
});
});




// Add event listener for the dropdown selection change
document.getElementById("hunting_ground").addEventListener("change", function() {
// Check if "custom" is selected
if (this.value === "Custom") {
  // Show the custom query textarea and label
  document.getElementById("custom_query_label").style.display = "block";
  document.getElementById("custom_query").style.display = "block";
} else {
  // Hide the custom query textarea and label
  document.getElementById("custom_query_label").style.display = "none";
  document.getElementById("custom_query").style.display = "none";
}
});