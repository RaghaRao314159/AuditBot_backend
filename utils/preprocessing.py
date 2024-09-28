import re
import fitz
import os
import time

from utils.json_parser import *

# PDF functions ==============================================================

# MAIN FUNCTION WRAPPER
def generate_chunks(DOCUMENT_DIR, 
                   chunks_path,
                   chunk_pageNum_pairs_path,
                   s_p_pairs_path,
                   chunking = 's', 
                   grouping = 1, 
                   min_chunk_size = 10,
                   doc_identifier = "ar_fy"):
    ''' 
    This function is a wrapper for the main chunking function. This function 
    saves the chunks created.
   
    Input:
    -----------
        DOCUMENT_DIR: str
            Path to document folder.

        chunks_path: str
            Path to save chunks.
        
        chunk_pageNum_pairs_path: str
            Path to save chunk and page number pairs.
        
        s_p_pairs_path: str
            Path to save sentence and paragraph pairs.

        chunking: str
            type of chunks, paragraphs = 'p' or sentences = 's'

        grouping: int
            chunks grouped together to make final chunk

        min_chunk_size: int
            min number of characters in each chunk

    Output:
    --------
        None
            function saves the following data:
            """
            all_chunks: list (str)
                each element is text (str) of a chunk
            saved at: chunks_path

            all_chunk_dict: dict
                chunk (str): page (int) pair
            saved at: chunk_pageNum_pairs_path
            
            all_s_p_pairs: dict
                sesentence: paragraph pair, used only when chunking == 's' and 
                grouping == 1
            saved at: s_p_pairs_path
            """
    '''
    # timed just for curious individuals
    start = time.time()

    # generate chunks
    all_chunks, all_chunk_dict, all_s_p_pairs = docs_to_chunks(DOCUMENT_DIR,
                                                               chunking,
                                                               grouping, 
                                                               min_chunk_size,
                                                               doc_identifier)

    # save chunks
    save_json({"chunks": all_chunks}, chunks_path)
    
    # save chunk : page number
    save_json(all_chunk_dict, chunk_pageNum_pairs_path)
    
    # save sentence : paragraph (not empty if chunking == 's')
    save_json(all_s_p_pairs, s_p_pairs_path)

    # display useful info for the curious
    end = time.time()
    print(end - start, "seconds")

    print("number of chunks:", len(all_chunks))


# MAIN FUNCTION used for preprocessing 
# Splits all PDF documents into chunks for RAG
def docs_to_chunks(DOCUMENT_DIR, 
                   chunking, 
                   grouping, 
                   min_chunk_size,
                   doc_identifier = "ar_fy"):
    ''' 
    This function is the MAIN FUNCTION used for preprocessing. It splits all 
    PDF documents into chunks for RAG
   
    Input:
    -----------
        DOCUMENT_DIR: str
            Path to document folder.

        chunking: str
            type of chunks, paragraphs = 'p' or sentences = 's'

        grouping: int
            chunks grouped together to make final chunk

        min_chunk_size: int
            min number of characters in each chunk
        
        doc_identifier: str
            label every file as 
            concatenate(name, document_identifier, year, .pdf).
            Ensure all documents used for RAG have the same doc_identifier.
            doc_identifier will help seperate wanted docs with unwanted docs.
            If doc does not have a single year, label it as "multiple years".

    Output:
    --------
        chunks: list (str)
            each element is text (str) of a chunk
        
        chunk_dict: dict
            chunk (str): page (int) pair

        sentence_paragraph_pairs: dict
            sesentence: paragraph pair, used only when chunking == 's' and 
            grouping == 1

    '''

    all_chunks = []
    all_chunk_dict = {}
    all_s_p_pairs = {}

    for root, dirs, files in os.walk(DOCUMENT_DIR):
        for file in files:
            # Get the full path of the file
            file_path = os.path.join(root, file)

            # documents directory contains content pages and audit reports
            # ignore content pages
            if file_path.find("content_pages") != -1:
                continue

            # Ignore non-audit reports
            idx = file_path.find(doc_identifier)
            if idx == -1:
                continue
            
            year = file_path[idx + len(doc_identifier):].split(".pdf")[0]

            
            chunks, chunk_dict, sentence_paragraph_pairs = pdf_to_chunks(
                file_path, 
                chunking,
                grouping, 
                min_chunk_size)
            
            all_chunks += chunks
            all_chunk_dict[year] = chunk_dict
            all_s_p_pairs.update(sentence_paragraph_pairs)
    
    return all_chunks, all_chunk_dict, all_s_p_pairs


# Splits single PDF document into chunks for RAG
def pdf_to_chunks(pdf_path, chunking, grouping, min_chunk_size):
    ''' 
    This function splits a single pdf document into chunks for RAG.
   
    Input:
    -----------
        pdf_path: str
            Path to document.

        chunking: str
            type of chunks 
            paragraphs = 'p'
            sentences = 's'
            fixed-size chunking = 'f'

        grouping: int
            chunks grouped together to make final chunk

        min_chunk_size: int
            min number of characters in each chunk

    Output:
    --------
        chunks: list (str)
            each element is text (str) of a chunk
        
        chunk_dict: dict
            chunk (str): page (int) pair

        sentence_paragraph_pairs: dict
            sesentence: paragraph pair, used only when chunking == 's' and 
            grouping == 1

    '''

    # convert pdf to pages
    pages = pdf_to_pages(pdf_path)

    # store paragraphs in a list
    paragraphs = []

    # store sentencess in a list
    sentences = []

    # store chunk : page in a dictionary
    chunk_dict = {}

    # store sentence : paragraph in a dictionary
    sentence_paragraph_pairs = {}

    current_page_number = 0

    # loop through pages to add paragraphs
    for idx, page in enumerate(pages):

        # ensure paragraphs are filtered (larger than min chunk size)
        per_page_paragraphs =  group(
            page_to_paragraphs(page, min_chunk_size), 
            grouping)    
        
        paragraphs += per_page_paragraphs

        page_number = page[:str(page).find('\n')]
        page_number_back = str(page)[-3:].strip('\n')

        if str(page_number).isdigit() and abs(idx - int(page_number)) < 15:
                current_page_number = page_number
                
        elif str(page_number_back).isdigit() and abs(idx - int(page_number_back)) < 15:
            current_page_number = page_number_back
        
        if chunking == 'p':
            # Paragraphs are the text chunks

            for paragraph in per_page_paragraphs:
                chunk_dict[paragraph] = int(current_page_number)
    
    
        # if chunking == s. then sentences are the text chunks
        else:
            per_page_sentences = []
            
            # loop through paragraphs to add sentences
            for paragraph in per_page_paragraphs:

                if chunking == 'f':
                    per_paragraph_sentences = group(
                    paragraph_to_fixedSizeChunks(paragraph, min_chunk_size),
                    grouping)

                else:
                    # ensure sentencess are filtered (larger than min chunk size)
                    per_paragraph_sentences = group(
                        paragraph_to_sentences(paragraph, min_chunk_size),
                        grouping)
                
                per_page_sentences += per_paragraph_sentences
                
                if (chunking == 's' or chunking == 'f') and grouping == 1:
                    for sentence in per_paragraph_sentences:
                        sentence_paragraph_pairs[sentence] = paragraph
            
            sentences += per_page_sentences

            for sentence in per_page_sentences:
                chunk_dict[sentence] = int(current_page_number)

    if chunking == 'p':
        chunks = paragraphs
    
    else:
        chunks = sentences

    return chunks, chunk_dict, sentence_paragraph_pairs

# Splits PDF documents into pages 
def pdf_to_pages(pdf_path):
    ''' 
    This function splits a single PDF documents into pages.
   
    Input:
    -----------
        pdf_path: str
            Path to document.

    Output:
    --------
        pages: list (str)
            each element is text (str) of a page
    '''
    # using fitz from PyMuPDF library (superior)

    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # store pages in a list
    pages = []

    # Iterate through each page
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num).get_text()
        pages.append(page)

    pdf_document.close()
    return pages


# Converts PDF documents into single string
def pdf_to_text(pdf_path):
    ''' 
    This function splits a single PDF document into a single string.
   
    Input:
    -----------
        pdf_path: str
            Path to document.

    Output:
    --------
        text: str
            whole pdf is a single string
    '''
    # using fitz from PyMuPDF library (superior)

    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # store pages in a list
    text = ""

    # Iterate through each page
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num).get_text()
        text += ("\n" + page)

    pdf_document.close()
    return text
            
# Text functions =============================================================

# Splits a page into paragraphs
def page_to_paragraphs(page, min_paragraph_length = 10):
    """
    @param page: str, text of a page
    @param min_paragraph_length: int, min number of chars in each paragraph

    @return paragraphs: list, each element is text (str) of a paragraph
    """

    # store paragraphs in a list
    paragraphs = []

    # use regular expression to split text with delimiters
    # ('.' or ':') + '\n'  is used as delimiter for paragraphs
    temp_paragraphs = re.split('\.\s*\n|:\n', page)

    # filter unwanted paragraphs
    for temp_paragraph in temp_paragraphs:

        # remove paragraphs that are bullet points (optional/unnecessary)
        paragraph = temp_paragraph.strip('•-\t')

        # remove paragraphs that are shorter than min_paragraph_length
        if len(paragraph) >= min_paragraph_length:
            paragraphs.append(paragraph)

    return paragraphs   

# Splits a paragraph into sentences
def paragraph_to_sentences(paragraph, min_sentence_length = 10):
    """
    @param paragraph: str, text of a paragraph
    @param min_sentence_length: int, min number of chars in each sentence

    @return sentences: list, each element is text (str) of a sentence
    """
    # store sentencess in a list
    sentences = []

    # use regular expression to split text with delimiters
    # '.' and ';' are used as delimiter for sentences
    temp_sentences = re.split('\.\s*|;\s*', paragraph)

    # filter unwanted sentences
    for temp_sentence in temp_sentences:

        # remove sentences that are just white spaces
        sentence = temp_sentence.strip()

        # remove sentences that are shorter than min_sentence_length

        if len(sentence) >= min_sentence_length:
            sentences.append(sentence)

    return sentences

# Splits a paragraph into sentences
def paragraph_to_fixedSizeChunks(paragraph, chunk_size):
    """
    @param paragraph: str, text of a paragraph
    @param min_sentence_length: int, min number of chars in each sentence

    @return sentences: list, each element is a sentence of chunk_size
    """
    # store sentencess in a list
    sentences = []

    i = 0


    while chunk_size * (i + 1) < len(paragraph):
        temp_sentence = paragraph[chunk_size * i: chunk_size * (i + 1)]

        # remove sentences that are just white spaces
        sentence = temp_sentence.strip()

        sentences.append(sentence)

        i += 1

    return sentences

# Groups smaller chunks into larger chunks
def group(text_array, grouping):
    """
    @param text_array: list, each element is text (str)
    @param grouping : int, elements grouped together to make new_array

    @return new_array: list, each element is text (str)
    """
    # e.g. with a grouping of 2, ['a','b','c','d','e'] ---> ['a b', 'c d', 'e']
    # gives additional control over size of chunks in RAG

    # if no grouping is done, return original array
    if grouping == 1:
        return text_array
    
    # new larger chunks are stored in a new list 
    new_array = []

    group = ""
    for i in range(len(text_array)):
        # seperate every chunk by a space (natural choice of delimiter)
        group += text_array[i] + " "

        # evenly split original array into groups of size grouping
        if i % grouping == grouping - 1 or i == len(text_array) - 1:

            # Additional filter on groups with white spaces
            group = group.strip()
            if len(group) != 0:
                new_array.append(group)

            # reset new group after being added to new_array
            group = ""
    
    return new_array

# Pairs text to page numbers written on the pdf 
# not every page is assigned a page number so this is necessary to match
# page number on content page with text
def get_true_pages(pages):
    ''' 
    This function Pairs text to page numbers written on the pdf. 
    Not every page is assigned a page number so this is necessary to 
    match the actual page number written on content page with text.
   
    Input:
    -----------
        pages: list (str)
            each element is text (str) of a page

    Output:
    --------
        true_pages: dict (int: str)
            page:text pairs where page numbers are the numbers written on the 
            pdf.
    '''

    # initialise true_pages as a dictionary with page number: text pairs
    true_pages = {}

    # loop though all pages (numbered and not numbered)
    for page in pages:

        # determine the pages that are numbered
        page_number = page[:str(page).find('\n')]
        if str(page_number).isdigit():
            true_pages[int(page_number)] = page
            
    return true_pages