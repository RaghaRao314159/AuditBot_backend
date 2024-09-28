from fastapi import FastAPI
from utils.chatbot_utils import (
    chat_stream, guardrail_inappropriate_chain, guardrail_irrelevant_chain, rag_stream_langserve, agent_langserve_chain, 
    all_agent_langserve_chain
)
from langserve import add_routes
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# initialise app
app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# main RAG chain
add_routes(
    app,
    rag_stream_langserve,
    path = '/rag'
)

# default LLM chain for when RAG is not needed
add_routes(
    app,
    chat_stream,
    path = '/chat'
)

# All agents combined into one
# Agent 1: checks if RAG is needed
# Agent 2: improves on user's question for more effective retrieval 
add_routes(
    app,
    all_agent_langserve_chain,
    path = '/all_agent'
)

# Guard rails for checking if input is inappropriate
add_routes(
    app,
    guardrail_inappropriate_chain,
    path = '/inappropriate'
)

# Guard rails for checking if input is irrelevant
add_routes(
    app,
    guardrail_irrelevant_chain ,
    path = '/irrelevant'
)

# start app
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)