from google import genai
from google.genai import types

from dotenv import load_dotenv
import os
import time
import argparse


"""
Rate limits of compatible models (Free Teir RPD):

gemini-3.1-pro-preview          0
gemini-3.1-flash-lite-preview   500
gemini-3-flash-preview          20
gemini-2.5-pro                  0
gemini-2.5-flash-lite           20
"""

# Load necessary env vars
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY == None:
    raise ValueError("Environment variable GEMINI_API_KEY not specified!")

# Specific store for project
STORE_NAME = "Islamic-Law-Sources"

def check_file_info(client, file_name: str) -> bool:
    """
    Returns True if the file exists in the store, false otherwise.
    """
    # Find the store first
    stores = client.file_search_stores.list()
    target_store = next((s for s in stores if s.display_name == STORE_NAME), None)
    
    if not target_store:
        print(f"Store '{STORE_NAME}' not found.")
        return False

    # List documents in that store
    documents = client.file_search_stores.documents.list(parent=target_store.name)
    
    for doc in documents:
        if doc.display_name == file_name:
            print(f"--- File Found: {file_name} ---")
            print(f"Internal ID: {doc.name}")
            print(f"Uploaded At: {doc.create_time}")
            return True
            
    print(f"File '{file_name}' not found in the store.")
    return False

def upload_to_store(client, file_path: str):
    if check_file_info(client, os.path.basename(file_path)):
        print("File already exists in store! Skipping upload.")
        return

    # Find or Create the store
    stores = client.file_search_stores.list()
    target_store = next((s for s in stores if s.display_name == STORE_NAME), None)
    
    if not target_store:
        target_store = client.file_search_stores.create(config={'display_name': STORE_NAME})

    print(f"Uploading {file_path}...")
    operation = client.file_search_stores.upload_to_file_search_store(
        file=file_path,
        file_search_store_name=target_store.name
    )
    
    # Wait for completion
    while not operation.done:
        time.sleep(2)
        operation = client.operations.get(operation)
        
    print("Upload and indexing complete!")

def test_query_file(client, file_path: str):
    """Modified test query to identify book name and author specifically."""
    file_name = os.path.basename(file_path)
    stores = client.file_search_stores.list()

    target_store = next((s for s in stores if s.display_name == STORE_NAME), None)
    if not target_store:
        print(f"Store '{STORE_NAME}' not found.")
        return

    # Specific prompt to extract bibliographic info
    prompt = f"Using the file '{file_name}' in your storage, identify the official title of the book and the name of the author. Return ONLY the Book Name and the Author Name."

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[target_store.name]
                )
            )]
        )
    )
    print(f"\n--- Identifying {file_name} ---")
    print(response.text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Islamic Law Sources in Gemini File Store")
    
    # Define mutually exclusive group so you can't check and upload at the same time
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Check if file exists in the store")
    group.add_argument("--upload", action="store_true", help="Upload a new file to the store")
    group.add_argument("--test", action="store_true", help="Test bibliographic retrieval for a file")
    
    # The file path is always required
    parser.add_argument("path", help="The local path to the PDF file")

    args = parser.parse_args()

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    if args.check:
        base_name = os.path.basename(args.path)
        check_file_info(client, base_name)

    elif args.upload:
        upload_to_store(client, args.path)

    elif args.test:
        test_query_file(client, args.path)
