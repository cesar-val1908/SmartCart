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
        {"role": "system", "content": prompt},
        *conversation_history,
        {"role": "user", "content": user_message},
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "createMultipleChoice",
                "description": "Create a multiple choice question for the user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "The question to ask the user."},
                        "reason": {"type": "string", "description": "The reason for asking this question."},
                        "options": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "A list of options for the user to choose from."
                        }
                    },
                    "required": ["question", "reason", "options"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "createSliderQuestion",
                "description": "Create a question with a slider for a numerical range.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "The question to ask the user."},
                        "reason": {"type": "string", "description": "The reason for asking this question."},
                        "slider_range": {"type": "string", "description": "The range for the slider, e.g., '10-5000'."}
                    },
                    "required": ["question", "reason", "slider_range"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "createOpenEndedQuestion",
                "description": "Create an open-ended question for the user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "The question to ask the user."},
                        "reason": {"type": "string", "description": "The reason for asking this question."}
                    },
                    "required": ["question", "reason"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "createRecommendations",
                "description": "Create a list of product recommendations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string", "description": "Product Name and short description."},
                                    "specs": {"type": "string", "description": "Product specifications."},
                                    "price": {"type": "string", "description": "Product price."},
                                    "ratings": {"type": "string", "description": "Product ratings."}
                                },
                                "required": ["text", "specs", "price", "ratings"]
                            }
                        }
                    },
                    "required": ["recommendations"]
                }
            }
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o-search-preview",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=1000
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        tool_call = tool_calls[0]
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        if function_name == "createMultipleChoice":
            return json.dumps({
                "type": "question_multiple_choice",
                "question": function_args.get("question"),
                "reasoning": function_args.get("reason"),
                "options": function_args.get("options")
            })
        elif function_name == "createSliderQuestion":
            return json.dumps({
                "type": "question_slider",
                "question": function_args.get("question"),
                "reasoning": function_args.get("reason"),
                "slider_range": function_args.get("slider_range")
            })
        elif function_name == "createOpenEndedQuestion":
            return json.dumps({
                "type": "question_open_ended",
                "question": function_args.get("question"),
                "reasoning": function_args.get("reason")
            })
        elif function_name == "createRecommendations":
            return json.dumps({
                "type": "recommendations_list",
                "recommendations": function_args.get("recommendations")
            })

    return response_message.content


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
