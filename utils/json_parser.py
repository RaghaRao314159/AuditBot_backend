import json

# JSON functions =============================================================

# saves python dictionaries as JSON objects in JSON files
def save_json(object, filename):
    """
    @param object: dictionary
    @param filename: str

    @return: None
    """
    with open(filename, 'w') as fp:
        json.dump(object, fp)

# Converts JSON object stored in JSON file into a python dictionary
def json_file_to_dict(file_path):
    ''' 
    This function converts a json object to a python dictionary.
   
    Input:
    -----------
        file_path: str
            Path to a json file with a json object

    Output:
    --------
        dictionary
            python dictionary that contains the same information as json object

    '''
    try:
        # try open json file 
        with open(file_path, 'r') as file:

            # convert JSON object in file to python dictionary
            dictionary = json.load(file)

        return dictionary
    
    except (json.JSONDecodeError, FileNotFoundError) as e:

        # handle error if cannot open JSON file
        print("Error reading JSON file:", e)

        return None

# Converts JSON object stored in JSON file into a python dictionary
# converts integer keys (stored as strings in JSON) into python int 
def json_file_to_dict_with_int_keys(file_path):
    """
    @param file_path: str

    @return: object: dictionary
    """
    try:
        # try open json file 
        with open(file_path, 'r') as file:
            data = json.load(file)
            
            # Convert keys to integers
            int_key_dict = {int(key): value for key, value in data.items()}
            
        return int_key_dict
    
    except (json.JSONDecodeError, FileNotFoundError) as e:

        # handle error if cannot open JSON file
        print("Error reading JSON file:", e)

        return None
    
    except ValueError as e:

        # handle error if keys are not integers
        print("Error converting keys to integers:", e)

        return None