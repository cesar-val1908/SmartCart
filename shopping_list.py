import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_bundle(event_type):
    prompt = f"""
You are an amazing and helpful shopping assistant. A user is preparing for an {event_type}.

Your task is to recommend **3 essential item** they should buy for that event.

For each item, include:
- "item": the item name
- "reason": why it is needed
- "price": estimated price
- "link": (optional) a placeholder product URL

Format your response as valid JSON in this exact structure:

[
  {{
    "item": "Tent",
    "reason": "For shelter overnight",
    "price": "$50",
    "link": "https://example.com/tent"
  }},
  ...
]
Only return the JSON. Do not include any explanation or text outside the JSON. 
Do not include markdown or any text formatting — only output plain JSON.


"""

    messages = [
        {"role": "system", "content": "You're a smart shopping assistant."},
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7
    )

    raw = response.choices[0].message.content
    print("RAW GPT RESPONSE:\n", raw) #help JSON not throw an error

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("Could not parse JSON from GPT response.")
        return []

if __name__ == "__main__":
    bundle = generate_bundle("back to school")
    for item in bundle:
        print(f"- {item['item']}: {item['reason']} ({item['price']})")
