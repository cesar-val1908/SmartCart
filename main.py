import os
from flask import Flask, jsonify, render_template, request, session # Import session
from openai import OpenAI
from waitress import serve

client = OpenAI() 

app = Flask(__name__)
app.secret_key = os.urandom(24)

def ai_bot_response(user_message, conversation_history):
    ai_prompt = """
    You are **CNZ Shopping**, a streamlined shopping assistant. Your role is to quickly identify user needs and recommend products.

When a user asks for a product, immediately engage them with **one follow-up question at a time** to narrow down their search. Frame your questions to elicit specific details.

**Question Examples:**
* "To help me find the best laptop for you, could you tell me your primary use case – is it for gaming, professional work, school, or general Browse?"
* (Based on "work"): "What kind of professional tasks will you be performing, and are there any specific software requirements?"
* (Based on "gaming"): "What types of games do you play, and what's your priority: resolution, frame rate, or portability?"
* "What is your ideal budget range for this item?"
* "Are there any specific features (like screen size, battery life, or brand) that are important to you?"

After gathering 2-4 key pieces of information, conduct a targeted search. Present **3 top product recommendations**. For each, include:
* **Product Name**
* **Core Specifications**
* **Price**
* **User Rating**
* **A concise reason** why it's a good fit.

Ask the user if these options meet their needs or if they'd like more suggestions, and make sure that you don't repeat questions.

    """
    
    # Initialize messages with the system prompt
    messages = [{"role": "system", "content": ai_prompt}]
    
    # Add previous conversation history
    messages.extend(conversation_history) 
    
    # Add the current user message
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o-mini-search-preview-2025-03-11", 
        messages=messages,
        max_tokens=100,
    )
    print("OpenAI API Raw Response:", response)
    return response.choices[0].message.content.strip()


@app.route("/")
def home():
    # Initialize or clear conversation history when the home page is loaded
    session['conversation_history'] = []
    return render_template("index.html")


@app.route("/get_response", methods=["POST"])
def get_response():
    data = request.json
    user_input = data.get("user_input")

    # Get conversation history from session, initialize if not present
    conversation_history = session.get('conversation_history', [])

    # Get the bot's response using the full history + current user input
    bot_response = ai_bot_response(user_input, conversation_history)

    # Update conversation history with both the user's message and the bot's response
    conversation_history.append({"role": "user", "content": user_input})
    conversation_history.append({"role": "assistant", "content": bot_response})
    
    # Store the updated history back in the session
    session['conversation_history'] = conversation_history

    return jsonify({"response": bot_response})


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)