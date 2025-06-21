import openai
import os
from dotenv import load_dotenv

load_dotenv()

def summarize_reviews(reviews):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = f"Summarize the following product reviews:\n{reviews}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']
