from openai import OpenAI
from IPython.display import display_markdown

# AGO
ROLE_AGO = '''Role:
You are a specialist who uses the context provided to answer the query.\n
'''

INSTRUCTIONS_AGO = '''Instruction:
Your response should cite sources' year and page number.
If possible, make ministries or government agencies the headings.
If you are unable to provide an answer, state "Unable to find, submit prompt again."\n
'''

BACKGROUND_AGO = '''Background:
The context is taken from audit reports from the Auditor-General's Office (AGO) of Singapore. 
AGO is an independent organ of state and the national auditor. They play an important role in enhancing public accountability in the management and use of public funds and resources through their audits.

They audit
    government ministries and departments
    organs of state
    statutory boards
    government funds
    other public authorities and bodies administering public funds (upon their request for audit), e.g. government-owned companies.

They report their audit observations to the President, Parliament and the public through the Annual Report of the Auditor-General management of the organisations audited through management letters.
Their observations include system weaknesses, non-compliance with control procedures or legislation, and instances of excess, extravagance, or gross inefficiency leading to waste in the use of public funds and resources.\n
'''

# National Day Rally
ROLE_NDR = '''Role:
You are a journalist in charge of the Singapore National Day Rally (NDR).
You have to use context from the NDR transcription to answer the query.\n
'''

INSTRUCTIONS_NDR = '''Instruction:
Your response should cite the source's year. Don't cite the context number.
Categorise your answers and provide headings. 
If you are unable to provide an answer, state "Unable to find, submit prompt again."\n
'''

BACKGROUND_NDR = '''Background:
The contexts are taken from a speech given by Singapore Prime Minister during the National Day Rally (NDR). 
NDR is an annual event where the Prime Minister addresses the nation on key issues and policies, and update Singaporeans on the country’s progress.\n
'''


document_options = {
    "AGO": {
        "role": ROLE_AGO,
        "instructions": INSTRUCTIONS_AGO,
        "background": BACKGROUND_AGO
    },              
    "NDR": {
        "role": ROLE_NDR,
        "instructions": INSTRUCTIONS_NDR,
        "background": BACKGROUND_NDR
    }
}


def openai_completion_to_text(completion):
    ''' 
    This function takes openai api output and converts to text.
   
    Input:
    -----------
        completion: class:`openai.types.chat.Completions`
            api output by openai

    Output:
    --------
        api_output: str
            parsed output.
    '''
    try:
        api_output = completion.choices[0].message.content
    except:
        api_output = completion.content

    return api_output


def generate_prompt(query,
                    inverted_tree, 
                    best_chunks, 
                    chunking, 
                    sentence_paragraph_pairs = {},
                    document = "AGO"):
    ''' 
    This function does prompt engineering to generate a prompt for LLM.
   
    Input:
    -----------
        query: str
            question by user

        inverted_tree: dictionary
            chunks (str) : meta data formed from content page

        best_chunks: list (str)
            chunks (str) that are top matches with query

        chunking: str
            type of chunks, paragraphs = 'p' or sentences = 's'
        
        sentence_paragraph_pairs: dictionary
            sentences (str) : paragraphs (str) the sentences are from
        
        document: str
            choose 1 one ["AGO", "NDR"]

    Output:
    --------
        prompt: str
            prompt for LLM.

    '''
    # Prompt engineering guidelines follow spiceworks
    # https://www.spiceworks.com/tech/artificial-intelligence/articles/what-is-prompt-engineering/

    # A role denotes the position where the prompt assumes an individual, 
    # which helps the AI create a response relevant to that persona.
    role = document_options[document]["role"]

    # instructions
    instuctions = document_options[document]["instructions"]

    # contextual information
    background = document_options[document]["background"]

    # Adding further contextual information
    context = "CONTEXT\n"

    # iterate through chunks found from RAG
    for i, chunk in enumerate(best_chunks):

        # if chunks are sentences
        if chunking == 's':

            # retrieve paragraphs where sentences originated from
            # this provides more contexual information
            paragraph = sentence_paragraph_pairs[chunk]
        
        # if chunks are already paragraphs, then do nothing
        else:
            paragraph = chunk
        
        # retrieve metadata from data store: year, section of doc, page
        metadata = inverted_tree[chunk]
        
        # year of audit report
        # year = metadata[0]["year"]
        year = metadata["year"]

        # some text are assigned page numbers
        if metadata.get("page", -1) != -1 :
            page = metadata["page"]
        
        # some text appear before 1st page (hence not assigned page numbers)
        else:
            page = "Before first page"
        
        # location refers to the chapter/heading the chunk is under
        # this is extracted from the content pages of the docs.
        # assign location seperately because some docs do not have content page
        location = metadata.get("location", -1)

        # if location exists
        if location != -1:
            location = ', '.join(metadata["location"])

            # Stitch all contexts together into one string
            context += f"Context {i}:\nYear: {year}\nLocation in document: {location}\nPage number: {page}\nContent: {paragraph}\n\n"
        
        else:
            context += f"Context {i}:\nYear: {year}\nPage number: {page}\nContent: {paragraph}\n\n"


    # stitch prompt together  
    prompt = role + instuctions + background + context + f"Query: {query}"

    return prompt

def generate_bad_prompt(
        query,
        best_chunks, 
        chunking, 
        sentence_paragraph_pairs = {}
    ):
    ''' 
    This function generates a bad prompt for LLM.
   
    Input:
    -----------
        query: str
            question by user

        inverted_tree: dictionary
            chunks (str) : meta data formed from content page

        best_chunks: list (str)
            chunks (str) that are top matches with query

        chunking: str
            type of chunks, paragraphs = 'p' or sentences = 's'
        
        sentence_paragraph_pairs: dictionary
            sentences (str) : paragraphs (str) the sentences are from
        
        document: str
            choose 1 one ["AGO", "NDR"]

    Output:
    --------
        prompt: str
            prompt for LLM.

    '''

    # Adding further contextual information
    context = ""

    # iterate through chunks found from RAG
    for chunk in best_chunks:

        # if chunks are sentences
        if chunking == 's':

            # retrieve paragraphs where sentences originated from
            # this provides more contexual information
            paragraph = sentence_paragraph_pairs[chunk]
        
        # if chunks are already paragraphs, then do nothing
        else:
            paragraph = chunk
        
        # Stitch all contexts together into one string
        context += f"{paragraph}\n\n"

    # stitch prompt together  
    prompt = context + f"Query: {query}"

    return prompt


def hyde(query):
    prompt = f"""Please write a passage to answer the question below.
    Question: {query}
    """
    return prompt