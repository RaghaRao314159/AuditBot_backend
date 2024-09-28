from utils.initialisations import *
from utils.prompt_engineering import *

# LLM model
llm = wrap_openai(openai.Client(api_key=OPENAI_API_KEY))

@traceable
def gpt4o(prompt, client, display = True):
    # api call to gpt 4-o
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    # convert the cryptic gpt response into string
    response = openai_completion_to_text(completion)

    # display the markdown output in python notebook
    if display:
        display_markdown(response, raw=True)

    # return the string response as well so can be traced by langsmith
    return response

def gpt4o_stream(prompt, client, display = False):
    # api call to gpt 4-o
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        stream = True
    )

    return completion


@traceable
def chat_gpt(messages, client):
    # api call to gpt 4-o
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    # convert the cryptic gpt response into string
    response = openai_completion_to_text(completion)

    # return the string response as well so can be traced by langsmith
    return response

@traceable
def trace_params(params):
    (query, chunking, grouping, min_chunk_size, batch_size, top_k, 
     weights, k, top_n, model_name, HyDE, comments) = params
    return {
        "query": query,

        "preprocessing": 
        {
            "chunking type": 'sentences' if chunking == 's' else 'paragraphs',
            "group chunks together": grouping,
            "minimum characters in chunk": min_chunk_size,
        },

        "vector store": 
        {
            "batch size": batch_size
        },

        "ranking":
        {
            "top k chunks per retriever": top_k,
            "weights for sparce retriever": weights[0],
            "weights for dense retriever": weights[1],
            "reciprocal rank fusion constant": k
        },
        "reranking":
        {
            "top n chunks for final ranking": top_n,
            "cross-encoder model": model_name
        },
        "improvements":
        {
            "HyDE": HyDE
        },
        "comments": comments      
    }


@traceable
def rag_pipeline(params, prompt, llm, display = True):
    traced_params = trace_params(params) 
    response = gpt4o(prompt, llm, display)
    return response

def rag_pipeline_stream(params, prompt, llm, display = False):
    traced_params = trace_params(params) 
    response = gpt4o_stream(prompt, llm, display)
    return response

# -----------------------------------------------------------------------
# untraced versions of functions for debugging
def gpt4o_untraced(prompt, client):
    # api call to gpt 4-o
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    # convert the cryptic gpt response into string
    response = openai_completion_to_text(completion)

    # display the markdown output in python notebook
    display_markdown(response, raw=True)

    # return the string response as well so can be traced by langsmith
    return response
