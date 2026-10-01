import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import json
import ast
import re
from neo4j import GraphDatabase

load_dotenv()

AZURE_OPENAI_API_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

URI = os.getenv("NEO4J_URL")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE")

if not all([AZURE_OPENAI_API_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_DEPLOYMENT_NAME]):
    raise ValueError("One or more Azure OpenAI environment variables are not set.")

if not all([URI, USERNAME, PASSWORD, DATABASE]):
    raise ValueError("One or more Neo4j environment variables are not set.")

client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_API_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION
)

with GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD)) as driver:
    driver.verify_connectivity()
    print("Connected to Neo4j database:", DATABASE)

def extract_entities_and_relations(doc):
    prompt = f"""
    You are an information extraction system that extracts entities and relationships
    from unstructured text for building a Neo4j Knowledge Graph.
    
    Your task is to analyze the provided text and return structured JSON containing:
    
    1. Entities
    2. Relationships between entities
    
    ## Entity Extraction Rules
    
    - Extract only meaningful entities that appear explicitly in the text.
    - Do not invent entities that are not supported by the text.
    - Merge duplicate entities that refer to the same real-world object.
    - Use the most complete and canonical name available in the text.
    - Assign each entity a type.
    
    Recommended entity types include:
    - Person
    - Organization
    - Location
    - Product
    - Technology
    - Event
    - Concept
    - Document
    - Service
    - Other
    
    ## Relationship Extraction Rules
    
    - Extract meaningful relationships between entities.
    - Each relationship must connect two entities listed in the "entities" array.
    - Use short and clear relationship names.
    - Relationship names should be written in UPPER_SNAKE_CASE.
    - Avoid vague relationships such as "related_to" unless no more specific relationship can be inferred.
    - Do not create relationships that are not supported by the text.
    - Remove duplicate relationships.
    
    Examples of good relationship names:
    - WORKS_FOR
    - LOCATED_IN
    - DEVELOPED_BY
    - USES
    - PART_OF
    - CREATED_BY
    - DEPENDS_ON
    - SUPPORTS
    - BELONGS_TO
    - CONNECTED_TO
    
    ## Output Requirements
    
    Return ONLY valid JSON.
    
    Do not include:
    - Markdown
    - Code fences
    - Explanations
    - Comments
    - Additional text
    
    Use exactly the following JSON structure:
    
    {{
      "entities": [
        {{
          "id": "entity_1",
          "name": "Entity Name",
          "type": "EntityType"
        }},
        {{
          "id": "entity_2",
          "name": "Another Entity",
          "type": "EntityType"
        }}
      ],
      "relations": [
        {{
          "subject": "entity_1",
          "relation": "RELATIONSHIP_TYPE",
          "object": "entity_2"
        }}
      ]
    }}
    
    Important constraints:
    
    - Every "subject" and "object" must reference an existing entity "id".
    - Entity IDs must be unique.
    - Do not create duplicate entities.
    - Do not create duplicate relationships.
    - Preserve the original language of entity names.
    - Relationship types must always be in English and UPPER_SNAKE_CASE.
    - If no entities are found, return an empty "entities" array.
    - If no relationships are found, return an empty "relations" array.
    
    Text:
    {doc}
    """

    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT_NAME,
        

    )