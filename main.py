import os

from flask import Flask, jsonify, render_template, request
from openai import OpenAI
from waitress import serve
from dotenv import load_dotenv

load_dotenv()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

client = OpenAI()

tools = [
    {
        "type": "web_search_preview"
    }
]

conversation_history = []

def ai_bot_response(prompt):
    
    conversation_history.append(
        {
        "role": "user",
        "content": prompt
        }
    )

    response = client.responses.create(

        model="gpt-4o-mini",
        input = [
            {
                "role": "system", 
                "content": "Customer service helper"
            },
            *conversation_history
        ],  
        tools = tools,                              #Allows openAI to explore the web
    )

    conversation_history.append(
        {
        "role": "assistant",
        "content": response.output_text
        }
    )
    return response.output_text


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get_response", methods=["POST"])
def get_response():
    data = request.json
    user_input = data.get("user_input")
    bot_response = ai_bot_response(user_input)
    return jsonify({"response": bot_response})


if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=8000)
