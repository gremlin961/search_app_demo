from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Form, Depends
import uvicorn
import shutil
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import json
from pkg import vertexModels
from fastapi.staticfiles import StaticFiles
import yaml
from fastapi.security import HTTPBasic, HTTPBasicCredentials


app = FastAPI()

# Read the gcp_parameters file for related project information
with open("parameters.yaml", "r") as yamlfile:
    parameters = yaml.safe_load(yamlfile)

# Initialize the variables
project_id = parameters['PROJECT_ID']
location = parameters['LOCATION']
region = parameters['REGION']
engine_id = parameters['DENAME']

# Pull the username and password info for the web service from the gcp_parameters file
username = parameters['WEBUSER']
password = parameters['WEBPASS']

# Configure authentication for the web service and define the username and password
security = HTTPBasic()


# Specify the location for the Jinja templates
templates = Jinja2Templates(directory="templates")

# Specify the location for static files
app.mount("/static", StaticFiles(directory="static"), name="static")


persona = 'You are a marketing professional'
objective = 'Provide information about the customer base for the associated Hunting Ground' 
context = 'Any additional information'
output_format = 'Specify your preferred output format' 



@app.get("/")
def home(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != username or credentials.password != password:
        raise HTTPException(
            status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Basic"}
        )
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
  else: 
     search_query = "Tell me about the " + data["hunting_ground"] + " HG"
  search_results = vertexModels.search_sample(project_id, location, engine_id, search_query)
  grounding_data = search_results.summary.summary_text
  #grounding_data = grounding_data.replace("\n", "<br />")
  return grounding_data



@app.post("/generate")
async def generate(request: Request, hunting_ground: str = Form(...), grounding: str = Form(...), persona: str = Form(...), objective: str = Form(...), context: str = Form(...), output_format: str = Form(...)):
    
    # Initialize the variables
    #query = f"""Tell me about the {hunting_ground} HG"""

    
    #print(context)
    
    # Perform the search query
    #print('performing search query now')
    #search_results = vertexModels.search_sample(project_id, location, engine_id, query)

    #search_summary = search_results.summary.summary_text
    
    print(grounding)

    # Construct the prompt
    prompt = f"""**Hunting Ground:** {hunting_ground}

**Persona:** {persona}

**Objective:** {objective}

**Context:**
{context}

**Grounding Data:**
{grounding}

**Output Format:** {output_format}"""

    # Call the Gemini model
    response = vertexModels.gemini_text(project_id, region, prompt)

    # Post-process the response to add new lines
    response = response.replace("\n", "<br>")

    # Render the results page
    return templates.TemplateResponse("index.html", {"request": request, "grounding":grounding, "persona": persona, "objective": objective, "context": context, "output_format": output_format, "hunting_ground": hunting_ground, "response": response})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)