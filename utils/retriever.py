# langchain libraries
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# huggingface libraries
from sentence_transformers import CrossEncoder

# import other useful python libraries
import numpy as np

# retriever functions

# This function takes langchain docs which are class wrappers for strings and 
# converts to python strings
def langchain_docs_to_textlist(langchain_docs):
    """
    @param langchain_docs: list, collection of langchain document class objects

    @return textlist: list, text (str) obtained from langchain object

    --------------------------------------------------------------------------

    Function summary:
    This function takes langchain docs which are class wrappers for strings and 
    converts to python strings
    """

    # initialise text list
    textlist = []

    # iterate through langchain docs list
    for doc in langchain_docs:

        # convert langchain doc to string
        # add to text list
        textlist.append(doc.page_content)
    
    # return list of strings that can be used for easier manipulation
    return textlist


# This function finds finds the top k similar chunks to query with hybrid 
# search. (BM25 and FAISS)
def ranking(chunks, query, top_k, openai_api_key):
    ''' 
    This function finds finds the top k similar chunks to query with hybrid 
    search. (BM25 and FAISS)
   
    Input:
    -----------
        chunks: list (str)
            each element is text (str) of a chunk

        query: str
            question by user

        top_k: int
            filter chunks among the top_k matches with query

        openai_api_key: str
            get from OpenAI website

    Output:
    --------
        good_chunks: list (str)
            chunks (str) that are top_k matches with query
        
        good_langchain_docs: list
            chunks (langchain_docs objects) that are top_k matches with query

    '''
    chunk_list_1 = chunks
    chunk_list_2 = chunks.copy()
    
    # initialize the bm25 retriever
    bm25_retriever = BM25Retriever.from_texts(
        chunk_list_1
    )
    bm25_retriever.k = top_k

    # initialize the faiss retriever
    embedding = OpenAIEmbeddings(model="text-embedding-3-small",
                                 api_key = openai_api_key)
    faiss_vectorstore = FAISS.from_texts(
        chunk_list_2, embedding
    )
    faiss_retriever = faiss_vectorstore.as_retriever(search_kwargs={"k": top_k})

    # initialize the ensemble retriever
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, faiss_retriever], weights=[0.5, 0.5]
    )

    # do hybrid search, combine with resiprocal rank fusion
    good_langchain_docs = ensemble_retriever.invoke(query)
    good_chunks = langchain_docs_to_textlist(good_langchain_docs)

    # return top k matches 
    return good_chunks, good_langchain_docs


# This function finds finds the top n similar chunks to query with cross 
# encoder.
def reranking(model_name, good_chunks, query, top_n = -1, model = None):
    '''
    This function finds finds the top n similar chunks to query with cross 
    encoder.
   
    Input:
    -----------
        model_name: str
            name of cross encoder model.

        good_chunks: list (str)
            contains top chunks (str) from 1st ranking.

        query: str
            question by user

        top_n: int
            filter chunks among the top_n matches with query
        
        model: Any
            cross encoder model if provided

    Output:
    --------
        best_chunks: list (str)
            chunks (str) that are top_n matches with query. These chunks are 
            sorted from best to worst

        sorted_scores: list (float)
            similarity scores of the top_n matches with query. These scores are
            sorted from best to worst

    '''
    # Initialise cross encoder model
    if model == None:
        model = CrossEncoder(model_name, max_length=512, )

    # Make a query string for every chunk
    queries = [query for _ in range(len(good_chunks))] 

    # Find classification score between query and chunk (trained to be a 
    # similarity score)
    scores = model.predict(list(zip(queries, good_chunks)))

    # get index of scores sorted in decreasing order
    best_idxs = np.argsort(scores)[::-1]

    # initialise output
    sorted_scores = []
    best_chunks = []

    # top_n = -1 (default) means provide all top matches
    # if top_n is incorrectly inputed, then replace wirh default behaviour
    if top_n > len(good_chunks):
        top_n = -1

    # loop through sorted indices
    for k, idx in enumerate(best_idxs):
        
        # stop once top_n is reached
        if k >= top_n and top_n != -1:
            break

        # append to output
        best_chunks.append(good_chunks[idx])
        sorted_scores.append(scores[idx])
    
    return best_chunks, sorted_scores