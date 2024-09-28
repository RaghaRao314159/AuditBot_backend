
from utils.agency import all_agent, guardrail_inappropriate, guardrail_irrelevant, improve_question, need_RAG
from utils.initialisations import *
from utils.db_utils import *
from utils.custom_print import *
from utils.retriever import *
from utils.json_parser import *
from utils.prompt_engineering import *
from utils.langsmith_trace import *

from langchain_core.runnables import (
    RunnableLambda, 
    RunnableParallel, 
    RunnablePassthrough,
    RunnableGenerator
)

# soon to be deprecated model classes
# from langchain.chat_models.openai import ChatOpenAI
# from langchain_community.chat_models.openai import ChatOpenAI

# latest model class
from langchain_openai import ChatOpenAI

from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


from nemoguardrails.integrations.langchain.runnable_rails import RunnableRails
from nemoguardrails import RailsConfig, LLMRails


# environment variables ======================================================
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# paths for python file =====================================================
DOCUMENT_DIR = "data/documents" # for AGO Audit Reports
DOCUMENT_DIR_NDR = "../data/documents_ndr" # for National Day Rally
PARSED_DOCUMENT_DIR = "data/parsed_documents"

chunks_path = PARSED_DOCUMENT_DIR + "/chunks.json"
chunk_pageNum_pairs_path = PARSED_DOCUMENT_DIR + "/chunk_pageNum_pairs.json"
s_p_pairs_path = PARSED_DOCUMENT_DIR + "/sentence_paragraph_pairs.json"
tree_path = PARSED_DOCUMENT_DIR + "/complete_tree.json"
save_inverted_tree_path = PARSED_DOCUMENT_DIR + "/inverted_tree.json"


# HYPERPARAMETERS ============================================================

# preprocessing --------------------------------------------------------------

# Chunk into sentences ('s') or paragraphs ('p')
chunking='s' 

# Group smaller chunks into a bigger chunk
grouping=1

# control minimum chubk size
min_chunk_size=100

# vector store ---------------------------------------------------------------

# add to data base in batches
batch_size = 1000

# Ranking --------------------------------------------------------------------

# top k matches for ranking. 
# Both sparse and dense search find top_k matches so hybrid search will return 
# at least top_k matches and most 2 * top_k matches
top_k = 30

# weights for each retrieval for reciprocal rank fusion
weights = [0.5, 0.5]

# reciprocal ranking fusion constant
k = 60

# Reranking ------------------------------------------------------------------

# top n matches for reranking
top_n = 20

# Cross encoder model
# claimed to be deprecated because it is bad but seems to still work fine
# model_name = "cross-encoder/stsb-roberta-base"

# best performing on Microsoft tests
model_name = "cross-encoder/ms-marco-MiniLM-L-12-v2"
cross_encoder_model = model = CrossEncoder(model_name, max_length=512)


# IMPROVEMENTS ===============================================================
HyDE = False
if HyDE:
    comments = "This is using HyDE"
else:
    comments = "None"

# pack parameters for tracing ================================================
params = (chunking, grouping, min_chunk_size, batch_size, top_k, 
          weights, k, top_n, model_name, HyDE, comments)


# Prepare datasets for augmentation ==========================================

# retrieve all required data structures

inverted_tree = json_file_to_dict(save_inverted_tree_path)
# load chunks from tree's keys
chunks = list(inverted_tree.keys())

# prepare metadata for chromadb
pre_metadata = list(inverted_tree.values())
metadata = chroma_preprocess_metadata(pre_metadata)

# load sentence paragraph pairs
if (chunking == 's' or chunking == 'f') and grouping == 1:
    s_p_pairs = json_file_to_dict(s_p_pairs_path)
else:
    s_p_pairs = {}

# start datastores ===========================================================

# vector datastore -----------------------------------------------------------
client_dense = chromadb.PersistentClient(path="data/db")

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=OPENAI_API_KEY,
                model_name="text-embedding-3-small"
            )

collection = chroma_get_or_create_collection(client_dense, 
                                             name = "audit", 
                                             embedding_function = openai_ef, 
                                             reset = False)

# test datastore ------------------------------------------------------------
# connect to the Elasticsearch cluster from python elasticsearch client
client_sparce = Elasticsearch(
    LOCAL_HOST_URL,
    basic_auth=HTTP_AUTH
)

# set up RAG pipeline =======================================================
def use_HyDE(question):
    if HyDE:
        query = gpt4o(hyde(question), llm, display = False)
    else:
        query = question

    return {
                "query" : query,
                "question": question
           }

#  ---------------------------------------------------------------------
def sparce_retrieval(kwargs):

    query = kwargs["query"]

    return bm25_elasticsearch(
        client_sparce, 
        index_name, 
        HTTP_AUTH, query, 
        top_k
    )

def dense_retrieval(kwargs):
    query = kwargs["query"]

    return chromadb_embedding_search(collection, query, top_k)

retrieval = RunnableParallel(
    {
        "sparce": sparce_retrieval,
        "dense": dense_retrieval,
        "rag_input": RunnablePassthrough()
    }
)

# --------------------------------------------------------------------------

def rank(kwargs):
    bm25_results = kwargs["sparce"]
    embedding_results = kwargs["dense"]
    good_chunks = reciprocal_rank_fusion(bm25_results, 
                                  embedding_results, 
                                  weights, 
                                  k)
    return {
                "query": kwargs["rag_input"]["query"], 
                "question": kwargs["rag_input"]["question"],
                "good chunks": good_chunks
           }

rank = RunnableLambda(rank)

# ---------------------------------------------------------------------------

def rerank(kwargs):
    query = kwargs["query"]
        
    good_chunks = kwargs["good chunks"]
    best_chunks, scores = reranking(model_name, 
                                    good_chunks, 
                                    query, 
                                    top_n, 
                                    cross_encoder_model)
    return {
                "query": kwargs["query"], 
                "question": kwargs["question"], 
                "best chunks": best_chunks
           }

rerank = RunnableLambda(rerank)

# ---------------------------------------------------------------------------

def augment(kwargs):
    question = kwargs["question"]

    best_chunks = kwargs["best chunks"]
    prompt = generate_prompt(
        question, 
        inverted_tree, 
        best_chunks, 
        chunking, 
        s_p_pairs)
    
    return {
                "query": kwargs["query"], 
                "question": kwargs["question"], 
                "prompt": prompt
           }

augment = RunnableLambda(augment)

# ---------------------------------------------------------------------------
def chat_llm(messages):
    response = chat_gpt(messages, llm)
    return response

def generate(kwargs):

    question = kwargs["question"]
    prompt = kwargs["prompt"]
    new_params = (question, ) + params
    response = rag_pipeline(new_params, prompt, llm, display = False)
    return response

def generate_stream(kwargs):

    question = kwargs["question"]
    prompt = kwargs["prompt"]
    new_params = (question, ) + params
    response = rag_pipeline_stream(new_params, prompt, llm, display = False)
    return response

generate = RunnableLambda(generate)

generate_stream = RunnableLambda(generate_stream)

rag = use_HyDE | retrieval | rank | rerank | augment | generate

rag_stream = use_HyDE | retrieval | rank | rerank | augment | generate_stream

# ----------------------------------------------------------------------------
# LangServe

# buffer runnable - helps with debugging
def does_nothing(kwargs):
    print("kwargs entered:", kwargs)
    return kwargs

# improve question asked by user for RAG
def improve_on_question(messages):
    history = messages[:-1]
    question = messages[-1]["content"]
    return improve_question(history, question)

improve_on_question = RunnableLambda(improve_on_question)

# model made using Langchain wrapper
model = ChatOpenAI(api_key=OPENAI_API_KEY, model='gpt-4o')

# -------------------------------------------------------------------
# It is possible to convert nemo guardrails into a LCEL chain
# however, I did not use it as streaming is not supported by rails chain.

config = RailsConfig.from_path("./config")
rails = LLMRails(config, llm=model)

async def rails_model(kwargs):
    # response = rails.generate(messages=kwargs)
    response = rails.stream_async(messages=kwargs)
    return response
    # return response["content"]

rails_model = RunnableLambda(rails_model)

# --------------------------------------------------------------------

# reformats prompt to be in format required for langchain model wrapper
def langchain_prompt(kwargs):
    return kwargs["prompt"]

# makes custom function into a chainable function
langchain_prompt = RunnableLambda(langchain_prompt)

# chain for normal conversation
chat_stream =  model | StrOutputParser()

# streaming is not supported for RunnableRails yet, which is needed for langserve
# chat_stream =  does_nothing | rails_model 
# chat_stream_guardrails = RunnableRails(config, runnable=chat_stream)


# chain for RAG
# rag_stream_langserve = improve_on_question | use_HyDE | retrieval | rank | rerank | augment | langchain_prompt | model | StrOutputParser()

rag_stream_langserve = use_HyDE | retrieval | rank | rerank | augment | langchain_prompt | model | StrOutputParser()

# rag_stream_langserve_guardrails = RunnableRails(config, runnable=rag_stream_langserve)


# ----------------------------------------------------------------------------
# agency

# chain for agent to decide if RAG is needed or not
def agent_langserve(messages):
    history = messages[:-1]
    question = messages[-1]["content"]
    return need_RAG(history, question)
        
agent_langserve_chain = RunnableLambda(agent_langserve)

# chain for agent that does everything
def all_agent_langserve(messages):
    history = messages[:-1]
    question = messages[-1]["content"]
    return all_agent(history, question)
        
all_agent_langserve_chain = RunnableLambda(all_agent_langserve)


# ----------------------------------------------------------------------------
# Guardrails

def guardrail_inappropriate_f(messages):
    question = messages[-1]["content"]
    return guardrail_inappropriate(question)

guardrail_inappropriate_chain = RunnableLambda(guardrail_inappropriate_f)


def guardrail_irrelevant_f(messages):
    question = messages[-1]["content"]
    return guardrail_irrelevant(question)

guardrail_irrelevant_chain = RunnableLambda(guardrail_irrelevant_f)

