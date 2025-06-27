import os
from flask import Flask, jsonify, render_template, request, session 
from openai import OpenAI
from waitress import serve
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

app = Flask(__name__)
app.secret_key = os.urandom(24) 

with open('ai_prompt.txt', 'r', encoding='utf-8') as file:
    prompt = file.read()   

def ai_bot_response(user_message, conversation_history):
    ai_prompt = prompt
    
    messages = [
        {
        "role": "system",
        "content": ai_prompt
        },
        *conversation_history
    ]
    
    messages.extend(conversation_history) 
    messages.append({"role": "user", "content": user_message})

    tools = [
        {
            "type": "web_search_preview"
        }
    ]
    
    response = client.responses.create(
        model="gpt-4o-mini", 
        input=messages,
        max_output_tokens=1000,
        tools = tools,
    )
    print("OpenAI API Raw Response:", response) # Keep this for detailed debugging
    return response.output_text


@app.route("/")
def home():
    session['conversation_history'] = []
    return render_template("index.html")


@app.route("/get_response", methods=["POST"])
def get_response():
    data = request.json
    user_input = data.get("user_input")

    conversation_history = session.get('conversation_history', [])

    bot_response = ai_bot_response(user_input, conversation_history)

    conversation_history.append({"role": "user", "content": user_input})
    conversation_history.append({"role": "assistant", "content": bot_response}) 
    session['conversation_history'] = conversation_history


    return jsonify({"response": bot_response})


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in .env file. Please set it up.")
    else:
        print("Starting Flask app with Waitress...")
        serve(app, host='0.0.0.0', port=8000)