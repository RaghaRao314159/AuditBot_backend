from pypdf import PdfReader
from preprocessing import *
from utils.content_page_parser import *

# Deprecated functions (due to better alternatives) ==========================
# The following functions are presented for documentation purposes

# using pypdf library (inferior)
def document_to_pages(document_path):
    reader = PdfReader(document_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        pages.append(text)

    return pages

# returns text chunks (misses out page numbers)
def pdf_to_chunks2(pdf_path, chunking = 's', grouping = 1, min_chunk_size = 1):
    """
    @param pdf_path: str, Path to document
    @param chunking: str, type of chunks, paragraphs = 'p' or sentences = 's'
    @param grouping : int, chunks grouped together to make final chunk
    @param min_chunk_size: int, min number of characters in each chunk

    @return chunks: list, each element is text (str) of a chunk
    """
    # convert pdf to pages
    pages = pdf_to_pages(pdf_path)

    # store paragraphs in a list
    paragraphs = []

    # loop through pages to add paragraphs
    for page in pages:

        # ensure paragraphs are filtered (larger than min chunk size)
        paragraphs =  group(
            page_to_paragraphs(page, min_chunk_size), 
            grouping)    

    # if chunking == p. then paragraphs are the text chunks
    chunks = paragraphs
    
    # if chunking == s. then sentences are the text chunks
    if chunking == 's':
        # store sentencess in a list
        sentences = []

        # loop through paragraphs to add sentences
        for paragraph in paragraphs:

            # ensure sentencess are filtered (larger than min chunk size)
            sentences += group(
                paragraph_to_sentences(paragraph, min_chunk_size),
                grouping)

        chunks = sentences

    return chunks

# returns nested text chunks (incorrect format for data base)
def pdf_to_chunks3(pdf_path, chunking = 's', grouping = 1):
    pages = pdf_to_pages(pdf_path)
    paragraphs = [group(page_to_paragraphs(page), grouping) for page in pages]
    chunks = paragraphs
    
    if chunking == 's':
        sentences = [
                [group(paragraph_to_sentences(paragraph), grouping) 
                for paragraph in page] 
            for page in pages]
        chunks = sentences

    return chunks

# langchain text splitter is not satisfactory
from langchain_text_splitters import RecursiveCharacterTextSplitter 
def langchain_pdf_to_chunks(DOCUMENT_PATH):
    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        separators=[
            "\n",
        ],
        chunk_size=100,
        chunk_overlap=0,
        length_function=len,
    )

    pages = pdf_to_pages(DOCUMENT_PATH)
    texts = text_splitter.create_documents(pages[14])

    print(texts)

# ONLY FOR ONE DOC
# This function produces the final data structure where chunks are keys and 
# values are metadata (headings / ministries / etc.)
def get_complete_inverted_tree2(chunk_pageNum_pairs, partial_inverted_tree):
    """
    @param partial_inverted_tree: dictionary, page number: path to reach page
    @param chunk_pageNum_pairs : list, chunk (str): page (int) pair
    @param tree: dictionary, page number: path to reach page
    
    @return complete_inverted_tree : dictionary, chunk: path to reach chunk 
    """
    # initialise final tree
    complete_inverted_tree = {}

    # iterate through chunks
    for chunk in chunk_pageNum_pairs:

        # page number where each chunk is located is obtained
        page = chunk_pageNum_pairs[chunk]

        # this page number is used to retrieve further metadata
        metadata =  partial_inverted_tree[page] + [{"page": page}]
        complete_inverted_tree[chunk] = metadata

    return complete_inverted_tree

# ONLY FOR ONE DOC
def get_inverted_tree2(chunk_pageNum_pairs, tree):
    """
    @param partial_inverted_tree: dictionary, page number: path to reach page
    @param chunk_pageNum_pairs : list, chunk (str): page (int) pair
    @param tree: dictionary, page number: path to reach page
    
    @return complete_inverted_tree : dictionary, chunk: path to reach chunk 
    """
    # initialise intermediate tree
    partial_inverted_tree = {}
    get_partial_inverted_tree(tree, [], partial_inverted_tree )


    complete_inverted_tree = get_complete_inverted_tree(chunk_pageNum_pairs, 
                                                        partial_inverted_tree) 

    return complete_inverted_tree