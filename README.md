## Search App Demo with Gemini Pro and Vertex AI Search

This demo application showcases the power of large language models (LLMs) combined with the enterprise-grade capabilities of Vertex AI Search. Built with FastAPI, it delivers a user-friendly interface for exploring the possibilities of grounded conversations.

**Key Features:**

* **Grounding with Vertex AI Search:** Leverage relevant information retrieved from your Vertex AI Search data store to ground LLM responses, ensuring contextually accurate and informative conversations. 
* **Customizable Persona and Objective:** Tailor the LLM's persona and objective to match specific conversational scenarios, from customer support to technical consulting.
* **Streaming Response:** Experience the immediacy of streaming responses, witnessing the LLM's thought process unfold in real-time. 
* **Document Upload and Integration:** Enhance conversational context by uploading documents and allowing the LLM to dynamically incorporate them into its understanding.

### Prerequisites

* **Google Cloud Project:** Ensure you have a Google Cloud project set up. If not, create one on the [Google Cloud Console](https://console.cloud.google.com).
* **Vertex AI Search Engine:** Create a Vertex AI Search engine within your project. Follow the [Vertex AI Search documentation](https://cloud.google.com/generative-ai-app-builder/docs/create-search-engine) for guidance.

### Configuration

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/search-app-demo.git
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Update parameters.yaml:**
   Open the `parameters.yaml` file and replace the placeholders with your specific GCP project details:
   ```yaml
   PROJECT_ID: Your GCP Project ID
   LOCATION: Your project resource location, such as us or global
   REGION: Your project resource region, such as us-central1 or us-east4
   DSNAME: Your Vertex AI Search Data Store ID
   DENAME: Your Vertex AI Search App ID
   ```

### Running Locally

1. **Start the FastAPI Application:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080 --reload
   ```
2. **Access the Demo:**
   Open a web browser and navigate to `http://127.0.0.1:8080`.

**Explore and Experiment:**

* **Select Grounding Queries:** Choose from predefined search queries to retrieve relevant grounding information from your Vertex AI Search data store.
* **Customize Persona and Objective:** Modify the persona and objective to tailor the LLM's behavior to your specific needs.
* **Initiate the Chat:** Click "Start Chat" to begin a grounded conversation.
* **Provide Follow-up Prompts:** Guide the conversation with follow-up prompts and observe how the LLM integrates context from the retrieved grounding information.
* **Upload Documents:** Upload documents to enrich the conversational context. 
* **Analyze Streaming Responses:** Pay attention to the unfolding response, gaining insights into the LLM's reasoning process. 