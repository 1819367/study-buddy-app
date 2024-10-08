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
def create_assistant():
    global assistant_id
    my_assistant = client.beta.assistants.retrieve(assistant_id="asst_XdYTmnWKrnciClxxeCx9nGFI")
    assistant_id = my_assistant.id
    return my_assistant

# Create a thread if there isn't one
def create_thread():
    global thread_id
    # check if the thread exists before creating it
    if thread_id == "":
        thread = client.beta.threads.create()
        thread_id = thread.id #corrected error
    else:
        # if one exists, retrieve the current thread ID
        thread = client.beta.threads.retrieve(thread_id)
        thread_id = thread.id
    return thread

# Function to add to the log in the assistant.log file
def log_run(run_status):
    if run_status in ["cancelled", "failed", "expired"]:
        log.err(str(datetime.datetime.now()) + " Run " + run_status + "\n")


# Render the HTML template - we're going to see a UI!!!
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", chat_history=chat_history)

# This is the POST route for the chat. Adds the chat to the chat_history array and sends it to the assistant playground on openai
@app.route("/chat", methods=["POST"])
# the message the user added is passed to the assisgned variable (user_input)
def chat():
    user_input = request.json["message"]
    
    # set up moderation for user's message
    moderation_result = client.moderations.create(
        input = user_input
    )

    while moderation_result.results[0].flagged == True:
        moderation_result = client.moderations.create(
            input = user_input
        )
        # append the message to the user to the chat_history
        chat_history.append({"role": "assistant","content": user_input})
        # return moderation message so that it prints out as a message in the chat window
        return jsonify(success=True, message="Assistant: Sorry, your message violated our community guidelines.  Please try another prompt.")
    
    # if the user's message passes moderation, their message is appended to the chat_history
    chat_history.append({"role": "user","content": user_input })

    # Send the message to the assistant
    message_params = {"thread_id": thread_id, "role": "user", "content": user_input}

    # pass all the message params with the dictionary to the method that creates the thread of messages
    thread_message = client.beta.threads.messages.create(**message_params)

    # create the run and pass it the thread ID and assistant ID
    run = client.beta.threads.runs.create(
        thread_id = thread_id,
        assistant_id = assistant_id
    )

    # time it takes to answer question, tjhe users sees a series of animated dots.
    while run.status != "completed":
        time.sleep(.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

   # Message from the assistant is also added to the chat_history or an error message if something goes wrong
    thread_messages = client.beta.threads.messages.list(thread_id)
    message = thread_messages.data[0].content[0].text.value
    if run.status in ["cancelled", "failed", "expired"]:
        message = "An error has occured, please try again."
    chat_history.append({"role": "assistant", "content": message})

    # run the log_run function and return the messages to finish the route
    log_run(run.status)
    return jsonify(success=True, message=message)

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
