# Content page parser / tree generation functions ============================

# The initial tree's leaves are a list of pages belonging to a section
# This function assigns text to each page in this tree
from utils.json_parser import *
import sys
import os


def add_text_to_tree(tree, true_pages):
    """
    @param tree: dictionary, hirarchy built using content page
    @param true_pages : dictionary, page:text pairs where page numbers are the 
                                    numbers written on the pdf

    @return None (tree is passed by reference so it is updated in function)
    """
    
    # this function is recurise to iterate through the nested tree depth first
    for child in tree:

        # Tree's Leaves are a list of pages so check if leaves are rechead
        if type(tree[child]) == list:

            # initialise dictionary to assign page_number: text pairs
            dic = {}

            for page_number in tree[child]:
                
                # fill dictionary with text
                dic[page_number] = true_pages[page_number]

            # update tree leaves with this dictionary, completing the tree
            tree[child] = dic
        
        # if not a leaf, enter the child node (recursion)
        else:
            add_text_to_tree(tree[child], true_pages)

# this function performs a partial flip of a tree
def get_partial_inverted_tree(tree, route, inverted_tree):
    """
    @param tree: dictionary, hirarchy built using content page
    @param route: list, path travered in the tree during recursion
    @param inverted_tree: dictionary, page number: path to reach page
    
    @return None (inverted_tree is passed by reference so it is updated)
    """
    # this function is recurise to iterate through the nested tree depth first
    for child in tree:

        # Tree's Leaves are a list of pages so check if leaves are rechead
        if type(tree[child]) == list:

            # initialise dictionary to assign page_number: text pairs
            
            new_route = route.copy()
            new_route += [child]

            for page_number in tree[child]:
                inverted_tree[page_number] = new_route
        
        # if not a leaf, enter the child node (recursion)
        else:
            new_route = route.copy()
            new_route += [child]
            get_partial_inverted_tree(tree[child], new_route, inverted_tree)


# This function produces the final data structure where chunks are keys and 
# values are metadata (headings / ministries / etc.)
def get_complete_inverted_tree(chunk_pageNum_pairs, partial_inverted_tree):
    """
    @param chunk_pageNum_pairs : list, chunk (str): page (int) pair
    @param partial_inverted_tree: dictionary, page number: path to reach page
    
    @return complete_inverted_tree : dictionary, chunk: path to reach chunk 
    """
    # initialise final tree
    complete_inverted_tree = {}

    #iterate through years
    for year in chunk_pageNum_pairs:

        # iterate through chunks
        for chunk in chunk_pageNum_pairs[year]:

            # page number where each chunk is located is obtained
            page = chunk_pageNum_pairs[year][chunk]

            # this page number is used to retrieve further metadata
            context = partial_inverted_tree[year].get(page, -1)

            # if page number doesn't exist, then chunk is part of the intro
            if context == -1:
                # metadata = [{"year": year}] + ["Introduction"]
                metadata = {"year": year, "location": ["Introduction"]}

            # else, add page number and context (like sub/headings) to metadata
            else:
                # metadata = [{"year": year}] + context + [{"page": page}]
                metadata = {"year": year, "location": context, "page": page}

            complete_inverted_tree[chunk] = metadata

    return complete_inverted_tree

# MAIN FUNCTION
# This function neatly combines partial and complete tree inversion into 1
def get_inverted_tree(chunk_pageNum_pairs, tree):
    """
    @param chunk_pageNum_pairs : list, chunk (str): page (int) pair
    @param tree: dictionary, page number: path to reach page
    
    @return complete_inverted_tree : dictionary, chunk: path to reach chunk 
    """
    # initialise intermediate tree
    partial_inverted_tree = {}

    # initialise final tree
    inverted_tree = {}

    # loop through all years
    for year in chunk_pageNum_pairs:

        # temporary tree for every year
        p_i_tree_year = {}
        get_partial_inverted_tree(tree[year], [], p_i_tree_year)

        # create partially inverted tree (does not include chunks)
        partial_inverted_tree[year] = p_i_tree_year
    
    # create fully inverted tree (includes chunks)
    inverted_tree = get_complete_inverted_tree(chunk_pageNum_pairs, 
                                               partial_inverted_tree)

    return inverted_tree


# MAIN FUNCTION WRAPPER
# This function generates and saves inverted tree
def generate_inverted_tree(chunk_pageNum_pairs_path,
                           has_content_page, 
                           save_inverted_tree_path,
                           tree_path = None):
    ''' 
    This function splits a single pdf document into chunks for RAG.
   
    Input:
    -----------
        chunk_pageNum_pairs_path: str
            Path to chunk and page number pairs.

        has_content_page: bool
            do documents have content pages that provide metadata?

        save_inverted_tree_path: str
            Path to save inverted tree.
        
        tree_path: str
            Path to (content page) tree.

    Output:
    --------
        None
            function saves the data (inverted tree)

    '''

    # get path to chunk : page pair dictionary
    chunk_pageNum_pairs = json_file_to_dict(chunk_pageNum_pairs_path)
    
    if has_content_page:
        # get tree (made from content page)
        tree = json_file_to_dict(tree_path)

        # invert the tree to get keys as chunks
        inverted_tree = get_inverted_tree(chunk_pageNum_pairs, tree) 

    else:
        # inverted tree is just chunk_pageNum_pairs dict but chunks as keys.
        inverted_tree = {}
        for year in chunk_pageNum_pairs:
            for chunk, page in chunk_pageNum_pairs[year].items():
                inverted_tree[chunk] = {
                    "year": year, 
                    "page": page if page != 0 else "Introduction"}

    # save inverted tree
    save_json(inverted_tree, save_inverted_tree_path)


# MAIN FUNCTION WRAPPER
# This function generates and saves inverted tree
def generate_inverted_tree_og(chunk_pageNum_pairs_path,
                            tree_path,
                            save_inverted_tree_path):
    ''' 
    This function splits a single pdf document into chunks for RAG.
   
    Input:
    -----------
        chunk_pageNum_pairs_path: str
            Path to chunk and page number pairs.

        tree_path: str
            Path to (content page) tree.

        save_inverted_tree_path: str
            Path to save inverted tree.

    Output:
    --------
        None
            function saves the data (inverted tree)

    '''

    # get path to chunk : page pair dictionary
    chunk_pageNum_pairs = json_file_to_dict(chunk_pageNum_pairs_path)
    
    # get tree (made from content page)
    tree = json_file_to_dict(tree_path)

    # invert the tree to get keys as chunks
    inverted_tree = get_inverted_tree(chunk_pageNum_pairs, tree) 

    # save inverted tree
    save_json(inverted_tree, save_inverted_tree_path)