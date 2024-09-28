from utils.chatbot_design import *
from utils.chatbot_utils import *

import gradio as gr

# this is the logic function that decides what to do with the text received by 
# the user
def logic(message, history):
    # takes in both message and history
    if len(history) == 0:
        # fresh chat
        response = rag.invoke(message)
        return response
    
    # otherwise, analyse whole history
    chat_history_messages = history + [{'role': 'user', 'content': message}]
    response = chat_llm(chat_history_messages)
    return response

# create a chatbot UI
chatbot = gr.ChatInterface(
    logic, 
    title = "My amazing assistant", 
    css=css, 
    type="messages")

# Launch the interface with the custom CSS
chatbot.launch()


