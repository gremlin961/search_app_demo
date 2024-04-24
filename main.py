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
import markdown


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
  grounding_data = markdown.markdown(grounding_data)
  return grounding_data

@app.post("/load_gemini_response")
async def load_gemini_response(request: Request):
    print("Generating Gemini Response...")
    data = await request.json()
    if (data["hunting_ground"] == 'Custom'):
        search_query = data["custom_query"]
    else: 
        search_query = "Tell me about the " + data["hunting_ground"] + " HG"
    
    prompt = f"""<Hunting Ground> {data["hunting_ground"]}

<Persona>
{data["persona"]}

<Objective>
{data["objective"]}

<context>
{data["context"]}

<Grounding Data>
{data["grounding"]}

<Output Format>
{data["output_format"]}"""

    #print(prompt)
    gemini_results = vertexModels.gemini_text(project_id, region, prompt)
    gemini_results = markdown.markdown(gemini_results)
    #print(gemini_results)
    return gemini_results


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)