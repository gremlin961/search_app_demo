# Copyright 2024 Google, LLC. This software is provided as-is,
# without warranty or representation for any use or purpose. Your
# use of it is subject to your agreement with Google.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
from google.cloud import aiplatform
from google.cloud import aiplatform_v1beta1 as vertex_ai
from typing import List
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1beta as discoveryengine



# Function for retrieving grounding data from Vertex AI Search Agent Builder
def search_sample(project_id, location, engine_id, search_query) -> List[discoveryengine.SearchResponse]:

    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )
    
    # Create a client
    client = discoveryengine.SearchServiceClient(client_options=client_options)
    
    # The full resource name of the search app serving config
    serving_config = f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{engine_id}/servingConfigs/default_config"
    
    
    content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
        # For information about snippets, refer to:
        # https://cloud.google.com/generative-ai-app-builder/docs/snippets
        snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
            return_snippet=True
            ),
        # For information about search summaries, refer to:
        # https://cloud.google.com/generative-ai-app-builder/docs/get-search-summaries
        summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
            summary_result_count=5,
            include_citations=True,
            ignore_adversarial_query=True,
            ignore_non_summary_seeking_query=True,
            model_prompt_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelPromptSpec(
                preamble=" "
            ),
            # Change the version to "stable" to use the GA version of the model
            model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
                version="gemini-1.0-pro-002/answer_gen/v1",
            ),
        ),
    )
    
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=search_query,
        #page_size=1,
        content_search_spec=content_search_spec,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )

    response = client.search(request)

    return response



# Function for calling the Gemini model
def gemini_text(project_id: str, location: str, prompt: str) -> str:
    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)
    # Load the model
    #multimodal_model = GenerativeModel("gemini-pro")
    multimodal_model = GenerativeModel("gemini-1.5-pro-preview-0409")
    # Query the model
    response = multimodal_model.generate_content(
        [
            #"what is shown in this image?",
            prompt,
        ]
    )
    #print(response)
    return response.text


# Function for calling the Gemini model
def gemini_chat(project_id: str, location: str, prompt: str) -> str:
    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)
    # Load the model
    #multimodal_model = GenerativeModel("gemini-pro")
    multimodal_model = GenerativeModel("gemini-1.5-pro-preview-0409")
    # Query the model
    chat = multimodal_model.start_chat()
    response = chat.send_message(
        prompt
    )
    #print(response)
    return response.text