import os
from flask import Flask, jsonify, request, session, render_template, json
from openai import OpenAI
from waitress import serve
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

app = Flask(__name__)
app.secret_key = os.urandom(24) 

with open('prompts/chatbot.txt', 'r', encoding='utf-8') as file:
    prompt = file.read()   


def ai_bot_response(user_message, conversation_history):
    
    messages = [
        {
        "role": "system",
        "content": prompt
        },
        *conversation_history
    ]
    
    messages.extend(conversation_history) 
    messages.append({"role": "user", "content": user_message})

    tools = [{"type": "web_search_preview"}]
    
    response = client.responses.create(
        model="gpt-4o-mini", 
        input=messages,
        max_output_tokens=1000,
        tools = tools,
    )
    print("OpenAI API Raw Response:", response) # Keep this for detailed debugging
    bot_response_text = response.output_text

    
    
    if bot_response_text.startswith('[Q_MC]'):
        response_parts =  bot_response_text[6:].split("][")
        question_text = response_parts[0]
        question_reasoning = response_parts[1]
        options = response_parts[2:]

        return json.dumps({
            "type": "question_multiple_choice",
            "question": question_text, 
            "reasoning": question_reasoning, 
            "options": options
        })

    elif bot_response_text.startswith('[Q_S]'):
        response_parts =  bot_response_text[5:].split("][")
        question_text = response_parts[0]
        question_reasoning = response_parts[1]
        slider_range = response_parts[2]

        return json.dumps({
            "type": "question_slider", 
            "question": question_text, 
            "reasoning": question_reasoning, 
            "slider_range": slider_range
        })          

    elif bot_response_text.startswith('[Q_OE]'):
        response_parts =  bot_response_text[6:].split("][")
        question_text = response_parts[0]
        question_reasoning = response_parts[1]

        return json.dumps({
            "type": "question_open_ended",
            "question": question_text, 
            "reasoning": question_reasoning
        })

    elif bot_response_text.startswith('[R]'):
        recommendations = []
        reco_blocks = bot_response_text.split('[R]')

        for block in reco_blocks:
            if block.strip(): # Process only non-empty blocks
                # Split each block by ][ to get text, specs, price, ratings
                # Ensure we split only on the '][' sequence
                parts = block.strip().split('][') 
                if len(parts) >= 4:
                    recommendation = {
                        "text": parts[0].strip('[]'), # Strip potential leading/trailing brackets
                        "specs": parts[1].strip('[]'),
                        "price": parts[2].strip('[]'),
                        "ratings": parts[3].strip('[]')
                    }
                    recommendations.append(recommendation)
                else:
                    # Handle case where a recommendation block doesn't have all parts
                    print("Warning: Incomplete recommendation block found:", block)
        return json.dumps({
            "type": "recommendations_list",
            "recommendations": recommendations
        })
     
    else:
        return bot_response_text


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