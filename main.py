from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Form, Depends
import uvicorn
import base64
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import json
from pkg import vertexModels
from fastapi.staticfiles import StaticFiles
import yaml
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import markdown
import asyncio



import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part, Tool, grounding
from google.cloud import aiplatform
from google.cloud import aiplatform_v1beta1 as vertex_ai
from typing import List
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1beta as discoveryengine


app = FastAPI()

# Read the gcp_parameters file for related project information
with open("parameters.yaml", "r") as yamlfile:
    parameters = yaml.safe_load(yamlfile)

# Initialize the variables
project_id = parameters['PROJECT_ID']
location = parameters['LOCATION']
region = parameters['REGION']
data_store_id = parameters['DSNAME']
engine_id = parameters['DENAME']

# ---- Uncomment the lines below to use basic authentication if needed. Also see the @app.get("/") section
# Pull the username and password info for the web service from the gcp_parameters file
#username = parameters['WEBUSER']
#password = parameters['WEBPASS']
# Configure authentication for the web service and define the username and password
#security = HTTPBasic()


# Specify the location for the Jinja templates
templates = Jinja2Templates(directory="templates")

# Specify the location for static files
app.mount("/static", StaticFiles(directory="static"), name="static")




persona = 'You are a Google Cloud Customer Engineer on the account team'
objective = 'Provide information about the associated account' 
context = ' '
output_format = 'This is a business conversation. Make sure to provide the reasoning for your response.' 




vertexai.init(project=project_id, location=region)
chat_model = GenerativeModel("gemini-1.5-pro-preview-0409")
chat = chat_model.start_chat()




def get_mime_type(file_extension):
  """Returns the MIME type based on the file extension.

  Args:
    file_extension: The file extension (e.g., "pdf", "mp3", "jpg").

  Returns:
    The MIME type as a string, or None if the extension is not recognized.
  """

  mime_types = {
    "pdf": "application/pdf",
    "mpeg": "audio/mpeg",
    "mp3": "audio/mpeg", # mp3 is technically a subset of MPEG
    "wav": "audio/wav",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "txt": "text/plain",
    "mov": "video/mov",
    "mp4": "video/mp4",
    "mpg": "video/mpeg",
    "avi": "video/avi",
    "wmv": "video/wmv",
    "mpegps": "video/mpegps", 
    "flv": "video/flv",
  }

  return mime_types.get(file_extension.lower(), None)







@app.get("/")
# --- Uncomment the below lines and comment out the following def statement to enable basic security
#def home(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
#    if credentials.username != username or credentials.password != password:
#        raise HTTPException(
#            status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Basic"}
#        )
def home(request: Request):
    hunting_grounds = [
        "Scheduled Reset",
        "Fully Unplug",
        "Needed Fun",
        "Keep Me Going"
    ]
    return templates.TemplateResponse("index.html", {"request": request, "persona": persona, "objective": objective, "context": context, "output_format": output_format, "hunting_grounds": hunting_grounds})




@app.post("/load_search_results")
async def load_search_results(request: Request):
  print("Generating grounding data from document search...")
  data = await request.json()
  if (data["hunting_ground"] == 'Custom'):
     search_query = data["custom_query"]
  elif (data["hunting_ground"] == 'VAIS'):
      print("Converting to VAIS search")
  else: 
     search_query = "Tell me about the " + data["hunting_ground"] + " HG"
  search_results = vertexModels.search_sample(project_id, location, engine_id, search_query)
  grounding_data = search_results.summary.summary_text
  grounding_data = markdown.markdown(grounding_data)
  print(grounding_data)
  return str(grounding_data)

@app.post("/load_gemini_response")
async def load_gemini_response(request: Request):
    data = await request.json()
    if (data["hunting_ground"] == 'VAIS'):
        # Set the global variable for chat_model to include the VAIS data store
        global chat_model, chat
        tools = [
        Tool.from_retrieval(
                retrieval=grounding.Retrieval(
                    source=grounding.VertexAISearch(datastore=f"projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{data_store_id}"),
                    disable_attribution=False,
                )
            ),
        ]
        print("Setting the grounding data")
        chat_model = GenerativeModel("gemini-1.5-pro-preview-0409", tools=tools,)
        chat = chat_model.start_chat()

    print("Generating Gemini Response...")
    data = await request.json()
    
    prompt = f"""
<Grounding Data>
{data["grounding"]}

<Persona>
{data["persona"]}

<Objective>
{data["objective"]}

<context>
{data["context"]}

<Output Format>
{data["output_format"]}

<START ANALYSIS>
If you understand, start with a greeting and ask me for my goals.
"""



    print(prompt)
    #gemini_results = vertexModels.gemini_chat(project_id, region, prompt)

    async def chat_stream():
        for chunk in chat._send_message_streaming(prompt):
        #async for chunk in anyio.to_async_iterable(chat._send_message_streaming(prompt)):
            if chunk.text:
                # Use a generator to yield content as it's received
                gemini_response = chunk.text
                print(gemini_response)
                yield gemini_response
                #yield chunk.text
                await asyncio.sleep(0.01) # Introduce a small delay 

    return StreamingResponse(chat_stream(), media_type="text/html")  



@app.post("/load_gemini_follow-up")
async def load_gemini_follow_up(request: Request):
    print("Generating Gemini Response...")
    data = await request.json()

    print(data)
    prompt = f"""{data["followupprompt"]}"""

    print(prompt)
    #gemini_results = vertexModels.gemini_chat(project_id, region, prompt)
    async def chat_stream():
        for chunk in chat._send_message_streaming(prompt):
            if chunk.text:
                gemini_response = chunk.text
                print(gemini_response)
                yield gemini_response
                #yield chunk.text
                await asyncio.sleep(0.01) # Introduce a small delay

    return StreamingResponse(chat_stream(), media_type="text/html") 

# Process file uploads
@app.post("/upload")
async def upload_file(files: List[UploadFile] = File(...)):
    encoded_files = []
    for file in files:
        file_extension = file.filename.split(".")[-1]
        print(f"File extension: {file_extension}")
        mimeType = get_mime_type(file_extension)
        if mimeType == None:
            mimeType = ('Unknown')
        print('The mime type for this file is ' + mimeType)
        contents = await file.read()
        encoded_file = base64.b64encode(contents).decode("utf-8")
        file_content = Part.from_data(data=base64.b64decode(encoded_file), mime_type=mimeType)
        prompt = "Add this document to your context. If you are able to process it, provide a simple response that it was successfully uploaded"
        gemini_results = chat.send_message([file_content, prompt])
        gemini_results = markdown.markdown(gemini_results.text)
        #print(gemini_results)
    return gemini_results
    #return {"filenames": [file.filename for file in files]}







if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)