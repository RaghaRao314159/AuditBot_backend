# generate yearly data for recursive retrieval

# import curtom modules
from utils.json_parser import save_json

# import llama index modules
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.embeddings.openai import OpenAIEmbedding as llama_OpenAIEmbedding
from llama_index.llms.openai import OpenAI as llama_OpenAI
from llama_index.agent.openai import OpenAIAgent as llama_OpenAIAgent
from llama_index.core.schema import IndexNode
from llama_index.core.schema import TextNode
# define constants
audit_summary_general = (
            f'''This content contains audit reports for all years. 
            Use this index if you want to look up details across multiple years.\
            Use this index if query does not mention any years.  
            Do not use this index if you want to analyse a single year.'''
    )

def audit_summary_yearly(year):
    return f'''This content contains audit reports from year {year}. 
            Use this index if you need to lookup specific details from {year}.
            Do not use this index if query does not mention any year.'''


sys_prompt2 = '''
Role:
You are a specialist who uses the context provided to answer the query.

Instruction:
Your response should cite sources' year and page number.
If possible, make ministries or government agencies the headings.

Background:
The context is taken from audit reports from the Auditor-General's Office (AGO) of Singapore. 
AGO is an independent organ of state and the national auditor. They play an important role in enhancing public accountability in the management and use of public funds and resources through their audits.

They audit
    government ministries and departments
    organs of state
    statutory boards
    government funds
    other public authorities and bodies administering public funds (upon their request for audit), e.g. government-owned companies.

They report their audit observations to the President, Parliament and the public through the Annual Report of the Auditor-General management of the organisations audited through management letters.
Their observations include system weaknesses, non-compliance with control procedures or legislation, and instances of excess, extravagance, or gross inefficiency leading to waste in the use of public funds and resources.
'''

sys_prompt = '''
You are a specialist who uses the context provided to answer the query.
Your response should cite sources' year and page number.
If possible, make ministries or government agencies the headings.
'''

# functions 
def generate_yearly_data(years, metadata, chunks, yearly_data_path):
    ''' 
    This function fills the data base with chunks and metadata
   
    Input:
    -----------
        years: list (str)
            list of all years.

        metadata: list (dict)
            contains year, location in document and page number of chunk
        
        chunks: list (str)
            each element is text (str) of a chunk
        
        yearly_data_path: str
            yearly_data is a dict with keys (years), 
                                       values (chunks and metadata)

    Output:
    ----------
        None
            yearly_data is saved in yearly_data_path
        
    '''

    # initialise yearly data
    yearly_data = {}

    # iterate through all the years
    for year in years:

        # initialise yearly lists to add as values
        yearly_chunks, yearly_metadata = [], []

        # iterate through the whole database to cluster by years
        for idx, meta in enumerate(metadata):
            if meta["year"] == year:

                # add to yearly lists
                yearly_chunks.append(chunks[idx])
                yearly_metadata.append(meta)
        
        # add to yearly data for each year
        yearly_data[year] = {"chunks": yearly_chunks,
                            "metadata": yearly_metadata}
    
    # save data
    save_json(yearly_data, yearly_data_path)


def llama_get_agent(db, embed_model, description, openai_api_key):
    ''' 
    This function creates llm agents that take chunks and interprets them 
   
    Input:
    -----------
        db: chromadb.api.models.Collection
            vector database
        
        embed_model: llama_index.embeddings.openai.OpenAIEmbedding
            Embedding nodel used in llama index recursive retrieval
        
        description:
            text (part of metadata) that describes the query engine. 
            Unsure of this helps with retrieval but probably not useful.
            Reason being audit summary used later will later be used to 
            identify which node to retrieve. 
        
        openai_api_key: str
            OpenAI api key

    Output:
    ----------
        agent: llama_index.agent.openai.OpenAIAgent
            vector database
    '''


    # Initialize ChromaVectorStore with the collection
    vector_store = ChromaVectorStore(chroma_collection = db)

    # create llama index 
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=embed_model,
    )

    # create vector engine from index
    vector_query_engine = index.as_query_engine()

    # Create an engine tool that wraps query engine with metadat
    query_engine_tools = [
        QueryEngineTool(
            query_engine=vector_query_engine,
            metadata=ToolMetadata(
                name = "vector_tool",
                description = (
                    description
                ),
            ),
        )
    ]

    # llm for agents
    function_llm = llama_OpenAI(model = "gpt-4o", api_key = openai_api_key)

    # create agent with prompt
    agent = llama_OpenAIAgent.from_tools(
        query_engine_tools,
        llm=function_llm,
        verbose=True,
        system_prompt = sys_prompt
    )

    # return agent
    return agent


def llama_get_agent_manual(db, embed_model, description, openai_api_key):
    ''' 
    This function creates llm agents that take chunks and interprets them 
   
    Input:
    -----------
        db: chromadb.api.models.Collection
            vector database
        
        embed_model: llama_index.embeddings.openai.OpenAIEmbedding
            Embedding nodel used in llama index recursive retrieval
        
        description:
            text (part of metadata) that describes the query engine. 
            Unsure of this helps with retrieval but probably not useful.
            Reason being audit summary used later will later be used to 
            identify which node to retrieve. 
        
        openai_api_key: str
            OpenAI api key

    Output:
    ----------
        agent: llama_index.agent.openai.OpenAIAgent
            vector database
    '''

    count = db.count()

    chunks_all_data = db.get([f"id{i}" for i in range(count)], 
                             include = ["metadatas", "documents","embeddings"])
    
    chunks_text = chunks_all_data["documents"]
    chunks_ids = chunks_all_data["ids"]
    chunks_info = chunks_all_data["metadatas"]
    chunks_embeddings = chunks_all_data["embeddings"]

    nodes = [TextNode(text = chunks_text[i], 
                     id_ = chunks_ids[i], 
                     extra_info = chunks_info[i],
                     embedding = chunks_embeddings[i])
            for i in range(count)]

    # create llama index 
    index = VectorStoreIndex(nodes, embed_model=embed_model)

    # create vector engine from index
    vector_query_engine = index.as_query_engine()

    # Create an engine tool that wraps query engine with metadat
    query_engine_tools = [
        QueryEngineTool(
            query_engine=vector_query_engine,
            metadata=ToolMetadata(
                name = "vector_tool",
                description = (
                    description
                ),
            ),
        )
    ]

    # llm for agents
    function_llm = llama_OpenAI(model = "gpt-4o", api_key = openai_api_key)

    # create agent with prompt
    agent = llama_OpenAIAgent.from_tools(
        query_engine_tools,
        llm=function_llm,
        verbose=True,
        system_prompt = sys_prompt
    )

    # return agent
    return agent


def get_top_level_retriever(agents, years, embed_model):
    ''' 
    This function creates llm agents that take chunks and interprets them 
   
    Input:
    -----------
        agents: list (llama_index.agent.openai.OpenAIAgent)
            list of agents for each database. 
            there is 1 database for each node.
        
        years: list (str)
            document titles
        
        embed_model: llama_index.embeddings.openai.OpenAIEmbedding
            Embedding nodel used in llama index recursive retrieval

    Output:
    ----------
        top_query_engine: BaseQueryEngine
            top level query engine that searches through the tree.
    '''
    # define top-level nodes
    objects = []

    node = IndexNode(
            text = audit_summary_general, 
            index_id = "all years", 
            obj = agents["all years"]
        )
    objects.append(node)

    for year in years:
        # define index node that links to these agents
        
        node_yearly = IndexNode(
            text = audit_summary_yearly(year), 
            index_id = year, 
            obj = agents[year]
        )
        objects.append(node_yearly)
    
    # define top-level retriever
    top_vector_index = VectorStoreIndex(
        objects = objects,
        embed_model = embed_model
    )
    # top_query_engine = top_vector_index.as_query_engine(similarity_top_k=1, verbose=True)

    top_query_engine = top_vector_index.as_query_engine(verbose=True)

    return top_query_engine
