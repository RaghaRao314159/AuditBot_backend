from flask import Flask, request, Response, stream_with_context, jsonify
import openai
import flask
from flask_cors import CORS
import json
from utils.agency import improve_question, need_RAG
from utils.chatbot_utils import *

# initialise LLM
# this is not a working api key, substitute your own key here
OPENAI_API_KEY = "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"
llm_client = openai.Client(api_key=OPENAI_API_KEY)

# Inilialise Flask App (backend)
app = Flask(__name__)

# This is to enable Cross-origin resource sharing so another server (frontend) 
# can have a 2-way communication with this flask backend
CORS(app)
    
# only one route is used
@app.route('/', methods=['POST'])
def chatWithBot():

    # we need to ensure the content type send is json
    content_type = request.headers.get('Content-Type')
    print(content_type)

    if content_type == 'application/json':
        json_data = request.json

        # Conversation is split into latest question and history
        # latest question is needed for RAG
        # history is needed for agent to check if RAG is needed 
        question = json_data['messages'][-1]["content"]
        history = json_data['messages'][:-1]

        # check for conversation length.
        # if in future, you would like to limit length of conversations
        print("length of messages:", len(json_data['messages']))

        # need_RAG is an agent that checks if question needs RAG
        if need_RAG(history, question):
            print("RAG INVOKED!!!")
            # This is an optional agent that improves on the user's question
            # for RAG purposes

            # We cannot always assume the user uses proper english so this step
            # might be required 

            # improved_question = improve_question(history, question)
            # print("IMPROVED QUESTION: ", improved_question)

            # invoke the LCEL chain 
            completion = rag_stream.invoke(question)
            
        else:
            # if RAG is not required, directly prompt the LLM with the 
            # conversation
            # Call the API with stream=True
            completion = llm_client.chat.completions.create(
                model="gpt-4o",
                messages=json_data['messages'],
                stream=True
            )
        
        # Use a generator to yield each part of the streamed response
        def generate():
            # completion is also a generator. In JS terms, it would be a 
            # promise
            for chunk in completion:
                # when streaming, the LLM outputs in small packets (delta) 
                # This is how delta can be accesses for GPT-4o. It might be 
                # different for other GPT models. Double check with OpenAI 
                delta = chunk.choices[0].delta.content
                if delta != None and len(delta) != 0:
                    # convert to JSON so it can be sent over to frontend
                    response = json.dumps({"answer": delta})

                    # streaming means have to yield.
                    # An async function will receive it on the frontend
                    yield f"data: {response}\n\n"

                # streaming has ended
                elif delta == None:
                    # message to frontend to indicate that streaming is over 
                    # and the async function on frontend can exit.
                    response = json.dumps({"answer": "DONE"})

                    yield f"data: {response}\n\n"

        # Return a response that streams the data to the client
        return Response(generate(), mimetype='text/event-stream')

    else:
        print('Content-Type not supported!')
        return 'Content-Type not supported!'

    
    
if __name__ == "__main__":
    app.run(debug=True)