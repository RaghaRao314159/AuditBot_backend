# import useful python libraries
import sys
import os
import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings
from elasticsearch import Elasticsearch
import openai
from langsmith import traceable
from langsmith.wrappers import wrap_openai


# define constants
# for AGO Audit Reports
DOCUMENT_DIR = "../data/documents"
DOC_IDENTIFIER = "ar_fy"

# for National Day Rally
DOCUMENT_DIR_NDR = "../data/documents_ndr"
DOC_IDENTIFIER_NDR = "Rally"

PARSED_DOCUMENT_DIR = "../data/parsed_documents"
LOCAL_HOST_URL = "http://localhost:9200"

# replace this password with your own
DOCKER_USERNAME = 'ilasthik'
DOCKER_PASSWORD = '3rzwe4-nadry8-Bgqf3m'
HTTP_AUTH=(DOCKER_USERNAME, DOCKER_PASSWORD)

# these are not working api keys, substitute your own key here
OPENAI_API_KEY = "s4_3XdsjuZplgRfhc2XufAQT3BlbfFJa2GYB3SrBWr84YxasPw5"
LANGCHAIN_API_KEY = 'lsd8-pt-cdf26323x9b742b5a516f4a90ffeg687_-e4f3d5f9a'


LANGCHAIN_ENDPOINT = "https://api.smith.langchain.com"
LANGCHAIN_TRACING_V2 = 'true'
LANGCHAIN_PROJECT="RAG"

# define environment variables
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ['LANGCHAIN_API_KEY'] = LANGCHAIN_API_KEY
os.environ['LANGCHAIN_TRACING_V2'] = LANGCHAIN_TRACING_V2
os.environ["LANGCHAIN_ENDPOINT"] = LANGCHAIN_ENDPOINT
os.environ["LANGCHAIN_PROJECT"] = "RAG"

# save paths
chunks_path = PARSED_DOCUMENT_DIR + "/chunks.json"
chunk_pageNum_pairs_path = PARSED_DOCUMENT_DIR + "/chunk_pageNum_pairs.json"
s_p_pairs_path = PARSED_DOCUMENT_DIR + "/sentence_paragraph_pairs.json"
tree_path = PARSED_DOCUMENT_DIR + "/complete_tree.json"
save_inverted_tree_path = PARSED_DOCUMENT_DIR + "/inverted_tree.json"
index_name = 'chromadb_documents'