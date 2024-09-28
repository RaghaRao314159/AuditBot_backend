import json

# Custom printing functions ==================================================  

def pretty_print_dictionary(dictionary):
    """
    @param dictionary: nested dictionary

    @return: None
    """
    print(json.dumps(dictionary, indent=4))

def pretty_print_list(lis):
    ''' 
    This function prints a python list with index.
   
    Input:
    -----------
        lis: list
            python list to be printed

    Output:
    --------
        None
            function prints the data (python list)

    '''
    idx = 0

    for element in lis:
        print(f"idx: {idx}\n")
        print(element)
        print("\n----------------------------------------------------------\n")
        idx += 1

def pretty_print_rank(chunks, scores):
    ''' 
    This function prints a python list with index.
   
    Input:
    -----------
        chunks: list (str)
            each element is text (str) of a chunk
        
        scores: list (int)
            each element is the similarity score (with query) goven to a chunk

    Output:
    --------
        None
            function prints the chunks frombest to worst match with query
    '''
    rank = 1

    for chunk, score in zip(chunks, scores):
        print(f"RANK: {rank}\n")
        print(chunk)
        print("\nSCORE:", score)
        print("\n----------------------------------------------------------\n")
        rank += 1