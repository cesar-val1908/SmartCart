import requests
import os
from dotenv import load_dotenv

load_dotenv()

def search_serp_products(query):
    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "engine": "google_shopping",
        "api_key": os.getenv("SERPAPI_KEY")
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None
