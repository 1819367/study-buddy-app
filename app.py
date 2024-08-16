from flask import Flask, render_template, request, jsonify
import time
from openai import OpenAI
import logging
import datetime
import re

# app will run at: http://127.0.0.1:5000/

# set up logging in the assistant.log file
log = logging.getLogger("assistant")

logging.basicConfig(filename = "assistant.log", level = logging.INFO)

from openai import OpenAI

client = OpenAI()

app = Flask(__name__)

# Initialize the Assistant and Thread globally so all functions have access to the assistant_id and thread_id
# global variables set to empty strings
assistant_id = ""
thread_id = ""

# The array that will hold the chat history as the user and the assistant interact
chat_history = [
    {"role": "system", 
     "content": "Hey there! How can I assist you with your learning today?"
     }
]

# Start by getting the assistant_id and thread_id and returning them
@app.route("/get_ids", methods=["GET"])
# funtion that will get the assistant ID and thread ID
def get_ids():
    return jsonify(assistant_id=assistant_id, thread_id=thread_id)

# If there is a message thread, send it to the the JavaScript using msg.role to render it to the UI. # # If there isn't a thread, return an error
@app.route("/get_messages", methods=["GET"])
def get_messages():
    if thread_id != "":
        thread_messages = client.beta.threads.messages.list(thread_id, order="asc")
        messages = [
            {
               "role": msg.role,
               "content": msg.content[0].text.value, 
            }
            for msg in thread_messages.data
        ]
        return jsonify(success=True, messages=messages)
    else:
        return jsonify(success=False, message="No thread ID")

# Create the assistant
# Use your assitant_id to retrieve your a assistant from the openai playground
# Replace "asst_yournewassistantID" with your assistant ID


# Create a thread if there isn't one


# Function to add to the log in the assistant.log file


# Render the HTML template - we're going to see a UI!!!
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", chat_history=chat_history)

# This is the POST route for the chat. Adds the chat to the chat_history array and sends it to the assistant playground on openai
 
    
# Reset the chat
@app.route("/reset", methods=["POST"])
def reset_chat():
    global chat_history
    chat_history = [{"role": "system", "content": "Hey there! How can I assist you with your learning today?"}]
    global thread_id
    thread_id = ""
    create_thread()
    return jsonify(success=True)


# Create the assistants and thread when we first load the flask server
@app.before_request
def initialize():
    app.before_request_funcs[None].remove(initialize)
    create_assistant()
    create_thread()
    
    
# Run the flask server
if __name__ == "__main__":
    app.run()
