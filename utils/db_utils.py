from IPython.utils import io
import numpy as np

# dense embedding search =====================================================

# chromda db functions -------------------------------------------------------
def chroma_get_or_create_collection(client, name, embedding_function, reset):
    ''' 
    This function creates a chroma vector data base
   
    Input:
    -----------
        client: chromadb.api.ClientAPI
            A persistent client (acts as a folder) where the database will be 
            stored
        
        name: str
            name of the database (collection)
        
        embedding_function: 
            chromadb.utils.embedding_functions.OpenAIEmbeddingFunction
            Embedding function used in chroma db
        
        reset: bool
            resets the whole persistent client, inclusing every collelction 
            (data base) stored inside. 
            ONLY RESET AT THE VERY START

    Output:
    ----------
        collection: chromadb.api.models.Collection
            vector database
    '''

    # if reset is True, reset everything
    if reset:
        client.reset()
    
    # create empty data base
    collection = client.get_or_create_collection(
        name = name, 
        embedding_function = embedding_function)

    return collection

def chroma_preprocess_metadata(pre_metadata):
    ''' 
    This function corrects the formatting of metadata about chunks to match 
    chroma db requirements
   
    Input:
    -----------
        pre_metadata: list (dict)
            pre_metadata = list(inverted_tree.values())

    Output:
    ----------
        metadata: list (dict)
            location field is changes from list to string
    '''

    # initialise metadata list
    metadata = []

    # loop through pre_metadata
    for pre_data in pre_metadata:

        # location field is changes from list to string
        data = {
                    "year": pre_data["year"]
               }
        
        # assign location seperately because some docs do not have content page
        location = pre_data.get("location", -1)

        # if location exists
        if location != -1:
            data["location"] = ', '.join(location)

        # assign page number seperately because some pages do not have a page.
        page = pre_data.get("page", -1)

        # if page number exists
        if page != -1:
            data["page"] = page
        
        metadata.append(data)
    
    return metadata


def chroma_fill_db(db, chunks, metadata, batch_size):
    ''' 
    This function fills the data base with chunks and metadata
   
    Input:
    -----------
        db: chromadb.api.models.Collection
            vector database
        
        chunks: list (str)
            each element is text (str) of a chunk
        
        metadata: list (dict)
            contains year, location in document and page number of chunk
        
        batch_size: int
            add to data base in batches

    Output:
    ----------
        None
            data base passed in by reference and filled in function
        
    '''
    # avoid unnecessary printing in jupyter notebooks
    with io.capture_output() as captured:

        # add to data base in batches 
        i, start, end = 0, 0, batch_size

        if batch_size >= len(chunks):
            db.add(
                ids = [f"id{i}" for i in range(len(chunks))],
                metadatas=metadata,
                documents=chunks
            )

            return


        # loop though chunks in batches of batch_size
        while batch_size * (i + 1) < len(chunks):

            # set start and end indices
            start = batch_size * i
            end = batch_size * (i + 1)

            # add batch to data base
            db.add(
                ids = [f"id{i}" for i in range(start, end)],
                metadatas=metadata[start : end],
                documents=chunks[start : end]
            )

            # increment to next batch
            i += 1

        # add remainder that do not amount to a whole batch
        db.add(
                ids = [f"id{i}" for i in range(end, len(chunks))],
                metadatas=metadata[end:],
                documents=chunks[end:]
            )

def chroma_update_db(db, chunks, metadata, batch_size):
    ''' 
    This function fills the data base with chunks and metadata
   
    Input:
    -----------
        db: chromadb.api.models.Collection
            vector database
        
        chunks: list (str)
            each element is text (str) of a chunk
        
        metadata: list (dict)
            contains year, location in document and page number of chunk
        
        batch_size: int
            add to data base in batches

    Output:
    ----------
        None
            data base passed in by reference and filled in function
        
    '''
    # avoid unnecessary printing in jupyter notebooks
    with io.capture_output() as captured:

        current_idx = db.count()

        # add to data base in batches 
        i, start, end = 0, 0, batch_size

        if batch_size >= len(chunks):
            db.add(
                ids = [f"id{i + current_idx}" for i in range(len(chunks))],
                metadatas=metadata,
                documents=chunks
            )

            return


        # loop though chunks in batches of batch_size
        while batch_size * (i + 1) < len(chunks):

            # set start and end indices
            start = batch_size * i
            end = batch_size * (i + 1)

            # add batch to data base
            db.add(
                ids = [f"id{i + current_idx}" for i in range(start, end)],
                metadatas=metadata[start : end],
                documents=chunks[start : end]
            )

            # increment to next batch
            i += 1

        # add remainder that do not amount to a whole batch
        db.add(
                ids = [f"id{i + current_idx}" for i in range(end, len(chunks))],
                metadatas=metadata[end:],
                documents=chunks[end:]
            )
        

def chromadb_embedding_search(database, query, top_k):
    ''' 
    This function fills the data base with chunks and metadata
   
    Input:
    -----------
        database: chromadb.api.models.Collection
            vector database
        
        query: str
            question by user

        top_k: int
            filter chunks among the top_k matches with query

    Output:
    ----------
        results: list (str, str)
            list of (result, rank) pairs
        
    '''
    # dense search for match with query 
    search_output = database.query(query_texts = [query],
                             n_results = top_k)
    
    # return matching chunks and their rank 
    results =  [(result, idx) for idx, result in 
            enumerate(search_output['documents'][0])]
    
    return results

# sparce embedding search ====================================================

# elasticsearch --------------------------------------------------------------

# Function to delete all indices
def elastic_reset(client, http_auth):
    try:
        # Get a list of all indices
        indices = client.indices.get('*', http_auth=http_auth)

        # Loop through the indices and delete each one
        for index in indices:
            client.indices.delete(index=index, http_auth=http_auth)
            print(f"reset index: {index}")
    except Exception as e:
        print(f"An error occurred when resetting elasticsearch: {e}")



def index_elastic_db(elastic_db, index_name, http_auth, chunks, reset):
    ''' 
    This function indexes the data so text search can be sped up drastically.
    This only needs to be done when the database is set up. 
   
    Input:
    -----------
        elastic_db: chromadb.api.models.Collection
            vector database
        
        index_name: str
            elasticsearch can store multiple indexes so index_name is required.

        http_auth: int
            the container in use requires a username and password which is set 
            upon creation.
        
        chunks: list (str)
            each element is text (str) of a chunk

        reset: boolean
            resets elastic db indices


    Output:
    ----------
        None
            data base passed in by reference and indexed in function
        
    '''
    # create indexing for sparce search
    if not elastic_db.indices.exists(index=index_name, http_auth=http_auth):
        elastic_db.indices.create(index=index_name, http_auth=http_auth)

    if reset:
        elastic_reset(elastic_db, http_auth=http_auth)

    # Index documents
    for i, chunk in enumerate(chunks):
        elastic_db.index(index=index_name, 
                    id=i, 
                    body={'text': chunk}, 
                    http_auth=http_auth)
        
def bm25_elasticsearch(elastic_db, index_name, http_auth, query, top_k):
    ''' 
    This function searches the database for a query that matches the text 
    using BM25.
   
    Input:
    -----------
        elastic_db: chromadb.api.models.Collection
            vector database
        
        index_name: str
            elasticsearch can store multiple indexes so index_name is required.

        http_auth: int
            the container in use requires a username and password which is set 
            upon creation.
        
        query: str
            question by user

        top_k: int
            filter chunks among the top_k matches with query

    Output:
    ----------
        results: list (str, int)
            list of (result, rank) pairs
        
    '''
    # set up a http request to the database sitting in a docker container
    response = elastic_db.search(index=index_name, body={
        'query': {
            'match': {
                'text': query
            }
        },
        'size': top_k
    }, http_auth=http_auth)

    # return search results
    results = [
        (hit['_source']['text'], idx) 
        for idx, hit in 
        enumerate(response['hits']['hits'])
        ]
    
    return results

# python manual bm25 search --------------------------------------------------
def bm25_search(BM25_db, chunks, query, top_k):
    ''' 
    This function searches for a query that matches the text using BM25. It 
    does not use a persistent database but instead a program memory. 

    The chunks (dataset) has to be passed in everytime the search is done. 
    This is not recommended for large datasets and production. It can be used
    for testing simple RAG frameworks.
   
    Input:
    -----------
        BM25_db: rank_bm25.BM25Okapi
            vector database

        chunks: list (str)
            each element is text (str) of a chunk
        
        query: str
            question by user

        top_k: int
            filter chunks among the top_k matches with query

    Output:
    ----------
        results: list (str, int)
            list of (result, rank) pairs
        
    '''
    # tokenizing splits the query into words as BM25 uses Bag-of-words
    tokenized_query = query.split()

    # Get BM25 scores
    bm25_scores = BM25_db.get_scores(tokenized_query)

    # Sort chunks based on BM25 scores
    top_n_indices = np.argsort(bm25_scores)[-top_k:][::-1]

    # return results
    return [(chunks[idx], idx) for idx in top_n_indices]


# Fusion =====================================================================
def reciprocal_rank_fusion(bm25_results, 
                           embedding_results, 
                           weights, 
                           k=60):
    ''' 
    This function fuses 2 ranks and produces a final rank using RRF algorithm.
   
    Input:
    -----------
        bm25_results: list (str, str)
            list of (result, rank) pairs from BM25

        embedding_results: list (str, str)
            list of (result, rank) pairs from dense search

        weights: list
            list of weights assigned to each retriever results

        k: int
            a constant used in the RRF algorithm.
            Empirically, k = 60 gives the best results.

    Output:
    ----------
        results: list (str)
            list of chunks
        
    '''
    # initialise dictionary for chunk: score pairs
    fusion_scores = {}

    # obtain weights from input
    bm25_weight = weights[0]
    embedding_weight = weights[1]

    # add weighted scores from bm25 ranked results
    for chunk, rank in bm25_results:
        fusion_scores[chunk] = (fusion_scores.get(chunk, 0) 
                                + bm25_weight / (k + rank))
    
    # add weighted scores from dense embedding search ranked results
    for chunk, rank in embedding_results:
        fusion_scores[chunk] = (fusion_scores.get(chunk, 0) 
                                + embedding_weight / (k + rank))
    
    # sort final scores in decreasing order
    sorted_results = sorted(fusion_scores.items(), 
                            key=lambda item: item[1], 
                            reverse=True)
    
    # return the best chunks
    good_chunks = [chunk for chunk, score in sorted_results]

    return good_chunks